[![WireGuard](https://www.wireguard.com/img/wireguard.svg)](https://www.wireguard.com)

# Ansible Role - WireGuard Site-to-Site VPN

Role to deploy WireGuard Site-to-Site VPN setups.

**Tested:**
* Debian 11

## Functionality

* **Package installation**
  * WireGuard
  * Resolvconf (_name resolution_)


* **Configuration**
  * Simplified configuration by the mapping of **topologies**
  * **Supported topologies**:
    * **[single](https://github.com/ansibleguy/infra_wireguard/blob/stable/ExampleSingle.md)** - simply connect two nodes
    * **[star](https://github.com/ansibleguy/infra_wireguard/blob/stable/ExampleStar.md)** - multiple edge/branch nodes connect to one central hub
    * **[mesh](https://github.com/ansibleguy/infra_wireguard/blob/stable/ExampleMesh.md)** - connect each of the peers to every other one
  * **Keys**
    * Generating public/private key-pairs for each host in a topology (*WG identifies peer by publicKey*)
    * Keys are written to the controller for consistency
  * **Routing**
    * The routing is **up to you to manage**! You could enable the auto-added WG routes or add custom up-/down-scripts.
    * We might add dynamic routing using [THIS](https://github.com/ansibleguy/infra_dynamic_routing) role later on.


  * **Default config**:
    * Saving private-key in file
    * Disabling route auto-adding (*anti-lockout & customization*)
    * Enabled syslog-logging with instance-identifiers
    * Restarting wg-service on changes
 

  * **Default opt-ins**:
    * Installation of 'resolvconf' for name-resolution to work
    * Using PSK for additional security
    * Purging of orphaned tunnels


  * **Default opt-outs**:
    * Traffic forwarding (*router-like*)


## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of this functionality can be opted in or out using the main defaults file and variables!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Warning:** Be aware that the WireGuard up-/down-scripts are executed as the **TUNNEL SERVICE** goes up; **NOT THE TUNNEL CONNECTION**.

  You might need to take this in consideration when planning/configuring your routes and metrics!


* **Info:** Here are some common error-messages you might see when mis-configuring your tunnels:
  * Error: ```RTNETLINK answers: Address already in use```
    * Problem: each tunnel must use a unique port to listen on - you might have assigned a duplicate port (*or forgot to set it to a custom one*)
  * Error: ```failure in name resolution```
    * Problem: the dns-hostname the service is trying to connect to is not set (*correctly*) or your target-host has general problems resolving DNS
  * Error: Tunnels are configured, services are running, but connection isn't up
    * Problem: the connection port might be blocked by a firewall


* **Info:** You should keep your topology names short. And try not to use special characters => they will get removed automatically (*except '_=+.-'*) so the key is a valid interface-name!


* **Info:** Interfaces will get a prefix prepended: (*can be changed as provided*)
  * single => wgS_
  * star => wgX_
  * mesh => wgM_
  

* **Info:** How to run tests is described [here](https://github.com/ansibleguy/infra_wireguard/blob/stable/molecule/default/Testing.md)


## Setup

For this role to work - you must install its dependencies first: (*on the controller*)

```
pip install netaddr
```

## Usage

### Examples

Here some detailed config examples and their results:

* [Topology - Single](https://github.com/ansibleguy/infra_wireguard/blob/stable/ExampleSingle.md)
* [Topology - Star](https://github.com/ansibleguy/infra_wireguard/blob/stable/ExampleStar.md)
* [Topology - Mesh](https://github.com/ansibleguy/infra_wireguard/blob/stable/ExampleMesh.md)


### Config

You can define your WireGuard topologies spanning multiple hosts or host-groups.

The role will filter the topologies to the ones the current target-host is a part of and configure those.

These peer-keys must match your ansible inventory-hostnames!

```yaml
wireguard:
  restart_on_change: true  # allow the wg-services to be restarted on changes

  topologies:
    dc_nl:
      type: 'single'
      peers:
        srv02:
          Endpoint: 'srv02.wg.template.ansibleguy.net'
          Address: '10.100.0.1/30'

        srv03:
          Endpoint: 'srv03.wg.template.ansibleguy.net'
          Address: '10.100.0.2/30'
```

The host-keys will be saved in the roles 'files' directory.

You might want to use 'ansible-vault' to encrypt those:
```bash
ansible-vault encrypt roles/ansibleguy.infra_wireguard/files/keys/some_file.key
```

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

Or if you have encrypted your keys:

```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml --ask-vault-pass
```

There are also some useful **tags** available:
* base
* config
* tunnels
* purge

If you only want to **provision one of your topologies** you can set the following variable at execution time:

```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml -e only_topo=TOPOLOGY_KEY
```
