# cocotb-docker
Example test bench for cocotb/pyuvm running in a Docker container

To build the docker image and run the simulation
```
make docker-build docker-sim
```

The default simulator for the docker container is `vcs`. To simulate outside docker and use e.g. `verilator` instead run
```
SIM=verilator make sim
```

To start a shell in the container
```
make docker-shell
```

To clean all simulation files
```
make cleanall
```
