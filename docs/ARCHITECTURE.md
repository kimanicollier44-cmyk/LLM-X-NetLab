# LLM-X-NetLab — Architecture

Three layers, mirroring the LLM-x poster:

**User layer** — `main.py` is the one client interface (demo, ask, subnet,
topology, layer, device, quiz, track, track-topo, earth, flow, bench, stages,
checks, hold-demo).

**Core system & orchestration** — the orchestrator decomposes each request and
routes it to a sub-agent: retriever (TF-IDF RAG over the networking KB +
knowledge graph), subnet agent, topology agent, layer agent, device agent,
tracker agent (IP hopper/tracker/mapper), with the domain X modules (safe code
interpreter, data analysis, math solver, external API contracts) on call. The
backbone seat is a staged training contract (pre-training -> SFT -> RLHF) with
a tiny bigram SLM trained on the KB as the runnable model. Memory: session
(short-term) + episodic (long-term, explicit-path only).

**Support & safety** — the brains council reviews every orchestrated answer: Gemini Carbon 4 Extended Thinking decides (MAP -> MODEL -> STRESS -> DECIDE, tiers 2048/8192/32768), Muse advises (authority: none). **v1.1.0: the HOLD gate system was removed at Darion's direction; the lab is online (`llmx_netlab/live.py`: DNS, TCP connect, port scan, ping, TTL traceroute, HTTP probe, geo lookup).** Guardrails keep the content safety filter, PII redaction and latency monitoring; MLOps adds the benchmark harness and feedback log. Guardrails add a content safety
filter, PII redaction and latency monitoring; MLOps adds the benchmark
harness and the feedback log.

**Data flow (ask):** question -> safety filter -> route -> tool/RAG evidence ->
council review -> grounded answer with sources -> session memory.

**Invariants:** offline only (no sockets anywhere); samples/data are supplied
or simulated; every tracking view is start/middle/end over supplied or
simulated paths; KML export never invents coordinates.
