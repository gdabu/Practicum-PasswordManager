
import nmap

def getHosts(network):
	nm = nmap.PortScanner()
	nm.scan(hosts=network, arguments='-n -sP -PE')

	host_list = []

	for host in nm.all_hosts():
		host_list.append({
			"host" : host
		})

	print host_list

	return host_list
