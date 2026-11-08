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

**Invariants:** samples/data are supplied or simulated except the v1.1.0
live seat (`llmx_netlab/live.py`), which opens real sockets only against a
named host; every tracking view is start/middle/end; KML export never
invents coordinates.

## Raw sockets & host requirements

Real ICMP (ping / TTL traceroute) needs `CAP_NET_RAW`, and that permission
is granted by the **host at launch time** — it cannot be created from
inside a running VM or container.

Verified 2026-11-08 in the build sandbox (Darion asked for the permission
to be created; every in-VM route was tried):

- The host runtime drops `CAP_NET_RAW` (also `CAP_NET_ADMIN`,
  `CAP_SYS_PTRACE`) from the capability bounding set
  (CapBnd `000001fffff7cfff`), seccomp filtering is on, `NoNewPrivs=1`,
  and `/proc/sys` is mounted read-only with
  `net.ipv4.ping_group_range = 65534 65534`.
- `sysctl -w` → permission denied, value unchanged. `setcap
  cap_net_raw+ep` on the ping / python3 binaries → exec fails with
  "Operation not permitted" (setcaps removed after the test). `capsh`
  raise → "Unable to set capabilities". Raw ICMP socket → `EPERM`;
  ping (DGRAM) socket → `EACCES`.
- Fix, host-side only: launch with the capability in the bounding set
  (e.g. `docker run --cap-add=NET_RAW ...`), a seccomp profile that
  allows the socket syscalls, and a `ping_group_range` that includes the
  caller's group (e.g. `0 2147483647`).
- In that sandbox, egress also passes through a transparent interceptor
  that accepts every TCP connect: a WAN scan of 1.1.1.1 reported ports
  54321 / 18765 / 9999 all open (~3 ms each, proxy env unset). Loopback
  scans discriminate correctly (a test listener on 18765 was found;
  9999 / 54321 stayed closed), and `ping_host` labels its fallback
  honestly: `tcp timing (icmp unavailable here)`.
- On a direct network (a normal host, Termux, a LAN) sockets are real:
  start with `python main.py scan <your router IP>`.
