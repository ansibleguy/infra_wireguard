[![WireGuard](https://www.wireguard.com/img/wireguard.svg)](https://www.wireguard.com)

# Ansible Role - WireGuard Site-to-Site VPN

Role to deploy WireGuard Site-to-Site VPN setups.

[![Molecule Test Status](https://badges.ansibleguy.net/infra_wireguard.molecule.svg)](https://molecule.readthedocs.io/en/latest/)
[![YamlLint Test Status](https://badges.ansibleguy.net/infra_wireguard.yamllint.svg)](https://yamllint.readthedocs.io/en/stable/)
[![Ansible-Lint Test Status](https://badges.ansibleguy.net/infra_wireguard.ansiblelint.svg)](https://ansible-lint.readthedocs.io/en/latest/)
[![Ansible Galaxy](https://img.shields.io/ansible/role/57785)](https://galaxy.ansible.com/ansibleguy/infra_wireguard)
[![Ansible Galaxy Downloads](https://img.shields.io/badge/dynamic/json?color=blueviolet&label=Galaxy%20Downloads&query=%24.download_count&url=https%3A%2F%2Fgalaxy.ansible.com%2Fapi%2Fv1%2Froles%2F57785%2F%3Fformat%3Djson)](https://galaxy.ansible.com/ansibleguy/infra_wireguard)

**Tested:**
* Debian 11
* Raspbian 11

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


  * **Default config**:
    * Saving private-key in file
    * Disabling route auto-adding (*anti-lockout & customization*)
    * Enabled syslog-logging with instance-identifiers
    * Restarting wg-service on changes
 

  * **Default opt-ins**:
    * Using PSK for additional security
    * Purging of orphaned tunnels


  * **Default opt-outs**:
    * Installation of 'resolvconf' for name-resolution override
    * Traffic forwarding (*router-like*)


  * **Features**:
    * Showing last logs if service re-/start fails
    * Auto-Connect of dynamic peer

----

## Contributing

Feel free to:

* Open PRs

* Start discussions

* Open issues => after checking out the troubleshooting guide below!

----

## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of the role's functionality can be opted in or out.

  For all available options - see the default-config located in the main defaults-file!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Warning:** Be aware that the WireGuard up-/down-scripts are executed as the **TUNNEL SERVICE** goes up; **NOT THE TUNNEL CONNECTION**.

  You might need to take this in consideration when planning/configuring your routes and metrics!


* **Info:** You should keep your topology names short. And try not to use special characters => they will get removed automatically (*except '_=+.-'*) so the key is a valid interface-name!


* **Info:** Interfaces will get a prefix prepended: (*can be changed as provided*)
  * single => wgs_
  * star => wgx_
  * mesh => wgm_
  

* **Info:** How to run tests is described [here](https://github.com/ansibleguy/infra_wireguard/blob/stable/molecule/default/Usage.md)


* **Info:** The host-keys will be saved in the roles 'files' directory by default. 

  This key-directory can be changed using the 'controller_key_store' variable!


* **Info:** If you are using **OPNSense firewalls** - you can use the [ansibleguy.opnsense Ansible collection](https://github.com/ansibleguy/collection_opnsense/blob/stable/docs/use_wireguard.md) to manage those WireGuard tunnels.

----

## Setup

For this role to work - you must install its dependencies first: (*on the controller*)

```
ansible-galaxy install -r requirements.yml
```

```
pip install netaddr
```

----

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

You might want to use 'ansible-vault' to encrypt the host-key files:
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

----

## Troubleshooting

If you encounter connectivity problems => please follow these steps to narrow down their source:

### 1. Is the vpn active?

```bash
wg show all
```
  
**If not**:

* The connection cannot be established - maybe a misconfiguration or some networking issue (_firewall blocking traffic_)
   
* Check your WireGuard logs:

  ```bash
  # 'wgs_ts2' is the WireGuard tunnel-interface in this example
  guy@srv:~# journalctl -u wg-quick@wgs_ts2
  > -- Journal begins at Tue 2022-02-08 15:46:07 UTC, ends at Tue 2022-02-08 17:01:27 UTC. --
  > Feb 08 16:12:31 test-ag-wg-s3 systemd[1]: Starting WireGuard via wg-quick(8) for wgs_ts2...
  > Feb 08 16:12:31 test-ag-wg-s3 wireguard_wgs_ts2[10698]: [#] ip link add wgs_ts2 type wireguard
  > Feb 08 16:12:31 test-ag-wg-s3 wireguard_wgs_ts2[10698]: [#] wg setconf wgs_ts2 /dev/fd/63
  ```

  * Here are some common error-messages you might see when mis-configuring your tunnels:
    * Error: ```RTNETLINK answers: Address already in use```
      * Problem: each tunnel must use a unique port to listen on - you might have assigned a duplicate port (*or forgot to set it to a custom one*)
    * Error: ```failure in name resolution```
      * Problem: the dns-hostname the service is trying to connect to is not set (*correctly*) or your target-host has general problems resolving DNS
    * Error: Tunnels are configured, services are running, but connection isn't up
      * Problem: the connection port might be blocked by a firewall


### 2. Is traffic going over the tunnel?

Ping the remote WireGuard tunnel ip - in the configuration this is the 'Address'.

**Important**: define the source-ip to use!

```bash
# .2 is the remote WG-IP; .1 is the local one
ping 10.0.1.2 -I 10.0.1.1
```

**If not**:

* Make sure the tunnel is really running!
* Check if the keys match => ```wg show all``` should show 'the same' public keys on both sides:

  ```bash
  guy@srv1:~# wg show all
  > interface: wgx_tx1
  > public key: FJgEWygMdiqRcTvij3PiXOtPJNtTENQkv301l2PGhwY=
  > ...
  ```
  
  ```bash
  guy@srv2:~# wg show all
  > ...
  > peer: FJgEWygMdiqRcTvij3PiXOtPJNtTENQkv301l2PGhwY=
  > ...
  ```
  
  To re-generate mismatched keys, just remove them from the controllers 'files' directory and re-run the role on the servers.

### 3. Is traffic being routed over the tunnel?

This **only applies** to tunnels that are used to **connect remote subnets**.

We test it with another ping - this time using the local subnet (_not WG-IP_).

```bash
# 172.30.1.1 is the remote 'subnet'; 172.20.0.1 is the local one
ping 172.30.1.1 -I 172.20.0.1
# you can also run a traceroute to get more information about the route taken:
traceroute 172.30.1.1
```

If you are motivated => you can run a tcpdump on the remote host to find out if traffic is coming 'through the tunnel'.

```bash
# 'wgs_ts2' is the WireGuard tunnel-interface in this example
guy@srv:~# tcpdump -i wgs_ts2
> tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
> listening on wgs_ts2, link-type RAW (Raw IP), snapshot length 262144 bytes
> 17:00:07.336550 IP 10.0.1.2 > 10.0.1.1: ICMP echo request, id 38770, seq 1, length 64
> 17:00:07.336695 IP 10.0.1.1 > 10.0.1.2: ICMP echo reply, id 38770, seq 1, length 64
```

**If not**:

* Check if a firewall is blocking any traffic between the hosts.
  
  UFW per example needs to allow incoming AND forwarding traffic.

* Check your routing configuration for errors and compare it against the 'running config':

  ```bash
  # show 'simple' overview
  ip route show all
  # show ALL routes
  ip route show table all
  # to remove unneccessary broadcast/local routes
  ip route show table all | grep -vE '^(broadcast|local)\s'
  ```

* The hosts need to support traffic forwarding!

  Make sure the setting 'wireguard.support.traffic_forwarding' is enabled.

* You could have forgotten to add the target network to the 'AllowedIPs'.

  This is necessary for star & mesh topologies!

### 4. Still having issues

It might be a role-problem/-bug or some other edge-case => please feel free to open a GitHub issue!

Please provide the troubleshooting results in the issue.
