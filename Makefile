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
	SIM=verilator $(MAKE) -f docker.mk clean # Set verilator as simulator or it will complain that vcs is not sourced

cleanall:
	SIM=verilator $(MAKE) -f docker.mk cleanall # Set verilator as simulator or it will complain that vcs is not sourced

# .PHONY: help

# help: ## This help.

# .DEFAULT_GOAL := help
