"""Replay every task over the native OpenEnv WebSocket protocol."""
import asyncio
import json
import sys
import websockets
from test_environment import exact_color
from server.environment import TASKS

async def replay(base):
    controls=0
    for task in TASKS:
        for mode in ('reference','conflict','partial','example'):
            async with websockets.connect(base.replace('http','ws',1)+'/ws') as ws:
                async def exchange(kind,data):
                    await ws.send(json.dumps({'type':kind,'data':data}))
                    response=json.loads(await ws.recv())
                    assert response['type']=='observation', response
                    return response['data']
                initial=await exchange('reset',{'task_id':task,'seed':42})
                observation=initial['observation']
                assert observation['task_id']==task
                n=len(observation['variables'])
                edges=observation['interference']
                allocation=None
                for k in range(1,n+1):
                    allocation=exact_color(n,edges,k)
                    if allocation is not None: break
                optimum=k
                if mode=='reference': action={'operation':'submit','allocation':allocation}; expected=1
                elif mode=='conflict': action={'operation':'submit','allocation':[0]*n}; expected=0
                elif mode=='partial': action={'operation':'submit','allocation':list(range(n))}; expected=optimum/n
                else: action={'operation':'finish','allocation':[]}; expected=0
                result=await exchange('step',action)
                assert result['done'] and abs(result['reward']-expected)<1e-9, (task,mode,result)
                controls+=1
    print(json.dumps({'native_episode_controls':controls,'tasks':len(TASKS),'result':'PASS'}))

asyncio.run(replay(sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8000'))
