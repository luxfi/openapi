.PHONY: openapi-lint openapi-fixtures help

help:
	@echo "openapi-lint     validate every yaml against the v3.1 contract"
	@echo "openapi-fixtures re-capture fixtures from HOST (default api.lux.network)"

openapi-lint:
	@python3 scripts/validate_openapi.py

HOST ?= https://api.lux.network

openapi-fixtures:
	@curl -sS $(HOST)/v1/info -X POST -H "Content-Type: application/json" \
		-d '{"jsonrpc":"2.0","id":1,"method":"info.getNetworkID"}' \
		| python3 -m json.tool > fixtures/info-getNetworkID-response.json
	@curl -sS $(HOST)/v1/health/liveness \
		| python3 -m json.tool > fixtures/health-liveness-response.json
	@curl -sS $(HOST)/v1/chain/P -X POST -H "Content-Type: application/json" \
		-d '{"jsonrpc":"2.0","id":1,"method":"platform.getHeight"}' \
		| python3 -m json.tool > fixtures/pchain-getHeight-response.json
	@echo "fixtures refreshed against $(HOST)"
