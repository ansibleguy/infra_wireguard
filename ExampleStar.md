# WireGuard Example - Topology 'Star'


## Off-Screen

This was done before running this example:

* Basic host-setup => using [THIS](https://github.com/ansibleguy/linub_bootstrap) role
* Network-interfaces and -capabilities => using [THIS](https://github.com/ansibleguy/linux_networking) role
* Allowing traffic for the used ports => using [THIS](https://github.com/ansibleguy/linux_ufw) role

## Config

You have to mind some cases when you configure a star-topology:

* The central server needs to be reachable per static IP or public DNS
* We would not recommend using the auto-added routes on the center node!

  A configuration error could lock you out as the routes get added with a metric of zero!

  Also: the build-in auto-added routes will not work for this kind of connection as the gateway is not set.

* There may only be one central server!
  
  If you want to configure a redundant star-topology => just use two.

* Don't forget to allowed forwarded traffic using iptables or ufw!

Basically the edge-nodes are using the 'single' config and the 'center' node has a customized config with N peers.

The prefix 'wgX_' will be prepended for interfaces of the topology 'star'.

This prefix and much more can be changed as provided.

```yaml
# to reference networks
site_networks:
  super: '192.168.0.0/17'
  nl:
    ip: '10.100.10.3'
    net: '192.168.30.0/24'
  de:
    ip: '10.100.10.4'
    net: '192.168.40.0/24'
  at:
    ip: '10.100.10.7'
    net: '192.168.70.0/24'

# vpn config
wireguard:
  support:
    traffic_forwarding: true

  topologies:
    dc_nl:
      type: 'star'
      peers:
        srv03:
          role: 'center'
          Endpoint: 'srv03.wg.template.ansibleguy.net'
          Address: "{{ site_networks.nl.ip }}/24"
          AllowedIPs: "{{ site_networks.super }}"  # can be list or single element
          PostUp:
            - "ip route add {{ site_networks.de.net }} metric 100 dev %i via {{ site_networks.de.ip }}"
            - "ip route add {{ site_networks.at.net }} metric 100 dev %i via {{ site_networks.at.ip }}"

        srv04:
          Endpoint: 'srv04.wg.template.ansibleguy.net'
          Address: "{{ site_networks.de.ip }}/24"
          Route: true  # auto-add routes to peer 'AllowedIPs'
          AllowedIPs: "{{ site_networks.de.net }}"

        srv07:  # srv07 is behind a firewall
          Address: "{{ site_networks.at.ip }}/24"
          ListenPort: ''  # does not need to listen on any port
          Route: true
          NATed: true
          AllowedIPs: "{{ site_networks.at.net }}"
```

## Result

### Controller

```bash
guy@ansible:~# ls -l roles/ansibleguy.infra_wireguard/files/keys/
> -rw-r----- dc_nl.psk
> -rw-r----- dc_nl_srv03.key
> -rw-r--r-- dc_nl_srv03.pub
> -rw-r----- dc_nl_srv04.key
> -rw-r--r-- dc_nl_srv04.pub
> -rw-r----- dc_nl_srv07.key
> -rw-r--r-- dc_nl_srv07.pub
```

You might want to use 'ansible-vault' to encrypt the private keys:
```bash
ansible-vault encrypt roles/ansibleguy.infra_wireguard/files/keys/some_file.key
```

### SRV03 (center)

```bash
# status
guy@srv03:~# wg show all
> interface: wgX_dc_nl
>   public key: BkxQWjX6k1QxP75uRxnFjCWOozNR9dJEQaWiPcXBDzE=
>   private key: (hidden)
>   listening port: 51820
> 
> peer: 7KKTmFPW+nup7M0PlzgeUKcul1d5GY/F2JUIeAwEZRQ=
>   preshared key: (hidden)
>   endpoint: IP:37910
>   allowed ips: 10.100.10.7/32, 192.168.70.0/24
>   latest handshake: 1 minute, 27 seconds ago
>   transfer: 868 B received, 1.23 KiB sent
>   persistent keepalive: every 25 seconds
> 
> peer: Nujd72NiAZHzxBBIrXAs6JuoAhvkgKtp7zIe8+V7cio=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.100.10.4/32, 192.168.40.0/24
>   latest handshake: 7 minutes, 26 seconds ago
>   transfer: 596 B received, 476 B sent

guy@srv03:~# systemctl status wg-quick@*
> ● wg-quick@wgX_dc_nl.service - WireGuard via wg-quick(8) for wgX_dc_nl
>      Loaded: loaded (/lib/systemd/system/wg-quick@.service; disabled; vendor preset: enabled)
>     Drop-In: /etc/systemd/system/wg-quick@.service.d
>              └─override.conf
>      Active: active (exited) since Sat 2022-01-29 21:00:18 CET; 7min ago
>        Docs: man:wg-quick(8)
>              man:wg(8)
>              https://www.wireguard.com/
>              https://www.wireguard.com/quickstart/
>              https://git.zx2c4.com/wireguard-tools/about/src/man/wg-quick.8
>              https://git.zx2c4.com/wireguard-tools/about/src/man/wg.8
>              https://github.com/ansibleguy/infra_wireguard

# config
guy@srv03:~# cat /etc/wireguard/wgX_dc_nl.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: star
> # role: center
> 
> [Interface]
> Address = 10.100.10.3/24
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/dc_nl_srv03.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> PostUp = ip route add 192.168.40.0/24 metric 100 dev %i via 10.100.10.4
> PostUp = ip route add 192.168.70.0/24 metric 100 dev %i via 10.100.10.7
> 
> [Peer]
> # srv04
> PublicKey = Nujd72NiAZHzxBBIrXAs6JuoAhvkgKtp7zIe8+V7cio=
> PresharedKey = NNMpluiPivWCGmV78jnkXyjL5JQYmr2/FFuIjp0Lxos=
> AllowedIPs = 10.100.10.4/32, 192.168.40.0/24
> Endpoint = srv04.wg.template.ansibleguy.net:51820
> 
> [Peer]
> # srv07
> PublicKey = 7KKTmFPW+nup7M0PlzgeUKcul1d5GY/F2JUIeAwEZRQ=
> PresharedKey = NNMpluiPivWCGmV78jnkXyjL5JQYmr2/FFuIjp0Lxos=
> AllowedIPs = 10.100.10.7/32, 192.168.70.0/24
> PersistentKeepalive = 25

# interfaces & routing
guy@srv03:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.100.10.0     0.0.0.0         255.255.255.0   U     0      0        0 wgX_dc_nl
> 192.168.40.0    10.100.10.4     255.255.255.0   UG    100    0        0 wgX_dc_nl
> 192.168.70.0    10.100.10.7     255.255.255.0   UG    100    0        0 wgX_dc_nl

guy@srv03:~# ip a
> # prettyfied
> 9: wgX_dc_nl: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.10.3/24 scope global wgX_dc_nl
```

### SRV04

```bash
# status
guy@srv04:~# wg show all
> interface: wgX_dc_nl
>   public key: Nujd72NiAZHzxBBIrXAs6JuoAhvkgKtp7zIe8+V7cio=
>   private key: (hidden)
>   listening port: 51820
> 
> peer: BkxQWjX6k1QxP75uRxnFjCWOozNR9dJEQaWiPcXBDzE=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.100.10.3/32, 192.168.0.0/17

# config
guy@srv04:~# cat /etc/wireguard/wgX_dc_nl.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: star
> # role: edge
> 
> [Interface]
> Address = 10.100.10.4/24
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/dc_nl_srv04.key
> MTU = 1500
> Table = 1000
> DNS = 1.1.1.1, 8.8.8.8
> 
> [Peer]
> PublicKey = BkxQWjX6k1QxP75uRxnFjCWOozNR9dJEQaWiPcXBDzE=
> PresharedKey = NNMpluiPivWCGmV78jnkXyjL5JQYmr2/FFuIjp0Lxos=
> AllowedIPs = 10.100.10.3/32, 192.168.0.0/17
> Endpoint = srv03.wg.template.ansibleguy.net:51820

# interfaces & routing
guy@srv04:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.100.10.0     0.0.0.0         255.255.255.0   U     0      0        0 wgX_dc_nl

guy@srv04:~# ip a
> # prettyfied
> 17: wgX_dc_nl: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.10.4/24 scope global wgX_dc_nl
```

### SRV07

```bash
# status
guy@srv07:~# wg show all
> interface: wgX_dc_nl
>   public key: 7KKTmFPW+nup7M0PlzgeUKcul1d5GY/F2JUIeAwEZRQ=
>   private key: (hidden)
>   listening port: 52255
> 
> peer: BkxQWjX6k1QxP75uRxnFjCWOozNR9dJEQaWiPcXBDzE=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.100.10.3/32, 192.168.0.0/17
>   latest handshake: 45 seconds ago
>   transfer: 14.91 KiB received, 16.17 KiB sent

# config
guy@srv07:~# cat /etc/wireguard/wgX_dc_nl.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: star
> # role: edge
> 
> [Interface]
> Address = 10.100.10.7/24
> PostUp = wg set %i private-key /etc/wireguard/keys/dc_nl_srv07.key
> MTU = 1500
> Table = 1000
> DNS = 1.1.1.1, 8.8.8.8
> 
> [Peer]
> PublicKey = BkxQWjX6k1QxP75uRxnFjCWOozNR9dJEQaWiPcXBDzE=
> PresharedKey = NNMpluiPivWCGmV78jnkXyjL5JQYmr2/FFuIjp0Lxos=
> AllowedIPs = 10.100.10.3/32, 192.168.0.0/17
> Endpoint = srv03.wg.template.ansibleguy.net:51820

# interfaces & routing
guy@srv07:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.100.10.0     0.0.0.0         255.255.255.0   U     0      0        0 wgX_dc_nl

guy@srv07:~# ip a
> # prettyfied
> 18: wgX_dc_nl: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.10.7/24 scope global wgX_dc_nl
```

