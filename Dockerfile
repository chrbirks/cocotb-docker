# syntax=docker/dockerfile:1

FROM 0x01be/verilator as verilator
FROM archlinux

# COPY set_umask.sh /set_umask.sh
# ENTRYPOINT ["/set_umask.sh"]

WORKDIR /test_root

## Install cocotb and extra python packages from requirements.txt
RUN pacman -Sy
RUN pacman -S python python-pip make grep time bc gcc --noconfirm
COPY requirements.txt .
RUN pip3 install -r requirements.txt

## Set default shell
SHELL ["/bin/bash", "-ec"]

## Set up Synopsys VCS
ENV SNPSLMD_LICENSE_FILE=27020@flexlm01.silicom.dk
ENV SNPS_SIM_DEFAULT_GUI=dve
ENV BOHR_VCS_DIR="/net/fs01/firmware-tools/synopsys/vcs"
ENV TMP_VCS_VER="Q-2020.03-SP1"
ENV VCS_VER=${TMP_VCS_VER}
ENV VCS_TARGET_ARCH=amd64
ENV VCS_HOME="$BOHR_VCS_DIR/$VCS_VER"
ENV SYNOPSYS_VCS_HOME="$VCS_HOME"
ENV VC_HOME="$BOHR_VCS_DIR/$VCS_VER"
ENV DESIGNWARE_HOME="$VCS_HOME"/../../vip_lib
ENV UVM_HOME="$VCS_HOME"/etc/
ENV PATH="$VCS_HOME/bin":$PATH

## Set up Verilator
COPY --from=verilator /opt/verilator/ /opt/verilator/
ENV VERILATOR_ROOT=/opt/verilator
ENV PATH="$VERILATOR_ROOT/bin":$PATH

## Compile and run testbench
CMD make -f docker.mk