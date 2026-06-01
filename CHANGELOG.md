# CHANGELOG

## v1.0.0 — 2026-05-31

Initial v1 lock-in. Pinned to node `v1.28.5`.

Every route, schema, error envelope, and fixture in this directory is
**Final**. No prior versions. No backwards-compatibility surface. No
intent to ship v2.

### Surfaces locked

- P-Chain JSON-RPC — 35 methods including the v1 atomic primitive
  `platform.createSovereignL1`.
- X-Chain JSON-RPC — UTXO settlement surface.
- C-Chain JSON-RPC — `eth_*` subset + `admin_importChain`. 18 active
  precompiles at fixed slot addresses.
- `/ext/info` — 14 methods.
- `/ext/admin` — 21 methods (operator-only).
- `/ext/health` — 3 endpoints (liveness, readiness, deep).
- `/ext/metrics` — Prometheus scrape.
- Keystore — 5 methods (off by default in production).
- Warp — 3 publish/unpublish methods + cross-chain message envelope.
- ZAP — binary transport, X25519 + ML-KEM-768 hybrid PQ handshake.

### Fixtures

All `fixtures/*.json` captured live from `https://api.lux.network` on
2026-05-31 against `luxd/1.28.5` (git commit
`6ca9b391e9f907a523f8718e4e555bdd25afe4cd`).
