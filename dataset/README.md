---
license: mit
pretty_name: Compiler Register Lab
tags:
- rl-environment
- openenv
- compilers
---
# Compiler Register Lab

A CPU-only OpenEnv environment teaching compiler register allocation through interference-graph coloring. Twelve tasks cover paths, even cycles, four-cliques with leaves, complete bipartite graphs, odd-rim wheels and crown graphs at 8 and 12 variables. Each reset randomly relabels vertices; an explicit seed reproduces an episode.

The agent sees every interference edge and assigns integer register IDs. The check action returns conflict feedback; submit ends the episode. A valid allocation earns the known chromatic optimum divided by the number of distinct registers used. Malformed or conflicting allocations earn zero. Intermediate checks earn zero. The twelfth action always ends the episode. The finish action terminates with zero.

This is an abstract compiler optimization task, not a full compiler or GPU kernel runtime. No generated code is executed. No runtime internet, secrets, task downloads or GPU are required. OpenEnv is pinned to 86a180ede21e044f7929b9a7783ad83aa67d83a3.

Validation: 56 independent unit tests and 48 native WebSocket episode controls covering optimal, conflicting, inefficient and admission-example allocations. Independent exact-coloring search verifies all reference optima across four seeds. No model calibration, learning improvement or private-task transfer is claimed.

Public source and reproducible generator: https://github.com/shashank-100/openenv-register-lab/tree/37b4654

Source archive: https://github.com/shashank-100/openenv-register-lab/blob/37b4654/dataset/source.tar.gz

Public image: ghcr.io/shashank-100/openenv-register-lab@sha256:4622f803b69fb85df2f1f22c8d155aa774b6236b0ce0f2f84d27c1a64b52e612

Anonymous image qualification: https://github.com/shashank-100/openenv-register-lab/actions/runs/40632572251

Review-only submission request: https://github.com/shashank-100/openenv-register-lab/blob/37b4654/submission.json

The universal admission example is {"operation":"finish","allocation":[]}, earning terminal reward zero. It checks the contract only; reference solutions are verified separately. Submission requires explicit human approval.
