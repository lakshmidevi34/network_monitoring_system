from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, DNS
from collections import defaultdict
import time

# Packet counters
packet_count = 0
tcp_count = 0
udp_count = 0
icmp_count = 0
arp_count = 0
dns_count = 0

# Data collections
source_ip_count = defaultdict(int)
destination_ports = defaultdict(int)
packet_sizes = []

start_time = time.time()

def process_packet(packet):
    global packet_count, tcp_count, udp_count, icmp_count, arp_count, dns_count

    packet_count += 1

    packet_size = len(packet)
    packet_sizes.append(packet_size)

    protocol = "UNKNOWN"
    src = "N/A"
    dst = "N/A"
    port = None

    # ARP detection
    if packet.haslayer(ARP):
        arp_count += 1
        src = packet[ARP].psrc
        dst = packet[ARP].pdst
        protocol = "ARP"

    # IP packets
    elif packet.haslayer(IP):
        src = packet[IP].src
        dst = packet[IP].dst

        source_ip_count[src] += 1

        if packet.haslayer(TCP):
            tcp_count += 1
            protocol = "TCP"
            port = packet[TCP].dport

        elif packet.haslayer(UDP):
            udp_count += 1
            protocol = "UDP"
            port = packet[UDP].dport

        elif packet.haslayer(ICMP):
            icmp_count += 1
            protocol = "ICMP"

        if packet.haslayer(DNS):
            dns_count += 1

        if port:
            destination_ports[port] += 1

    else:
        return

    elapsed_time = time.time() - start_time
    packets_per_second = packet_count / elapsed_time if elapsed_time > 0 else 0

    print("\n==============================")
    print("Packet Number:", packet_count)
    print("Protocol:", protocol)
    print("Source IP:", src)
    print("Destination IP:", dst)
    print("Packet Size:", packet_size, "bytes")

    if port:
        print("Destination Port:", port)

    print("\n--- Protocol Statistics ---")
    print("TCP:", tcp_count)
    print("UDP:", udp_count)
    print("ICMP:", icmp_count)
    print("ARP:", arp_count)
    print("DNS:", dns_count)

    print("\n--- Traffic Metrics ---")
    print("Packets per second:", round(packets_per_second,2))

    print("\n--- Top Source IPs ---")
    top_ips = sorted(source_ip_count.items(), key=lambda x: x[1], reverse=True)[:5]
    for ip, count in top_ips:
        print(ip, "->", count, "packets")

    print("\n--- Top Destination Ports ---")
    top_ports = sorted(destination_ports.items(), key=lambda x: x[1], reverse=True)[:5]
    for p, count in top_ports:
        print("Port", p, "->", count, "packets")

    print("==============================")

print("Starting Advanced Network Monitoring...\n")

sniff(prn=process_packet, store=False)