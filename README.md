# WORK IN PROGRESS - DO NOT USE IN PRODUCTION!

# Ansible Role - Wireguard Site-to-Site VPN

Role to deploy advanced Wireguard Site-to-Site VPN setups.

Used as **routed vpn** to gain the ability to map redundancies/failover.

**Tested:**
* Debian 11

## Functionality

* **Package installation**
  * Ansible dependencies (_minimal_)


* **Configuration**
  * Simple configuration for complex topologies/setups
  * Three supported **topologies**:
    * line - simply connect two nodes
    * star - one or multiple central hubs to connect branch/edge sites
    * mesh - connect each of the peers to every other one (_also known as full-mesh_)

  * Support to use multiple internet-uplinks (_routing failover_)

  * **Default config**:
    * 
 

  * **Default opt-ins**:
    * 


  * **Default opt-outs**:
    * 


## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of this functionality can be opted in or out using the main defaults file and variables!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Info:** **Dynamic routing** is not yet supported - but will be added later on to simplify complexer setups.


## Setup

For this role to work - you must install its dependencies first:

```
ansible-galaxy install -r requirements.yml
```

Also: the **Python3 module 'netaddr'** is needed on the controller-system for dynamic TunnelIP mapping to work => the role will try to install it when ran.


## Usage

### Config

First you will have to configure your topologies:

```yaml
wireguard_s2s:
  groups:
    

  ...
```

After that you will need to configure your sites:

```yaml
wireguard_s2s:
  groups:
    ...

  sites:
    

  ...
```

Link your inventory-hosts to the role-config:

```yaml
# inventory/vpn/host_vars/server1.yml
wireguard_s2s_name: 'HQ'

```

You might want to use 'ansible-vault' to encrypt your passwords:
```bash
ansible-vault encrypt_string
```

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

There are also some useful **tags** available:
* 
*
