# syntax=docker/dockerfile:1

# FROM verilator/verilator:4.106 as verilator
FROM 0x01be/verilator as verilator
FROM archlinux

# COPY set_umask.sh /set_umask.sh
# ENTRYPOINT ["/set_umask.sh"]

WORKDIR /test_root

## Install cocotb and extra python packages from requirements.txt
RUN pacman -Sy
RUN pacman -S xorg-xeyes xorg-xauth python python-pip make grep time bc gcc --noconfirm
COPY requirements.txt .
RUN pip3 install -r requirements.txt

## Set default shell
SHELL ["/bin/bash", "-ec"]

## Set up Synopsys VCS
ARG BUILD_ARG_SNPSLMD_LICENSE_FILE
ARG BUILD_ARG_VCS_ROOT_DIR
ARG BUILD_ARG_VCS_VER
ENV SNPSLMD_LICENSE_FILE ${BUILD_ARG_SNPSLMD_LICENSE_FILE}
ENV VCS_ROOT_DIR ${BUILD_ARG_VCS_ROOT_DIR}
ENV VCS_VER ${BUILD_ARG_VCS_VER}
ENV SNPS_SIM_DEFAULT_GUI=dve
ENV VCS_TARGET_ARCH="amd64"
ENV VCS_HOME="$VCS_ROOT_DIR/$VCS_VER"
ENV SYNOPSYS_VCS_HOME="$VCS_HOME"
ENV VC_HOME="$VCS_ROOT_DIR/$VCS_VER"
ENV DESIGNWARE_HOME="$VCS_HOME"/../../vip_lib
ENV UVM_HOME="$VCS_HOME"/etc/
ENV PATH="$VCS_HOME/bin":$PATH

## Set up Verilator
COPY --from=verilator /opt/verilator/ /opt/verilator/
ENV VERILATOR_ROOT=/opt/verilator
ENV PATH="$VERILATOR_ROOT/bin":$PATH

## Compile and run testbench
CMD make -f docker.mk
