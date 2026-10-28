"""Register allocation as graph coloring. No generated code is executed."""
import random
import uuid
from typing import Literal
from pydantic import Field, StrictInt
from openenv.core.env_server import Action, Observation, State, Environment

class RegisterAction(Action):
    operation: Literal['check', 'submit', 'finish'] = 'submit'
    allocation: list[StrictInt] = Field(default_factory=list, max_length=32)

class RegisterObservation(Observation):
    task_id: str = ''
    instruction: str = ''
    variables: list[str] = Field(default_factory=list)
    interference: list[list[int]] = Field(default_factory=list)
    feedback: str = ''
    steps_remaining: int = 12

FAMILIES = ('path', 'cycle', 'clique', 'bipartite', 'wheel', 'crown')
TASKS = [f'{f}-{n}' for f in FAMILIES for n in (8, 12)]

def make_graph(task_id, seed):
    family, size = task_id.rsplit('-', 1)
    n = int(size)
    edges = set()
    def edge(a,b):
        edges.add(tuple(sorted((a,b))))
    if family in ('path','cycle','wheel'):
        limit = n-1 if family == 'wheel' else n
        for i in range(limit-1): edge(i,i+1)
        if family != 'path': edge(limit-1,0)
        if family == 'wheel':
            for i in range(limit): edge(i,n-1)
        optimum = 2 if family != 'wheel' else 4
    elif family == 'clique':
        # Four mutually interfering variables, with attached independent leaves.
        for a in range(4):
            for b in range(a+1,4): edge(a,b)
        for a in range(4,n): edge(a,a%4)
        optimum=4
    elif family in ('bipartite','crown'):
        for a in range(n//2):
            for b in range(n//2,n):
                if family != 'crown' or a != b-n//2: edge(a,b)
        optimum=2
    else: raise ValueError('Unknown task')
    permutation=list(range(n)); random.Random(seed).shuffle(permutation)
    return n, sorted([sorted((permutation[a],permutation[b])) for a,b in edges]), optimum

class RegisterEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True
    def __init__(self):
        super().__init__()
        self._state=State()
        self.last=None
        self.reset()
    @property
    def state(self): return self._state
    def reset(self, seed=None, episode_id=None, task_id=None, **kwargs):
        task_id = task_id or TASKS[0]
        if task_id not in TASKS: raise ValueError('Unknown task_id')
        self.task_id=task_id
        self.n,self.edges,self.optimum=make_graph(task_id, seed if seed is not None else random.SystemRandom().randrange(2**32))
        self._state=State(episode_id=episode_id or str(uuid.uuid4()),step_count=0)
        self.last=RegisterObservation(task_id=task_id, instruction=(
            'Allocate registers to variables v0..vN-1. Each edge [i,j] means vi and vj must use different registers. '
            'Send allocation as N integer register IDs in 0..N-1, in variable order. Minimize distinct registers. '
            'Use operation=check for conflict feedback or submit to finish. Invalid allocations earn 0; '
            'valid allocations earn chromatic optimum / number of registers used. At most 12 actions. '
            'Example shape: {"operation":"submit","allocation":[0,1,0]}. '
            'operation=finish ends with 0. All constraints are visible.'),
            variables=[f'v{i}' for i in range(self.n)],interference=self.edges,reward=0.0)
        return self.last
    def step(self, action, timeout_s=None, **kwargs):
        if self.last.done: return self.last.model_copy(deep=True)
        self._state.step_count+=1
        allocation=action.allocation
        valid = len(allocation)==self.n and all(0<=v<self.n for v in allocation)
        conflicts=[]
        if valid:
            conflicts=[(a,b) for a,b in self.edges if allocation[a]==allocation[b]]
            valid=not conflicts
        used=len(set(allocation)) if allocation else 0
        score=self.optimum/used if valid else 0.0
        done=action.operation in ('submit','finish') or self.state.step_count>=12
        reward=score if done and action.operation!='finish' else 0.0
        feedback=(f'Valid; {used} registers.' if valid else
                  f'Invalid. Supply exactly {self.n} IDs in 0..{self.n-1}. Conflicts: {conflicts[:8]}.')
        self.last=RegisterObservation(task_id=self.task_id,feedback=feedback,
            reward=reward,done=done,steps_remaining=max(0,12-self.state.step_count))
        return self.last
