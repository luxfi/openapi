# Lux OpenAPI

Canonical OpenAPI v3.1 specification for the Lux core protocol.

Version pin: **v1.0.0** = node `v1.28.5`.

The spec is the contract the world consumes when integrating with the Lux
core protocol. Every method, schema, error envelope, and example
documented here is **Final**. There is no v0; there will be no v2.

## Files

| File | Surface | Transport |
|------|---------|-----------|
| `pchain.yaml` | P-Chain — validator registry, sovereign-L1 launch, chain manifest | JSON-RPC |
| `xchain.yaml` | X-Chain — UTXO settlement | JSON-RPC |
| `cchain.yaml` | C-Chain — primary EVM (`eth_*`) + node admin | JSON-RPC |
| `info.yaml`   | `/v1/info` — chain state, peers, bootstrap | JSON-RPC |
| `admin.yaml`  | `/v1/admin` — alias management, plugin management | JSON-RPC |
| `health.yaml` | `/v1/health` — liveness, readiness, deep checks | REST + JSON-RPC |
| `metrics.yaml`| `/v1/metrics` — Prometheus scrape | REST (text) |
| `keystore.yaml` | local keystore (off in production) | JSON-RPC |
| `warp.yaml`   | cross-chain message verification | JSON-RPC |
| `zap.yaml`    | binary RPC transport (X25519 + ML-KEM-768) | binary |
| `fixtures/`   | request/response snapshots captured live | JSON |

## Servers

```yaml
servers:
  - url: https://api.lux.network/v1        # mainnet
  - url: https://api-test.lux.network/v1   # testnet
  - url: https://api-dev.lux.network/v1    # devnet
```

The legacy `/ext/...` paths remain mounted on each node for direct
operator access. The `/v1/...` paths are the gateway-fronted public
contract.

## Regenerate

```sh
make openapi-lint    # validate every yaml against OpenAPI v3.1
make openapi-fixtures # re-capture fixtures from a live testnet node
```

The lint target shells out to `python3 scripts/validate_openapi.py` (no
external tooling required — the validator is pure-stdlib + PyYAML).

## Rules

- **OpenAPI v3.1** (JSON Schema draft 2020-12).
- **Self-contained.** No `$ref` across yaml files. The cost of debugging
  cross-file ref chains exceeds the cost of duplication.
- **No backwards-compatibility.** No `deprecated: true`. No alias
  paths. v1 is the lock; the next version is a wholly new contract.
- **Spec describes Lux only.** Zero references to other brands.
- **Every method's `description` cites the canonical
  implementation file:line.**

## Cross-references

The following LPs ship with this contract and define the on-protocol
semantics of the methods documented here:

- LP-016 — omnichain message router (`warp.yaml`)
- LP-017 — native bridge programs
- LP-018 — yield-bearing bridge
- LP-019 — threshold MPC (`zap.yaml` identity)
- LP-020 — Quasar consensus (`info.yaml` bootstrap semantics)
- LP-021 — Warp messaging (`warp.yaml` envelope)

`platform.createSovereignL1` (LP cross-ref slot reserved — see
`pchain.yaml` description fields).
