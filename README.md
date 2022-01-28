# Ansible Role - Wireguard Site-to-Site VPN

Role to deploy Wireguard Site-to-Site VPN setups.

**Tested:**
* Debian 11

## Functionality

* **Package installation**
  * WireGuard
  * Resolvconf (_name resolution_)


* **Configuration**
  * Simplified configuration by the mapping of **topologies**
  * Supported topologies:
    * single - simply connect two nodes
  * In progress:  (**NOT YET AVAILABLE**)
    * Topologies (*currently testing dynamic routing*)
       * star - one or multiple central hubs to connect branch/edge sites (**NOT YET AVAILABLE**)
       * mesh - connect each of the peers to every other one (**NOT YET AVAILABLE**)


  * **Default config**:
    * Saving private-key in file
    * Disabling route auto-adding (*anti-lockout & customization*)
    * Enabled syslog-logging with instance-identifiers
 

  * **Default opt-ins**:
    * Installation of 'resolvconf' for name-resolution to work
    * Using PSK for additional security


  * **Default opt-outs**:
    * Traffic forwarding (*router-like*)


## Info

* **Note:** this role currently only supports debian-based systems


* **Note:** Most of this functionality can be opted in or out using the main defaults file and variables!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Warning:** Tunnels that have fallen out of the config-scope will not yet be purged from the target-system.
This functionality will be added later on!


* **Note:** The star and mesh topologies depend heavily on the way the routing is implemented.
In those setups I would not recommend using the auto-added routes!
Therefore, configuring static routes becomes confusing/messy very quickly.
I'll check to get dynamic routing up-and-running before continuing with those topologies!


## Setup

None.

## Usage

### Config

You can define your WireGuard topologies spanning multiple hosts or host-groups.

The role will filter the topologies to the ones the current target-host is a part of and configure those.

```yaml
wireguard:
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

    site_a:  # srv04 is a device behind NAT
      peers:
        srv02:
          Endpoint: 'srv02.wg.template.ansibleguy.net'
          Address: '10.100.0.5/30'
          PersistentKeepalive: 25
        srv04:
          Address: '10.100.0.6/30'
          PersistentKeepalive: 25
```

The host-keys will be saved in the roles 'files' directory.

You might want to use 'ansible-vault' to encrypt those:
```bash
ansible-vault encrypt roles/ansibleguy.infra_wireguard/files/keys/some_file.key
```

### Result

```bash
guy@srv03:~# cat /etc/wireguard/dc_nl.conf
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: single
> 
> [Interface]
> Address = 10.100.0.2/30
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/dc_nl_srv03.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> 
> [Peer]
> PublicKey = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
> PresharedKey = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=
> AllowedIPs = 10.100.0.1/32, 0.0.0.0/0, ::/0
> Endpoint = srv02.wg.template.ansibleguy.net:51820

guy@srv03:~# tail /var/log/syslog | grep wireguard_
> Jan 28 23:53:55 srv03 wireguard_dc_nl[6566]: [#] ip link add dc_nl type wireguard
> Jan 28 23:53:55 srv03 wireguard_dc_nl[6566]: [#] wg setconf dc_nl /dev/fd/63
> Jan 28 23:53:55 srv03 wireguard_dc_nl[6566]: [#] ip -4 address add 10.100.0.2/30 dev dc_nl
> Jan 28 23:53:55 srv03 wireguard_dc_nl[6566]: [#] ip link set mtu 1500 up dev dc_nl
> Jan 28 23:53:55 srv03 wireguard_dc_nl[6587]: [#] resolvconf -a tun.dc_nl -m 0 -x
> Jan 28 23:53:55 srv03 wireguard_dc_nl[6566]: [#] wg set dc_nl private-key /etc/wireguard/keys/dc_nl_srv03.key

guy@srv03:~# ip a
> 7: dc_nl: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>    link/none 
>    inet 10.100.0.2/30 scope global dc_nl
>       valid_lft forever preferred_lft forever
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
