# AGENTS.md

Operator surface contract for `~/work/lux/openapi/`.

## What is stable

Every method, schema, error envelope, and example in every yaml file is
**Final**. No method documented in v1.0.0 will change shape, change
semantics, or be removed without a wholly new version (v2.0.0). There
will be no v2.0.0; the contract is a permanent lock.

## What is not stable

Nothing. v1 is the lock.

## Rules for agents touching this directory

1. **Never edit a method in place to change shape.** If a method needs
   a different shape, add a new method with a new name; never break the
   v1 surface.
2. **Never add `deprecated: true`.** Methods are either Final (in v1)
   or wholly absent (in v2 — which does not exist).
3. **Never `$ref` across yaml files.** Each file is fully
   self-contained.
4. **Never mention other brands.** This spec describes the core
   protocol only.
5. **Every new fixture must be live.** Capture from a real node;
   never fabricate.
6. **Every `description` cites file:line** of the canonical
   implementation in `~/work/lux/node/`.

## Where the canonical implementation lives

| Surface | Path |
|---------|------|
| P-Chain | `~/work/lux/node/vms/platformvm/service.go` |
| X-Chain | `~/work/lux/node/vms/xvm/service.go` |
| C-Chain | `~/work/lux/evm/` (Coreth-derived) |
| info    | `~/work/lux/node/service/info/service.go` |
| admin   | `~/work/lux/node/service/admin/service.go` |
| health  | `~/work/lux/node/service/health/service.go` |
| warp    | `~/work/lux/node/service/warp/service.go` |
| keystore| `~/work/lux/node/service/keystore/service.go` |
| zap     | `~/work/lux/zap/` |

## How to validate

```sh
make openapi-lint
```

`make openapi-lint` runs `python3 scripts/validate_openapi.py` which
loads each yaml, asserts OpenAPI v3.1 shape, and asserts every fixture
matches its declared schema.

## How to refresh fixtures

```sh
make openapi-fixtures HOST=https://api.lux.network
```

This re-runs each fixture's recorded RPC against `HOST` and rewrites
`fixtures/*.json` with the new response body. Diff before committing.
