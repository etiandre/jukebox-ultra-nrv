import subprocess, re

def get_subnet():
    ip_out = subprocess.check_output(["ip", "addr", "show", CONFIG["iface"]]).decode()
    return re.findall("inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,3})", ip_out)[0]

def scan(subnet):
    #TODO: remove nmap dependency
    nmap_out = subprocess.check_output(["nmap", "-n", "-sP", "-oG", "-", "subnet"]).decode()
    return re.findall("Host: ([\d\.]+) \(\)", nmap_out)[0]

def get_mac(ip):
	if ip == "127.0.0.1":
		return "00:00:00:00:00:00"
	else:
		arping_out = subprocess.check_output(["arping", "-f", "-w", "1", ip]).decode()
		return re.findall("\[([\w:]+)",arping_out)[0]



