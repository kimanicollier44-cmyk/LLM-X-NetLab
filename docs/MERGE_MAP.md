# Merge map — where every source landed

## Source 1: the LLM-x Architecture Diagram (poster)

| Poster block | Module |
|---|---|
| User Interface Layer (web / mobile / API clients) | `main.py` CLI (the client seat) |
| Agentic Orchestrator & Planner (task decomposition, tool use, multi-agent coordination) | `llmx_netlab/orchestrator.py` |
| Multi-Modal Gateway & Input Processing (tokenizer, embedding models, media encoders) | `llmx_netlab/gateway.py`, `llmx_netlab/embeddings.py` |
| LLM Core Backbone (pre-training, SFT, RLHF) | `llmx_netlab/backbone.py` (staged contract + tiny bigram SLM) |
| RAG System (vector database, external KBs, knowledge graph) | `llmx_netlab/rag.py` |
| Memory Systems (session short-term, episodic long-term) | `llmx_netlab/memory.py` |
| Domain-Specific Modules 'X' (code interpreter, data analysis, math solver, external APIs) | `llmx_netlab/domain.py` |
| MLOps & Continuous Learning (deployment, evaluation, online learning) | `llmx_netlab/mlops.py` |
| Guardrails & Monitoring (safety filter, PII redaction, latency) | `llmx_netlab/guardrails.py` |

## Source 2: the Computer Networking notes (7 handwritten pages)

All 28 numbered topics became KB entries in `llmx_netlab/kb.py` (what networking
is; PAN/LAN/MAN/WAN; wired/wireless/VPN; devices + functions + examples;
topologies; IP addressing, classes, private ranges; protocols; OSI + TCP/IP
models; routing vs switching; cables/connectors; firewall types; security
types; bandwidth; commands; internet services; data-flow example) and the
working engines in `llmx_netlab/netlab.py` (subnet calculator, topology
simulator, layer mapper, device advisor, ping simulator).

## Source 3: Darion's additions (2026-11-08)

| Addition | Module |
|---|---|
| IP address hopper / tracker / mapper — track start point, middle point, ending point | `llmx_netlab/iphop.py` |
| Google Earth | `llmx_netlab/earth.py` (KML export seat, names-only, no geolocation) |
| Google Flow | `llmx_netlab/flowvideo.py` (video planning seat, render HOLD) |
| Gemini Carbon 4 Extended Thinking | `llmx_netlab/brains/carbon4.py` (DECIDER, tiers 2048/8192/32768) |
| Muse advisor (his standing council pattern) | `llmx_netlab/brains/muse.py` + `council.py` |
