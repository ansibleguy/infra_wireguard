from re import sub as regex_replace


class FilterModule(object):

    def filters(self):
        return {
            "safe_single_name": self.safe_single_name,
            "safe_star_name": self.safe_star_name,
            "ensure_list": self.ensure_list,
            "flatten_hosts": self.flatten_hosts,
        }

    @staticmethod
    def safe_linux_interface_name(key: str) -> str:
        return regex_replace('[^a-zA-Z0-9_=+.-]', '', key.replace(' ', '_'))[:15]

    @classmethod
    def safe_single_name(cls, key: str) -> str:
        return cls.safe_linux_interface_name(key)

    @classmethod
    def safe_star_name(cls, key: str) -> str:
        # allowing for id's to be appended
        return cls.safe_linux_interface_name(key)[:13]

    @staticmethod
    def flatten_hosts(topologies: dict) -> list:
        hosts = []

        for v in topologies.values():
            hosts.extend([peer for peer in v['peers'].keys()])

        return hosts

    # @staticmethod
    # def get_ip_by_id(nw_cidr: str, nw_id: int, gw_range: int, gw: bool = False) -> str:
    #     # pulls the Nth ip of the configured network(-range)
    #     network = IPNetwork(nw_cidr)
    #     ip_range = [ip for ip in network.iter_hosts()]
    #     if gw:
    #         for i in range(gw_range):
    #             # the first N ips will always be used for the center point/gateway
    #             ip_range.pop(0)
    #
    #     if nw_id > len(ip_range):
    #         raise ValueError(f"Cannot use a network-id '{nw_id}' that is out of range for the configured network '{nw_cidr}'!"
    #                          f"Available ids: 1-{len(ip_range)}")
    #
    #     return str(ip_range[nw_id])

    @staticmethod
    def ensure_list(data: (str, list)) -> list:
        # if user supplied a string instead of a list => convert it to match our expectations
        if type(data) == list:
            return data

        else:
            return [data]
