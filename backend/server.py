from ml_ids import add_packet_feature, detect_anomaly
from flask import Flask, jsonify, request
from flask_cors import CORS
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, DNS
from collections import defaultdict
import threading
import time
import requests
from chatbot import generate_response

app = Flask(__name__)
CORS(app)

# -----------------------------
# GLOBAL NETWORK STATS
# -----------------------------
stats = {
    "total_packets": 0,
    "tcp": 0,
    "udp": 0,
    "icmp": 0,
    "arp": 0,
    "dns": 0,
    "packets_per_second": 0,
    "top_ips": {},
    "top_ports": {},
    "alerts": [],
    "attackers": []
}

source_ips = defaultdict(int)
dest_ports = defaultdict(int)

start_time = time.time()


# -----------------------------
# GEO LOCATION FUNCTION
# -----------------------------
def get_location(ip):

    try:

        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)

        data = r.json()

        return {
            "ip": ip,
            "city": data.get("city", ""),
            "country": data.get("country", ""),
            "org": data.get("org", ""),
            "loc": data.get("loc", "")
        }

    except:
        return None


# -----------------------------
# PACKET PROCESSING
# -----------------------------
def process_packet(packet):

    stats["total_packets"] += 1

    packet_size = len(packet)
    protocol_id = 0
    port = 0
    src = "unknown"

    if packet.haslayer(IP):
        src = packet[IP].src

    # Protocol detection
    if packet.haslayer(TCP):
        protocol_id = 1
        port = packet[TCP].dport

    elif packet.haslayer(UDP):
        protocol_id = 2
        port = packet[UDP].dport

    elif packet.haslayer(ICMP):
        protocol_id = 3

    # Feed ML model
    add_packet_feature(packet_size, protocol_id, port)

    if detect_anomaly(packet_size, protocol_id, port):

        alert = {
            "message": f"AI anomaly detected from {src}",
            "severity": "HIGH"
        }

        if alert not in stats["alerts"]:
            stats["alerts"].append(alert)

    # ARP
    if packet.haslayer(ARP):
        stats["arp"] += 1

    if packet.haslayer(IP):

        source_ips[src] += 1

        if packet.haslayer(TCP):

            stats["tcp"] += 1
            port = packet[TCP].dport
            dest_ports[port] += 1

        elif packet.haslayer(UDP):

            stats["udp"] += 1
            port = packet[UDP].dport
            dest_ports[port] += 1

        elif packet.haslayer(ICMP):

            stats["icmp"] += 1

        if packet.haslayer(DNS):
            stats["dns"] += 1

        # DDoS detection rule
        if source_ips[src] > 200:

            alert = {
                "message": f"Possible DDoS from {src}",
                "severity": "MEDIUM"
            }

            if alert not in stats["alerts"]:

                stats["alerts"].append(alert)

                loc = get_location(src)

                if loc:
                    stats["attackers"].append(loc)

    # Top IPs
    stats["top_ips"] = dict(
        sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:5]
    )

    # Top Ports
    stats["top_ports"] = dict(
        sorted(dest_ports.items(), key=lambda x: x[1], reverse=True)[:5]
    )

    # Limit alerts
    if len(stats["alerts"]) > 20:
        stats["alerts"].pop(0)


# -----------------------------
# START PACKET SNIFFER
# -----------------------------
def start_sniffing():
    sniff(prn=process_packet, store=False)


# -----------------------------
# NETWORK STATS API
# -----------------------------
@app.route("/stats")
def get_stats():

    elapsed = time.time() - start_time

    pps = stats["total_packets"] / elapsed if elapsed > 0 else 0

    data = stats.copy()
    data["packets_per_second"] = round(pps, 2)

    return jsonify(data)


# -----------------------------
# CHATBOT API
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.json
        question = data.get("message")

        if not question:
            return jsonify({"reply": "No question provided"}), 400

        reply = generate_response(question, stats)

        return jsonify({"reply": reply})

    except Exception as e:
        print("SERVER ERROR:", e)  # 🔥 IMPORTANT
        return jsonify({"reply": "Server error occurred"}), 500


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":

    sniff_thread = threading.Thread(target=start_sniffing)
    sniff_thread.daemon = True
    sniff_thread.start()

    app.run(port=5000, debug=True)