# Notice

This testing will use over 10 docker instances and might be too much for a pc to handle.

You may want to use a remote docker server.

# Usage

Check out the [Molecule Tutorial](https://github.com/ansibleguy/ansible_tutorial/blob/main/Molecule.md) on how to get started!

# Running

```bash
cd roles/ansibleguy.infra_wireguard
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
