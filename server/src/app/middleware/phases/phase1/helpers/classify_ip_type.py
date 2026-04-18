from dataclasses import dataclass
import ipaddress

@dataclass(slots=True, frozen=True)
class IPClassification:
    normalized: str
    ip_type: str
    net_48: str
    net_32: str

def classify_ip_type(ip: str) -> IPClassification:
    try:
        addr = ipaddress.ip_address(ip)
        if isinstance(addr, ipaddress.IPv6Address):
            return IPClassification(
                normalized=str(ipaddress.IPv6Network(f"{ip}/64", strict=False).network_address),
                ip_type="ipv6",
                net_48=str(ipaddress.IPv6Network(f"{ip}/48", strict=False).network_address),
                net_32=str(ipaddress.IPv6Network(f"{ip}/32", strict=False).network_address),
            )
        return IPClassification(normalized=ip, ip_type="ipv4", net_48="", net_32="")
    except ValueError:
        return IPClassification(normalized=ip, ip_type="unknown", net_48="", net_32="")