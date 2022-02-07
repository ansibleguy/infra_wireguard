from re import sub as regex_replace


class FilterModule(object):

    def filters(self):
        return {
            "safe_int_name": self.safe_int_name,
            "ensure_list": self.ensure_list,
            "flatten_hosts": self.flatten_hosts,
            "flatten_ints": self.flatten_ints,
            "one_center": self.one_center,
            "star_edge_peers": self.star_edge_peers,
            "mesh_peers": self.mesh_peers,
        }

    @staticmethod
    def safe_int_name(key: str) -> str:
        return regex_replace('[^a-zA-Z0-9_=+.-]', '', key.replace(' ', '_'))[:15]

    @staticmethod
    def flatten_hosts(topologies: dict) -> list:
        hosts = []

        for v in topologies.values():
            hosts.extend([peer for peer in v['peers'].keys()])

        return hosts

    @classmethod
    def flatten_ints(cls, topologies: dict, current_host: str, int_prefixes: dict) -> list:
        # getting all interfaces that should be present on the host
        ints = []

        for k, v in topologies.items():
            if current_host in v['peers'].keys():
                if 'type' in v:
                    try:
                        ints.append(cls.safe_int_name(f"{int_prefixes[v['type']]}_{k}"))

                    except KeyError:
                        ints.append(cls.safe_int_name(f"{int_prefixes['single']}_{k}"))

                else:
                    ints.append(cls.safe_int_name(f"{int_prefixes['single']}_{k}"))

        return ints

    @staticmethod
    def one_center(peers: dict) -> bool:
        centers = 0

        for v in peers.values():
            if 'role' in v and v['role'] == 'center':
                centers += 1

        if centers == 1:
            return True

        return False

    @staticmethod
    def star_edge_peers(peers: dict) -> dict:
        edges = {}

        for k, v in peers.items():
            if 'role' not in v or v['role'] != 'center':
                edges[k] = v

        return edges

    @staticmethod
    def mesh_peers(all_peers: dict, this_host: str) -> dict:
        return {k: v for k, v in all_peers.items() if k != this_host}

    @staticmethod
    def ensure_list(data: (str, list)) -> list:
        # if user supplied a string instead of a list => convert it to match our expectations
        if type(data) == list:
            return data

        else:
            return [data]
