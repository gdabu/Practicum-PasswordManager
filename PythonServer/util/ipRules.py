# echo /path/to/my/script | at now + 5 min
# iptables -I INPUT -s 192.168.1.100 -j DROP
# echo "iptables -D INPUT -s 192.168.1.100 -j DROP" | at @10pm 
# 
import os

def blockIp(ip, duration):
	retvalue = os.system("iptables -I INPUT -s " + ip + " -p tcp --destination-port " + `8000` + " -j DROP")
	retvalue2 = os.system("echo 'iptables -D INPUT -s " + ip + " -p tcp --destination-port " + `8000` + " -j DROP' | at now + " + `duration` + " min")
	print retvalue, retvalue2