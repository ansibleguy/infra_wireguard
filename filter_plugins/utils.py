from re import sub as regex_replace
from netaddr import IPNetwork


class FilterModule(object):

    def filters(self):
        return {
            "safe_wg_name": self.safe_wg_name,
        }

    @staticmethod
    def safe_wg_name(key: str) -> str:
        name = regex_replace('[^a-zA-Z0-9_=+.-]', '', key.replace(' ', '_'))
        return name[:15]

    @staticmethod
    def get_ip_by_id(nw_cidr: str, nw_id: int, gw: bool = False, gw_range: int = 1) -> str:
        # pulls the Nth ip of the configured network(-range)
        network = IPNetwork(nw_cidr)
        ip_range = [ip for ip in network.iter_hosts()]
        if gw:
            for i in range(gw_range):
                # the first N ips will always be used for the center point/gateway
                ip_range.pop(i)

        if nw_id > len(ip_range):
            raise ValueError(f"Cannot use a network-id '{nw_id}' that is out of range for the configured network '{nw_cidr}'!"
                             f"Available ids: 1-{len(ip_range)}")

        return str(ip_range[nw_id])
