import pytest
from pydantic import ValidationError
from server.environment import RegisterEnvironment, RegisterAction, TASKS, make_graph

def exact_color(n, edges, k):
    adjacency=[set() for _ in range(n)]
    for a,b in edges: adjacency[a].add(b); adjacency[b].add(a)
    colors=[-1]*n
    def search():
        uncolored=[v for v in range(n) if colors[v]<0]
        if not uncolored: return colors.copy()
        v=max(uncolored,key=lambda v:(len({colors[w] for w in adjacency[v] if colors[w]>=0}),len(adjacency[v])))
        forbidden={colors[w] for w in adjacency[v]}
        for c in range(min(k,max(colors)+2)):
            if c in forbidden: continue
            colors[v]=c
            result=search()
            if result is not None: return result
            colors[v]=-1
        return None
    return search()

@pytest.mark.parametrize('task',TASKS)
@pytest.mark.parametrize('seed',[0,1,42,2026])
def test_optimum_and_rewards(task,seed):
    env=RegisterEnvironment(); initial=env.reset(task_id=task,seed=seed)
    n,edges,optimum=make_graph(task,seed)
    assert initial.interference==edges and len(initial.variables)==n
    assert exact_color(n,edges,optimum-1) is None
    allocation=exact_color(n,edges,optimum)
    checked=env.step(RegisterAction(operation='check',allocation=allocation))
    assert not checked.done and checked.reward==0
    result=env.step(RegisterAction(allocation=allocation))
    assert result.done and result.reward==1
    assert env.step(RegisterAction(operation='finish')).reward==1
    env.reset(task_id=task,seed=seed)
    invalid=env.step(RegisterAction(allocation=[0]*n))
    assert invalid.done and invalid.reward==0
    env.reset(task_id=task,seed=seed)
    partial=env.step(RegisterAction(allocation=list(range(n))))
    assert partial.done and partial.reward==pytest.approx(optimum/n)

@pytest.mark.parametrize('allocation',[[],[0],[-1]*8,[8]*8])
def test_malformed_zero(allocation):
    env=RegisterEnvironment()
    assert env.step(RegisterAction(allocation=allocation)).reward==0

@pytest.mark.parametrize('allocation',[[True]*8,[1.0]*8,['1']*8])
def test_strict_integers(allocation):
    with pytest.raises(ValidationError): RegisterAction(allocation=allocation)

def test_budget_finish_reset_and_sessions():
    a=RegisterEnvironment();b=RegisterEnvironment()
    first=a.reset(task_id=TASKS[-1],seed=42)
    assert first.model_dump()==a.reset(task_id=TASKS[-1],seed=42).model_dump()
    for i in range(12):
        result=a.step(RegisterAction(operation='check'))
        assert result.done==(i==11)
    assert b.state.step_count==0
    assert a.reset().steps_remaining==12
    assert a.step(RegisterAction(operation='finish')).done
    for task in TASKS:
        a.reset(task_id=task)
        result=a.step(RegisterAction(operation='finish',allocation=[]))
        assert result.done and result.reward==0
    with pytest.raises(ValueError): a.reset(task_id='invalid')
