---
license: mit
pretty_name: Compiler Register Lab
---
# Compiler Register Lab

An OpenEnv environment teaching compiler register allocation through interference-graph coloring. Twelve tasks cover paths, even cycles, four-cliques with leaves, complete bipartite graphs, odd-rim wheels, and crown graphs at 8 and 12 variables. Each reset randomly relabels vertices; explicit seeds reproduce an episode.

The agent sees every edge and assigns integer register IDs. `check` returns bounded conflict feedback. `submit` ends the episode; `finish` ends with zero. The 12th action always ends the episode. A valid allocation earns the known chromatic number divided by the number of distinct registers used; malformed or conflicting allocations earn zero. Intermediate checks earn zero. Reference optima follow from each graph construction and are independently tested with exact coloring. No model calibration, learning or private-task improvement is claimed.

This is an abstract compiler optimization environment, not a full compiler or GPU kernel runtime. No generated code is executed. All state is session-local. Tasks require no internet, secrets, downloads or GPU at runtime. OpenEnv is pinned to `86a180ede21e044f7929b9a7783ad83aa67d83a3`.

Run: `uvicorn server.app:app --host 0.0.0.0 --port 8000`.
Validate: `openenv validate --url http://localhost:8000`.
Tests: `python -m pytest -q`.

The universal admission example is `{"operation":"finish","allocation":[]}`: terminal reward zero, used solely to verify the episode contract. It is not a solver or an indication of task performance. Independent reference solutions are tested separately.
