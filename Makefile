SIM ?= vcs

docker-build:
	@DOCKER_BUILDKIT=1 docker build -t cocotb-docker .

docker-sim:
	docker run \
	--rm \
	--init \
	--cap-add \
	SYS_PTRACE \
	-u $$(id -u):$$(id -g) \
	-h $$(hostname) \
	-e USER="$${USER}" \
	-e SIM \
	-e DISPLAY="$${DISPLAY}" \
	-v "$$(pwd):/test_root" \
	-v /net/fs01/firmware-tools:/net/fs01/firmware-tools \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-t \
	cocotb-docker

docker-shell:
	docker run \
	--rm \
	--init \
	--cap-add \
	SYS_PTRACE \
	-u $$(id -u):$$(id -g) \
	-h $$(hostname) \
	-e USER="$${USER}" \
	-e DISPLAY="$${DISPLAY}" \
	-v "$$(pwd):/test_root" \
	-v /net/fs01/firmware-tools:/net/fs01/firmware-tools \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-i -t \
	--entrypoint /bin/bash \
	cocotb-docker

sim:
	$(MAKE) -f docker.mk

clean:
	SIM=verilator $(MAKE) -f docker.mk clean # Set verilator as simulator or it will complain that vcs is not sourced

cleanall:
	SIM=verilator $(MAKE) -f docker.mk cleanall # Set verilator as simulator or it will complain that vcs is not sourced

# .PHONY: help

# help: ## This help.

# .DEFAULT_GOAL := help
