IMAGE=ghcr.io/gohugoio/hugo:v0.157.0

all: build

build:
	docker run --rm -v $(PWD):/site $(IMAGE) --minify

serve: build
	docker run --rm -p 1313:1313 -v $(PWD):/site $(IMAGE) server --bind 0.0.0.0 --port 1313 --baseURL http://localhost:1313/ --disableFastRender --buildDrafts --buildFuture

clean:
	rm -rf public