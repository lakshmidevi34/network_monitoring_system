# import ollama

# def generate_response(question, stats):

#     system_prompt = f"""
# You are an AI cybersecurity assistant.

# Network Stats:
# Total Packets: {stats.get("total_packets")}
# Packets/sec: {stats.get("packets_per_second")}

# TCP: {stats.get("tcp")}
# UDP: {stats.get("udp")}
# ICMP: {stats.get("icmp")}
# ARP: {stats.get("arp")}
# DNS: {stats.get("dns")}

# Top IPs: {stats.get("top_ips")}
# Top Ports: {stats.get("top_ports")}

# Alerts: {stats.get("alerts")}
# Attackers: {stats.get("attackers")}

# Explain clearly and simply.
# """

#     try:
#         response = ollama.chat(
#             model="phi",   # 🔥 IMPORTANT
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": question}
#             ]
#         )

#         return response["message"]["content"]

#     except Exception as e:
#         return f"Chatbot error: {str(e)}"

import ollama

def generate_response(question, stats):

    try:
        response = ollama.chat(
            model="phi",
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity assistant. Answer clearly."
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response.get("message", {}).get("content", "No response")

    except Exception as e:
        print("CHATBOT ERROR:", e)   # 🔥 IMPORTANT (see error in terminal)
        return "Chatbot is currently unavailable."