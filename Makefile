.PHONY: test build bump publish

test:
	uv run pytest tests

build:
	rm -rf dist
	uv build

# make bump [part=patch|minor|major]
bump:
	uv version --bump $(or $(part),patch)

# токен берётся из UV_PUBLISH_TOKEN в окружении
publish: test build
	uv publish
