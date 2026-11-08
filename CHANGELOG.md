# Changelog

## 1.1.0 — 2026-11-08 (Darion's direction: online, hold gates removed)
- HOLD gate system REMOVED; the council reviews but refuses nothing.
- NEW llmx_netlab/live.py — real sockets: DNS lookup, TCP connect + latency,
  port scan (named host), ping (system ICMP where permitted, TCP-timing
  fallback), TTL traceroute feeding the tracker (start/middle/end), HTTP
  probe, IP geo lookup (ip-api.com, approximate).
- New commands: ping / scan / trace / connect / dns / http / geo.
- Verified: pytest 36 passed (incl. real loopback socket tests), CHECKS 23/23.
- Environment note: in this build sandbox ICMP/UDP are blocked and a
  transparent egress proxy accepts all TCP connects, so WAN scan results
  from here are proxy-tainted; on a normal network results discriminate.

## 1.0.0 — 2026-11-08
- Merge of the LLM-x architecture diagram + the 7-page computer networking
  notes into one offline system: RAG tutor over the notes KB, subnet /
  topology / layer / device engines, tiny bigram SLM, council (Carbon 4
  decider + Muse advisor), guardrails, MLOps benchmark.
- Darion's additions: IP hopper/tracker/mapper (start / middle / end),
  Google Earth KML export seat, Google Flow video-planning seat,
  Gemini Carbon 4 Extended Thinking tiers.
