from flask import Flask, render_template, jsonify, request
import os
import platform
import socket
import time

app = Flask(__name__)

def get_network_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    net_info = {
        "Hostname": hostname,
        "IP Address": ip_address,
        "Gateway": os.popen("ipconfig" if platform.system() == "Windows" else "route -n").read(),
        "Subnet Mask": os.popen("ipconfig" if platform.system() == "Windows" else "ifconfig").read(),
    }
    return net_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/measure-latency')
def measure_latency():
    host = request.args.get('host', 'google.com')
    system = platform.system().lower()
    if 'windows' in system:
        command = f"ping -n 1 {host}"
    else:
        command = f"ping -c 1 {host}"
    result = os.popen(command).read()
    latency = result.split("time=")[-1].split("ms")[0] if "time=" in result else "N/A"
    return jsonify({"latency": latency})

@app.route('/measure-packet-loss')
def measure_packet_loss():
    host = request.args.get('host', 'google.com')
    try:
        system = platform.system().lower()
        if 'windows' in system:
            command = f"ping -n 4 {host}"
        else:
            command = f"ping -c 4 {host}"
        result = os.popen(command).read()
        lost_packets = int(result.split("Lost = ")[-1][0]) if "Lost" in result else 0
        total_packets = 4
        packet_loss = (lost_packets / total_packets) * 100
        return jsonify({"packet_loss": packet_loss})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/network-info')
def network_info():
    try:
        info = get_network_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/measure-rtt')
def measure_rtt():
    host = request.args.get('host', 'google.com')
    start_time = time.time()
    system = platform.system().lower()
    if 'windows' in system:
        command = f"ping -n 1 {host}"
    else:
        command = f"ping -c 1 {host}"
    os.popen(command).read()
    rtt = (time.time() - start_time) * 1000
    return jsonify({"rtt": round(rtt, 2)})

@app.route('/traceroute')
def traceroute():
    host = request.args.get('host', 'google.com')
    system = platform.system().lower()
    if 'windows' in system:
        command = f"tracert {host}"
    else:
        command = f"traceroute {host}"
    try:
        result = os.popen(command).read()
        return jsonify({"traceroute": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/dns-lookup')
def dns_lookup():
    host = request.args.get('host', 'google.com')
    try:
        ip_addresses = socket.gethostbyname_ex(host)
        return jsonify({"dns_records": ip_addresses})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/system-uptime')
def system_uptime():
    try:
        system = platform.system().lower()
        if 'windows' in system:
            uptime = os.popen("net stats workstation").read()
        else:
            uptime = os.popen("uptime").read()
        return jsonify({"uptime": uptime})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)