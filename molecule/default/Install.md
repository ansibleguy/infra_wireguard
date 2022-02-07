# Notice

This testing will use over 10 docker instances and might be too much for a pc to handle.

You may want to use a remote docker server.

# Installation

## Docker

You need a docker server/instance to deploy the test-servers to.

### Install
Install docker as described [here](https://docs.docker.com/engine/install/ubuntu/)

```bash
sudo apt-get update
sudo apt-get -y install ca-certificates curl gnupg lsb-release
```
Add the repository
```bash
# ubuntu
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# debian
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### Configure

Either way - the docker server must have the following setting configured in '/etc/docker/daemon.json':

```bash
{"cgroup-parent": "docker.slice"}
```

Restart docker after adding that setting. This allows systemd to work inside the container without mapping cgroup manually.

For further information see: [serverfault.com](https://serverfault.com/questions/1053187/systemd-fails-to-run-in-a-docker-container-when-using-cgroupv2-cgroupns-priva)

#### Locally

This is NOT RECOMMENDED.

You will have to set-up docker as described [here](https://docs.docker.com/engine/security/rootless/).

Switch the docker_host to your local one. (_molecule/default/molecule.yml_)
```yaml
---

references:
  docker:
    all: &docker_all
      docker_host: 'unix://var/run/docker.sock'  # localhost
```

#### Remote

Installation
```bash
sudo apt-get -y install docker-ce-cli
```

As mentioned before/above - we recommend running the testing on a server.

You might want to consider using the [docker role](https://github.com/ansibleguy/infra_docker_minimal) to provision a docker server as a vm.

You will have to configure the ip-address to your docker-server. (_molecule/default/molecule.yml_)
```yaml
---

references:
  docker:
    all: &docker_all
      docker_host: 'tcp://172.16.111.91:2375'
```

But it seems like the docker module does not get the molecule config. (_Still connecting to localhost_)

Therefore, you will have to set this environmental variable in addition:

```bash
export DOCKER_HOST='tcp://172.16.111.91:2375'
```


## Molecule

Install testing tools:

```bash
pip3 install molecule molecule-docker
```

# Running

```bash
cd ansibleguy.infra_wireguard
# to run build the test instances, run the tests and clean up afterwards
molecule test

# for troubleshooting
molecule create
# now we can run the actual playbook as many times as we need/want
molecule converge
# test it
molecule verify
# clean it up when we finished troubleshooting
molecule destroy
```

# Background

The tests are creating:

* 3 Single Topologies

  * 1x Default config
  * 1x Auto-Routed
  * 1x NATed


* 3 Star Topologies


  * 1x Default star
  * 2x Redundant star (_two center nodes with routing failover_)


* 1 Mesh Topology


The config can be found in the 'converge.yml' file.

Connectivity is tested using simple pings.
