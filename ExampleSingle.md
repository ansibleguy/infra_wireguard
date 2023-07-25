# WireGuard Example - Topology 'Single'

## Off-Screen

This was done before running this example:

* Basic host-setup => using [THIS](https://github.com/ansibleguy/linux_bootstrap) role
* Network-interfaces and -capabilities => using [THIS](https://github.com/ansibleguy/linux_networking) role
* Allowing traffic for the used ports => using [THIS](https://github.com/ansibleguy/linux_ufw) role

## Config

The prefix 'wgs_' will be prepended for interfaces of the topology 'single'.

This prefix and much more can be changed as provided.

```yaml
# to reference networks
site_networks:
  nl: '192.168.30.0/24'
  de: '192.168.40.0/24'
  at: '192.168.70.0/24'

# vpn config
wireguard:
  restart_on_change: true
  support:
    traffic_forwarding: true

  topologies:
    nl2de:
      type: 'single'  # single => default type
      peers:
        srv03:
          Endpoint: 'srv03.wg.template.ansibleguy.net'
          Address: '10.100.0.1/30'
          PostUp: ["ip route add {{ site_networks.de }} dev %i metric 100"]

        srv04:
          Endpoint: 'srv04.wg.template.ansibleguy.net'
          Address: '10.100.0.2/30'
          PostUp: ["ip route add {{ site_networks.nl }} dev %i metric 10"]

    nl2at:
      NATed: true  # srv07 is behind a firewall
      peers:
        srv03:
          Endpoint: 'srv03.wg.template.ansibleguy.net'
          ListenPort: 51821  # srv03 already uses the default port for the nl2de connection
          Address: '10.100.0.5/30'
          AllowedIPs: ["{{ site_networks.nl }}"]

        srv07:
          Address: '10.100.0.6/30'
          ListenPort: ''  # does not need to listen on any port
          Route: true  # auto-add routes to peer 'AllowedIPs'
          AllowedIPs: ["{{ site_networks.at }}"]
```

## Result

### Controller

```bash
guy@ansible:~# ls -l roles/ansibleguy.infra_wireguard/files/keys/
> -rw-r----- nl2at.psk
> -rw-r----- nl2at_srv03.key
> -rw-r--r-- nl2at_srv03.pub
> -rw-r----- nl2at_srv07.key
> -rw-r--r-- nl2at_srv07.pub
> -rw-r----- nl2de.psk
> -rw-r----- nl2de_srv03.key
> -rw-r--r-- nl2de_srv03.pub
> -rw-r----- nl2de_srv04.key
> -rw-r--r-- nl2de_srv04.pub
```

You might want to use 'ansible-vault' to encrypt the private keys:
```bash
ansible-vault encrypt roles/ansibleguy.infra_wireguard/files/keys/some_file.key
```

### SRV03 (two connections)

```bash
# status
guy@srv03:~# wg show all
> interface: wgs_nl2at
>   public key: oqSWbjmFmA/YL+mMxABXERinS+EP/zLwvNQ8bBNnbDY=
>   private key: (hidden)
>   listening port: 51821
> 
> peer: CyKlu3qdIQDePC48PIpn3LQBukUCy7EPMZ5fkfgfnzI=
>   preshared key: (hidden)
>   endpoint: IP:36336
>   allowed ips: 10.100.0.6/32, 192.168.70.0/24
>   latest handshake: 1 minute, 42 seconds ago
>   transfer: 1.88 KiB received, 748 B sent
>   persistent keepalive: every 25 seconds
> 
> interface: wgs_nl2de
>   public key: bUeQ1vZSzwRubjghV1tzVaFgh7kEls6hgG0O9IHKXwM=
>   private key: (hidden)
>   listening port: 51820
> 
> peer: V0WLyIRRHSCTOe8+POwsIUOlvxEfECoK1uqSPcenbH0=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.100.0.2/32, 0.0.0.0/0, ::/0
>   latest handshake: 4 minutes, 56 seconds ago
>   transfer: 52.95 KiB received, 52.61 KiB sent

guy@srv03:~# systemctl status wg-quick@wgs_nl2at.service 
> ● wg-quick@wgs_nl2at.service - WireGuard via wg-quick(8) for wgs_nl2at
>      Loaded: loaded (/lib/systemd/system/wg-quick@.service; enabled; vendor preset: enabled)
>     Drop-In: /etc/systemd/system/wg-quick@.service.d
>              └─override.conf
>      Active: active (exited) since Sat 2022-01-29 21:27:35 CET; 14min ago
>        Docs: man:wg-quick(8)
>              man:wg(8)
>              https://www.wireguard.com/
>              https://www.wireguard.com/quickstart/
>              https://git.zx2c4.com/wireguard-tools/about/src/man/wg-quick.8
>              https://git.zx2c4.com/wireguard-tools/about/src/man/wg.8
>              https://github.com/ansibleguy/infra_wireguard

guy@srv03:~# systemctl status wg-quick@wgs_nl2de.service 
> ● wg-quick@wgs_nl2de.service - WireGuard via wg-quick(8) for wgs_nl2de
>      Loaded: loaded (/lib/systemd/system/wg-quick@.service; enabled; vendor preset: enabled)
>     Drop-In: /etc/systemd/system/wg-quick@.service.d
>              └─override.conf
>      Active: active (exited) since Sat 2022-01-29 21:28:14 CET; 14min ago
>        Docs: man:wg-quick(8)
>              man:wg(8)
>              https://www.wireguard.com/
>              https://www.wireguard.com/quickstart/
>              https://git.zx2c4.com/wireguard-tools/about/src/man/wg-quick.8
>              https://git.zx2c4.com/wireguard-tools/about/src/man/wg.8
>              https://github.com/ansibleguy/infra_wireguard

# config
guy@srv03:~# ls -l /etc/wireguard/
> drwxr-xr-x 2 root root 4096 Jan 29 21:25 keys
> -rw-r----- 1 root root  430 Jan 29 21:27 wgs_nl2at.conf
> -rw-r----- 1 root root  497 Jan 29 21:28 wgs_nl2de.conf


guy@srv03:~# cat /etc/wireguard/wgs_nl2at.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: single
> 
> [Interface]
> Address = 10.100.0.5/30
> ListenPort = 51821
> PostUp = wg set %i private-key /etc/wireguard/keys/nl2at_srv03.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> 
> [Peer]
> PublicKey = CyKlu3qdIQDePC48PIpn3LQBukUCy7EPMZ5fkfgfnzI=
> PresharedKey = AHKseTdvRB/Uyf+KleIR3JsnqTjV2Ggx3w41nvnqn+Q=
> AllowedIPs = 10.100.0.6/32, 192.168.70.0/24
> PersistentKeepalive = 25

guy@srv03:~# cat /etc/wireguard/wgs_nl2de.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: single
> 
> [Interface]
> Address = 10.100.0.1/30
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/nl2de_srv03.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> PostUp = ip route add 192.168.40.0/24 dev %i metric 100
> 
> [Peer]
> PublicKey = V0WLyIRRHSCTOe8+POwsIUOlvxEfECoK1uqSPcenbH0=
> PresharedKey = lhPeuFqJ1w4L14DnoDXFi9IrcrnZ8RZCYwhsYDDMEJ8=
> AllowedIPs = 10.100.0.2/32, 0.0.0.0/0, ::/0
> Endpoint = srv04.wg.template.ansibleguy.net:51820

# interfaces & routing
guy@srv03:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.100.0.0      0.0.0.0         255.255.255.252 U     0      0        0 wgs_nl2de
> 10.100.0.4      0.0.0.0         255.255.255.252 U     0      0        0 wgs_nl2at
> 192.168.40.0    0.0.0.0         255.255.255.0   U     100    0        0 wgs_nl2de

guy@srv03:~# ip a
# prettyfied
> 12: wgs_nl2at: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.0.5/30 scope global wgs_nl2at
> 13: wgs_nl2de: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.0.1/30 scope global wgs_nl2de
```

### SRV04
```bash
# status
guy@srv04:~# wg show all
> interface: wgs_nl2de
>   public key: V0WLyIRRHSCTOe8+POwsIUOlvxEfECoK1uqSPcenbH0=
>   private key: (hidden)
>   listening port: 51820
> 
> peer: bUeQ1vZSzwRubjghV1tzVaFgh7kEls6hgG0O9IHKXwM=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.100.0.1/32, 0.0.0.0/0, ::/0
>   latest handshake: 5 minutes, 40 seconds ago
>   transfer: 52.61 KiB received, 52.95 KiB sent

# config
guy@srv04:~# ls -l /etc/wireguard/
> drwxr-xr-x 2 root root 4096 Jan 29 15:36 keys
> -rw-r----- 1 root root  497 Jan 29 15:36 wgs_nl2de.conf

guy@srv04:~# cat /etc/wireguard/nl2de.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: single
> 
> [Interface]
> Address = 10.100.0.2/30
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/nl2de_srv04.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> PostUp = ip route add 192.168.30.0/24 dev %i metric 10
> 
> [Peer]
> PublicKey = bUeQ1vZSzwRubjghV1tzVaFgh7kEls6hgG0O9IHKXwM=
> PresharedKey = lhPeuFqJ1w4L14DnoDXFi9IrcrnZ8RZCYwhsYDDMEJ8=
> AllowedIPs = 10.100.0.1/32, 0.0.0.0/0, ::/0
> Endpoint = srv03.wg.template.ansibleguy.net:51820

# interfaces & routing
guy@srv04:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.100.0.0      0.0.0.0         255.255.255.252 U     0      0        0 wgs_nl2de
> 192.168.30.0    0.0.0.0         255.255.255.0   U     10     0        0 wgs_nl2de

guy@srv04:~# ip a
# prettyfied
> 19: wgs_nl2de: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.0.2/30 scope global wgs_nl2de
```

### SRV07
```bash
# status
guy@srv07:~# wg show all
> interface: wgs_nl2at
>   public key: CyKlu3qdIQDePC48PIpn3LQBukUCy7EPMZ5fkfgfnzI=
>   private key: (hidden)
>   listening port: 38876
> 
> peer: oqSWbjmFmA/YL+mMxABXERinS+EP/zLwvNQ8bBNnbDY=
>   preshared key: (hidden)
>   endpoint: IP:51821
>   allowed ips: 10.100.0.5/32, 192.168.30.0/24
>   latest handshake: 1 minute, 30 seconds ago
>   transfer: 932 B received, 2.54 KiB sent
>   persistent keepalive: every 25 seconds

# config
guy@srv07:~# ls -l /etc/wireguard/
> drwxr-xr-x 2 root root 4096 Jan 29 14:52 keys
> -rw-r----- 1 root root  449 Jan 29 16:25 wgs_nl2at.conf

guy@srv07:~# cat /etc/wireguard/nl2at.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: single
> 
> [Interface]
> Address = 10.100.0.6/30
> PostUp = wg set %i private-key /etc/wireguard/keys/nl2at_srv07.key
> MTU = 1500
> Table = 1000
> PostUp = if ! ip rule show | grep -q '1000';then ip rule add to all lookup 1000;fi
> DNS = 1.1.1.1, 8.8.8.8
> 
> [Peer]
> PublicKey = oqSWbjmFmA/YL+mMxABXERinS+EP/zLwvNQ8bBNnbDY=
> PresharedKey = AHKseTdvRB/Uyf+KleIR3JsnqTjV2Ggx3w41nvnqn+Q=
> AllowedIPs = 10.100.0.5/32, 192.168.30.0/24
> Endpoint = srv03.wg.template.ansibleguy.net:51821
> PersistentKeepalive = 25

# interfaces & routing
guy@srv07:~# ip route show table all | grep -vE '^(broadcast|local)\s'
# prettyfied
> 10.100.0.5 dev nl2at table 1000 scope link 
> 192.168.30.0/24 dev nl2at table 1000 scope link 
> 10.100.0.4/30 dev nl2at proto kernel scope link src 10.100.0.6

guy@srv07:~# ip a
# prettyfied
> 20: wgs_nl2at: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
>     inet 10.100.0.6/30 scope global wgs_nl2at

```
