DOMAIN = puhrez.com
REMOTE ?= origin
.DEFAULT_GOAL := help

.PHONY: help front build clean


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

public: build ## Push to aws and remote
	git push ${REMOTE}
	aws s3 sync public s3://${DOMAIN} --acl "public-read" --cache-control max-age=86400 --expires "2034-01-01T00:00:00Z" --content-encoding gzip

build:  clean ## Minify and compress
	minify -r -o public/ frontend/
	cp frontend/favicon.ico public/
	cp -r frontend/assets public
	cp -r frontend/things/articles/assets public/things/articles
	find public -type f -exec gzip "{}" \; -exec mv "{}.gz" "{}" \;

clean:  ## Clean up for fresh build state
	rm -rf public
