"""Computer-networking knowledge base, distilled from the handwritten
networking notes Darion supplied (7 pages, @i.lovecoding on Instagram).

Every entry: id, title, body, tags. This is the RAG corpus, the tutor's
textbook, and the tiny SLM's training text — all offline, all local.
"""

ENTRIES = [
    {
        "id": "what-is-networking",
        "title": "What is computer networking?",
        "body": "Computer networking is the process of connecting computers and other devices together so they can communicate, share resources and exchange data with each other. It allows devices to work together over a network, either small like a home network or large like the internet.",
        "tags": ["basics", "definition"],
    },
    {
        "id": "network-types-by-size",
        "title": "Types of networks by size (PAN, LAN, MAN, WAN)",
        "body": "Networks are classified by size and scope. PAN - Personal Area Network, e.g. Bluetooth or a phone hotspot. LAN - Local Area Network, e.g. home, office or school. MAN - Metropolitan Area Network, e.g. city wide. WAN - Wide Area Network, e.g. countries or the internet. Larger networks cover bigger areas: PAN inside LAN inside MAN inside WAN.",
        "tags": ["pan", "lan", "man", "wan", "types"],
    },
    {
        "id": "network-kinds",
        "title": "Wired, wireless and VPN networks",
        "body": "A wired network uses cables (Ethernet). A wireless network uses radio waves (WiFi). A VPN creates a secure connection over the internet.",
        "tags": ["wired", "wireless", "vpn", "types"],
    },
    {
        "id": "devices-overview",
        "title": "Key devices in a network",
        "body": "Router - connects different networks and routes data; example: home router or ISP router. Switch - connects devices within the same network; example: a 24-port switch. Hub - sends data to all devices (broadcasts), an old network hub, less common now. Modem - connects your local network or home network to the ISP (the internet); example: cable modem. Access Point - provides wireless network (WiFi) access to devices; example: WiFi router. Repeater - extends WiFi range; example: WiFi extender.",
        "tags": ["router", "switch", "hub", "modem", "access point", "repeater", "devices"],
    },
    {
        "id": "router",
        "title": "Router",
        "body": "A router connects different networks and routes data between them. It works at the network layer (Layer 3) and uses IP addresses. Examples: home router, ISP router. Routing protocols include RIP, OSPF and BGP.",
        "tags": ["router", "devices", "layer 3", "ip"],
    },
    {
        "id": "switch",
        "title": "Switch",
        "body": "A switch connects devices in the same network and forwards data to the right device. It works at the data link layer (Layer 2) and uses MAC addresses. Example: a 24-port switch. Switching features include VLAN and STP.",
        "tags": ["switch", "devices", "layer 2", "mac", "vlan"],
    },
    {
        "id": "topologies",
        "title": "Network topologies (bus, star, ring, mesh, tree)",
        "body": "Network topology is the arrangement of devices in a network. Bus - all devices share one main cable. Star - all devices connect to a central device. Ring - devices are connected in a circle. Mesh - devices connect to many other devices. Tree - hierarchical connection, like a tree.",
        "tags": ["bus", "star", "ring", "mesh", "tree", "topology"],
    },
    {
        "id": "ip-addressing",
        "title": "IP addressing (IPv4, IPv6, public, private)",
        "body": "An IP address is a unique number given to each device on a network. IPv4 is a 32-bit address, e.g. 192.168.1.1. IPv6 is a 128-bit address, e.g. 2001:0db8::1. IP addresses can be public (used on the internet) or private (used in local networks). Private IPv4 ranges: 10.0.0.0 - 10.255.255.255, 172.16.0.0 - 172.31.255.255, 192.168.0.0 - 192.168.255.255. Loopback (IPv4) is 127.0.0.1. The public IPv4 range is roughly 1.0.0.0 - 223.255.255.255 excluding private ranges.",
        "tags": ["ip", "ipv4", "ipv6", "private", "public", "addressing"],
    },
    {
        "id": "ip-classes",
        "title": "IP address classes A-E",
        "body": "IP addresses are divided into classes to make address management easier. Class A: first octet 1-126, default subnet mask 255.0.0.0, used for large networks. Class B: 128-191, mask 255.255.0.0, medium networks. Class C: 192-223, mask 255.255.255.0, small networks. Class D: 224-239, no default mask, multicast. Class E: 240-255, experimental.",
        "tags": ["class a", "class b", "class c", "class d", "class e", "subnet mask", "ip"],
    },
    {
        "id": "protocols",
        "title": "Network protocols (TCP, UDP, HTTP, HTTPS, FTP)",
        "body": "Protocols are rules that control how data is sent, received and understood. TCP - reliable, connection-oriented (e.g. web, email). UDP - faster, connectionless (e.g. video streaming, online games). HTTP - transfers web pages. HTTPS - secure version of HTTP, uses encryption. FTP - transfers files over a network. DNS resolves domain names and IP forwards packets at the internet layer, ICMP reports errors.",
        "tags": ["tcp", "udp", "http", "https", "ftp", "dns", "icmp", "protocols"],
    },
    {
        "id": "osi-model",
        "title": "OSI model (7 layers)",
        "body": "The OSI model is a 7-layer theoretical framework used to understand how data moves over a network: 7 Application, 6 Presentation, 5 Session, 4 Transport, 3 Network, 2 Data Link, 1 Physical. The TCP/IP model is the practical 4-layer model widely used on the internet; OSI helps in understanding network concepts.",
        "tags": ["osi", "layers", "model"],
    },
    {
        "id": "tcpip-model",
        "title": "TCP/IP model (4 layers)",
        "body": "The TCP/IP model has 4 layers, each with a specific function. Layer 4 Application - provides network services to applications; examples HTTP, FTP, DNS. Layer 3 Transport - handles data delivery and reliability; examples TCP, UDP. Layer 2 Internet - handles routing and addressing; examples IP, ICMP. Layer 1 Network Access - manages the physical connection and data link; examples Ethernet, WiFi. The TCP/IP model is a practical model, while the OSI model has 7 layers.",
        "tags": ["tcp/ip", "layers", "model", "application", "transport", "internet", "network access"],
    },
    {
        "id": "routing-vs-switching",
        "title": "Differences between routing and switching",
        "body": "Routing works at the network layer (Layer 3), connects different networks, uses a router, uses IP addresses; examples RIP, OSPF, BGP. Switching works at the data link layer (Layer 2), connects devices in the same network, uses a switch, uses MAC addresses; examples VLAN, STP.",
        "tags": ["routing", "switching", "layer 3", "layer 2"],
    },
    {
        "id": "cables-connectors",
        "title": "Network cables and connectors",
        "body": "Network cables are used to connect devices in a network. Twisted Pair - used in LAN, e.g. Cat5e and Cat6, connector RJ45 (Ethernet). Coaxial - used in older networks (less common), connector BNC. Fiber Optic - used for high speed and long distance, connector SC.",
        "tags": ["cables", "cat5e", "cat6", "coaxial", "fiber", "rj45", "connectors"],
    },
    {
        "id": "firewall-types",
        "title": "Firewall types",
        "body": "A firewall is a security device or software that monitors and controls incoming and outgoing network traffic based on security rules. Packet Filtering - filters data based on IP, port and protocol. Stateful Inspection - tracks connection state. Next-Generation Firewall (NGFW) - deep packet inspection with advanced security features. Proxy Firewall - acts as an intermediary between networks.",
        "tags": ["firewall", "security", "packet filtering", "stateful", "ngfw", "proxy"],
    },
    {
        "id": "network-security",
        "title": "Network security types",
        "body": "Network security protects data and devices from threats and unauthorized access, and can be achieved using different types of methods and tools. Firewall - blocks unauthorized access (blocks unwanted traffic). Antivirus - detects and removes malware. Encryption - protects data by converting it to code (keeps data safe, e.g. HTTPS). VPN - creates a secure connection (a secure tunnel) over the internet. IDS/IPS - detects and prevents attacks.",
        "tags": ["security", "firewall", "antivirus", "encryption", "vpn", "ids", "ips"],
    },
    {
        "id": "bandwidth",
        "title": "Network bandwidth",
        "body": "Bandwidth is the amount of data that can be transmitted over a network in a given time. It is measured in bps (bits per second); common units are Kbps, Mbps and Gbps. Higher bandwidth means faster data transfer, lower bandwidth means slower data transfer. Comparison: dial-up about 56 Kbps, broadband about 10 Mbps, fiber optic about 1 Gbps.",
        "tags": ["bandwidth", "bps", "mbps", "gbps", "speed"],
    },
    {
        "id": "commands",
        "title": "Common network commands",
        "body": "These commands are used to troubleshoot and manage networks. ping - checks if a device is reachable. ipconfig - shows IP configuration (Windows). ifconfig - shows IP configuration (Linux). tracert - shows the route to a destination. netstat - shows active connections. nslookup - looks up domain names. arp - shows the ARP table. route - shows the routing table.",
        "tags": ["ping", "ipconfig", "ifconfig", "tracert", "netstat", "nslookup", "arp", "route", "commands"],
    },
    {
        "id": "internet-services",
        "title": "Internet and its services",
        "body": "The internet is a global network of networks that connects millions of devices and provides many services. Web - access to websites, e.g. Google and YouTube. Email - send and receive messages. FTP - transfer files. Chat - real-time communication. Cloud - store data online, e.g. Google Drive.",
        "tags": ["internet", "web", "email", "cloud", "services"],
    },
    {
        "id": "data-flow-example",
        "title": "Example of data flow",
        "body": "An example of data flow inside a local network: a laptop sends data to a switch, the switch forwards it to a router, and the router sends it out to the internet. In a home setup the path is: device, modem, router, then the laptop, desktop and access point on the local side.",
        "tags": ["data flow", "example"],
    },
    {
        "id": "conclusion",
        "title": "Conclusion",
        "body": "Computer networking helps devices and people communicate, share resources and access information. It uses different devices, protocols and topologies to make the internet and local networks work efficiently. Stay connected, stay learning, keep coding.",
        "tags": ["conclusion", "summary"],
    },
]


def all_entries():
    return list(ENTRIES)


def entry_by_id(entry_id):
    for e in ENTRIES:
        if e["id"] == entry_id:
            return e
    return None


def corpus_text():
    """The full KB as one text — the SLM's training corpus."""
    return "\n".join(f"{e['title']}. {e['body']}" for e in ENTRIES)
