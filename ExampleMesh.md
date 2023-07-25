# WireGuard Example - Topology 'Mesh'

## Off-Screen

This was done before running this example:

* Basic host-setup => using [THIS](https://github.com/ansibleguy/linux_bootstrap) role
* Network-interfaces and -capabilities => using [THIS](https://github.com/ansibleguy/linux_networking) role
* Allowing traffic for the used ports => using [THIS](https://github.com/ansibleguy/linux_ufw) role

## Config

Every node will connect to every other node.

You have to mind some cases when you configure a mesh-topology:

* We strongly recommend enabling auto-routing for this topology! Else the routing gets messy pretty fast.

  * Background info: the build-in auto-added routes will not work for this kind of connection as the gateway is not set. 
  
    Therefore, we have implemented a replacement for these. See below for results.

* **AllowedIPs MUST BE SET** for this topology-type!

* Auto-added routes depend on correctly configured 'AllowedIPs'.

  The default value (_0.0.0.0/0 & ::/0_) will not work for multiple peers at once.

A single tunnel interface is used to connect to all peers.

The prefix 'wgm_' will be prepended for interfaces of the topology 'mesh'.

This prefix and much more can be changed as provided.

```yaml
wireguard:
  restart_on_change: true
  support:
    traffic_forwarding: true

  topologies:
    dcs:
      type: 'mesh'
      Route: true
      peers:
        aws:
          Endpoint: 'dc1.wg.template.ansibleguy.net'
          Address: '10.0.3.1/24'
          AllowedIPs: '172.16.31.0/24'  # can be list or single element
        hetzner:
          Endpoint: 'dc2.wg.template.ansibleguy.net'
          Address: '10.0.3.2/24'
          AllowedIPs: '172.16.32.0/24'
        rando:
          NATed: true
          ListenPort: ''  # does not need to listen on any port
          Address: '10.0.3.3/24'
          AllowedIPs: '172.16.33.0/24'

```

## Result

### Controller

```bash
guy@ansible:~# ls -l roles/ansibleguy.infra_wireguard/files/keys/
> -rw-r----- dcs.psk
> -rw-r----- dcs_aws.key
> -rw-r--r-- dcs_aws.pub
> -rw-r----- dcs_hetzner.key
> -rw-r--r-- dcs_hetzner.pub
> -rw-r----- dcs_rando.key
> -rw-r--r-- dcs_rando.pub
```

You might want to use 'ansible-vault' to encrypt the private keys:
```bash
ansible-vault encrypt roles/ansibleguy.infra_wireguard/files/keys/some_file.key
```

### AWS

```bash
# status
guy@aws:~# wg show all
interface: wgm_dcs
  public key: X4wfjxxYKKxumKp9OuvjMP9R0/fa4Q6QRwcpzn2qPxk=
  private key: (hidden)
  listening port: 51820

peer: FRfiUjNUcNN3f4eyq5Fx0XQIIfC4nTMPLWsXBDsOqEQ=
  preshared key: (hidden)
  endpoint: IP:51820
  allowed ips: 10.0.3.3/32, 172.30.33.0/24
  latest handshake: 1 minute, 1 second ago
  transfer: 1.43 KiB received, 1.82 KiB sent
  persistent keepalive: every 25 seconds

peer: MAinYYgddfr6qK8+zjG8tUUI+TqJmcxTMpM0bVrn0Bk=
  preshared key: (hidden)
  endpoint: IP:51820
  allowed ips: 10.0.3.2/32, 172.30.32.0/24
  latest handshake: 2 minutes, 55 seconds ago
  transfer: 220 B received, 308 B sent

systemctl status wg-quick@*
* wg-quick@wgm_dcs.service - WireGuard via wg-quick(8) for wgm_dcs
     Loaded: loaded (/lib/systemd/system/wg-quick@.service; enabled; vendor preset: enabled)
    Drop-In: /etc/systemd/system/wg-quick@.service.d
             `-override.conf
     Active: active (exited) since Mon 2022-02-07 22:39:34 UTC; 4min 26s ago
       Docs: man:wg-quick(8)
             man:wg(8)
             https://www.wireguard.com/
             https://www.wireguard.com/quickstart/
             https://git.zx2c4.com/wireguard-tools/about/src/man/wg-quick.8
             https://git.zx2c4.com/wireguard-tools/about/src/man/wg.8
             https://github.com/ansibleguy/infra_wireguard

# config
guy@aws:~# cat /etc/wireguard/wgm_dcs.conf 
> # Ansible managed
> # ansibleguy.infra_wireguard
> 
> # topology: mesh
> 
> [Interface]
> Address = 10.0.3.1/24
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/dcs_aws.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> 
> # auto-routes
> PostUp = ip route add 172.30.32.0/24 dev %i metric 101 via 10.0.3.2
> PostUp = ip route add 172.30.33.0/24 dev %i metric 101 via 10.0.3.3
> 
> [Peer]
> # hetzner
> PublicKey = MAinYYgddfr6qK8+zjG8tUUI+TqJmcxTMpM0bVrn0Bk=
> PresharedKey = MofuLHjqLMXJuJlu7xuQO5vb1cmFe/8rj/pllrSQKkI=
> AllowedIPs = 10.0.3.2/32, 172.30.32.0/24
> Endpoint = dc2.wg.template.ansibleguy.net:51820
> 
> [Peer]
> # rando
> PublicKey = FRfiUjNUcNN3f4eyq5Fx0XQIIfC4nTMPLWsXBDsOqEQ=
> PresharedKey = MofuLHjqLMXJuJlu7xuQO5vb1cmFe/8rj/pllrSQKkI=
> AllowedIPs = 10.0.3.3/32, 172.30.33.0/24
> PersistentKeepalive = 25

guy@aws:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.0.3.0        0.0.0.0         255.255.255.0   U     0      0        0 wgm_dcs
> 172.30.31.0     0.0.0.0         255.255.255.0   U     0      0        0 eth1
> 172.30.32.0     10.0.3.2        255.255.255.0   UG    101    0        0 wgm_dcs
> 172.30.33.0     10.0.3.3        255.255.255.0   UG    101    0        0 wgm_dcs
```

### Hetzner

```bash
# status
guy@hetzner:~# wg show all
> interface: wgm_dcs
>   public key: MAinYYgddfr6qK8+zjG8tUUI+TqJmcxTMpM0bVrn0Bk=
>   private key: (hidden)
>   listening port: 51820
> 
> peer: X4wfjxxYKKxumKp9OuvjMP9R0/fa4Q6QRwcpzn2qPxk=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.0.3.1/32, 172.30.31.0/24
>   latest handshake: 9 minutes, 12 seconds ago
>   transfer: 308 B received, 220 B sent
> 
> peer: FRfiUjNUcNN3f4eyq5Fx0XQIIfC4nTMPLWsXBDsOqEQ=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.0.3.3/32, 172.30.33.0/24
>   persistent keepalive: every 25 seconds

# config
guy@hetzner:~# cat /etc/wireguard/wgm_dcs.conf 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_wireguard
> 
> # topology: mesh
> 
> [Interface]
> Address = 10.0.3.2/24
> ListenPort = 51820
> PostUp = wg set %i private-key /etc/wireguard/keys/tm1_hetzner.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> 
> # auto-routes
> PostUp = ip route add 172.30.31.0/24 dev %i metric 101 via 10.0.3.1
> PostUp = ip route add 172.30.33.0/24 dev %i metric 101 via 10.0.3.3
> 
> [Peer]
> # aws
> PublicKey = X4wfjxxYKKxumKp9OuvjMP9R0/fa4Q6QRwcpzn2qPxk=
> PresharedKey = MofuLHjqLMXJuJlu7xuQO5vb1cmFe/8rj/pllrSQKkI=
> AllowedIPs = 10.0.3.1/32, 172.30.31.0/24
> Endpoint = dc1.wg.template.ansibleguy.net:51820
> 
> [Peer]
> # rando
> PublicKey = FRfiUjNUcNN3f4eyq5Fx0XQIIfC4nTMPLWsXBDsOqEQ=
> PresharedKey = MofuLHjqLMXJuJlu7xuQO5vb1cmFe/8rj/pllrSQKkI=
> AllowedIPs = 10.0.3.3/32, 172.30.33.0/24
> PersistentKeepalive = 25

guy@hetzner:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.0.3.0        0.0.0.0         255.255.255.0   U     0      0        0 wgm_dcs
> 172.30.31.0     10.0.3.1        255.255.255.0   UG    101    0        0 wgm_dcs
> 172.30.32.0     0.0.0.0         255.255.255.0   U     0      0        0 eth1
> 172.30.33.0     10.0.3.3        255.255.255.0   UG    101    0        0 wgm_dcs
```

### Rando

```bash
# status
guy@rando:~# wg show all
> interface: wgm_dcs
>   public key: FRfiUjNUcNN3f4eyq5Fx0XQIIfC4nTMPLWsXBDsOqEQ=
>   private key: (hidden)
>   listening port: 53336
> 
> peer: X4wfjxxYKKxumKp9OuvjMP9R0/fa4Q6QRwcpzn2qPxk=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.0.3.1/32, 172.30.31.0/24
>   latest handshake: 10 seconds ago
>   transfer: 308 B received, 220 B sent
> 
> peer: MAinYYgddfr6qK8+zjG8tUUI+TqJmcxTMpM0bVrn0Bk=
>   preshared key: (hidden)
>   endpoint: IP:51820
>   allowed ips: 10.0.3.2/32, 172.30.32.0/24
>   latest handshake: 23 seconds ago
>   transfer: 8.58 KiB received, 8.46 KiB sent

# config
guy@rando:~# cat /etc/wireguard/wgm_dcs.conf 
> # Ansible managed: Do NOT edit this file manually!
> # ansibleguy.infra_wireguard
> 
> # topology: mesh
> 
> [Interface]
> Address = 10.0.3.3/24
> PostUp = wg set %i private-key /etc/wireguard/keys/tm1_rando.key
> MTU = 1500
> Table = off
> DNS = 1.1.1.1, 8.8.8.8
> 
> # auto-routes
> PostUp = ip route add 172.30.31.0/24 dev %i metric 101 via 10.0.3.1
> PostUp = ip route add 172.30.32.0/24 dev %i metric 101 via 10.0.3.2
>
> # get dynamic endpoint to re-/connect
> PostUp = /bin/bash -c "while sleep 30 ; do ping -c4 10.0.3.1 > /dev/null 2>&1 ; done &"
> PostUp = /bin/bash -c "while sleep 30 ; do ping -c4 10.0.3.2 > /dev/null 2>&1 ; done &"
>
> [Peer]
> # aws
> PublicKey = X4wfjxxYKKxumKp9OuvjMP9R0/fa4Q6QRwcpzn2qPxk=
> PresharedKey = MofuLHjqLMXJuJlu7xuQO5vb1cmFe/8rj/pllrSQKkI=
> AllowedIPs = 10.0.3.1/32, 172.30.31.0/24
> Endpoint = dc1.wg.template.ansibleguy.net:51820
> 
> [Peer]
> # hetzner
> PublicKey = MAinYYgddfr6qK8+zjG8tUUI+TqJmcxTMpM0bVrn0Bk=
> PresharedKey = MofuLHjqLMXJuJlu7xuQO5vb1cmFe/8rj/pllrSQKkI=
> AllowedIPs = 10.0.3.2/32, 172.30.32.0/24
> Endpoint = dc2.wg.template.ansibleguy.net:51820

guy@rando:~# route -n
> Kernel IP routing table
> Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
> 0.0.0.0         GW              0.0.0.0         UG    0      0        0 eth0
> 10.0.3.0        0.0.0.0         255.255.255.0   U     0      0        0 wgm_dcs
> 172.30.31.0     10.0.3.1        255.255.255.0   UG    101    0        0 wgm_dcs
> 172.30.32.0     10.0.3.2        255.255.255.0   UG    101    0        0 wgm_dcs
> 172.30.33.0     0.0.0.0         255.255.255.0   U     0      0        0 eth1
```
