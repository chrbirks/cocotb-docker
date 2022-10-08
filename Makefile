docker-build:
	@DOCKER_BUILDKIT=1 docker build -t cocotb-docker .

docker-sim:
	docker run \
	--init \
	--cap-add \
	SYS_PTRACE \
	-u $$(id -u):$$(id -g) \
	-v "$$(pwd):/test_root" \
	-v /net/fs01/firmware-tools:/net/fs01/firmware-tools \
	-t \
	cocotb-docker

docker-shell:
	docker run \
	--init \
	--cap-add \
	SYS_PTRACE \
	-u $$(id -u):$$(id -g) \
	-v "$$(pwd):/test_root" \
	-v /net/fs01/firmware-tools:/net/fs01/firmware-tools \
	-i -t \
	--entrypoint /bin/bash \
	cocotb-docker

clean:
	$(MAKE) -f docker.mk clean

cleanall:
	$(MAKE) -f docker.mk cleanall

# .PHONY: help

# help: ## This help.

# .DEFAULT_GOAL := help
