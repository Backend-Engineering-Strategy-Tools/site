IMAGE=ghcr.io/gohugoio/hugo:v0.160.1

all: serve

# Local Hugo (extended) — default targets
serve:
	hugo server --bind 0.0.0.0 --port 1313 --baseURL http://localhost:1313/ --disableFastRender --buildDrafts --buildFuture

build:
	hugo --minify

# Docker targets (kept as fallback)
docker-serve:
	docker run --rm -w /site -p 1313:1313 -v $(PWD):/site $(IMAGE) server --bind 0.0.0.0 --port 1313 --baseURL http://localhost:1313/ --disableFastRender --buildDrafts --buildFuture

docker-build:
	docker run --rm -w /site -v $(PWD):/site $(IMAGE) --minify

clean:
	rm -rf public
