#!/usr/bin/python3
# coding: utf-8
import subprocess
import sys
import argparse
from random import shuffle
from pocs import const
from banner import banner
from concurrent.futures import ThreadPoolExecutor,wait, ALL_COMPLETED

naabu = 'naabu_linux'


#设置两种系统
def getsys(sys0):
	global naabu
	if sys0.lower() == 'linux':
		naabu = 'naabu_linux'
	if sys0.lower() == 'win':
		naabu = 'naabu_win.exe'


#覆盖写入
def pFile(strw):
	try:
		f = open('ports.txt','a')
		f.write(strw)
		f.write('\n')
	finally:
		f.close()


#端口扫描
def port_scan(file_name):
	portL = []
	cmd = ["./ports/"+naabu, "-iL", file_name, "-p", const.all_ports, "-nC", "-privileged", "-silent", "-ping", "false", "-verify", "-rate", "1000", "-exclude-cdn"]
	print("Ports Scanning.")
	try:
		output = subprocess.check_output(cmd)
		print("Finish Ports Scan.")
		portL = str(output).split("\\n")
		try:
			portL[0] = portL[0].split("'")[1]
		except:
			pass
		del portL[-1]
		for pl in portL:
			pFile(pl)
	except:
		return portL

	return portL


#low level
def unauth_low(target):
	port = str(target.split(":")[1])
	for dl in const.dic_list_low:
		if port in dl["port"]:
			dl["func"](target)



#mid level
def unauth_mid(target):
	port = str(target.split(":")[1])
	for dl in const.dic_list_mid:
		if port in dl["port"]:
			dl["func"](target)


#high level
def unauth_high(target):
	port = str(target.split(":")[1])
	for dl in const.dic_list_high:
		if port in dl["port"]:
			dl["func"](target)

#high level
def springb(target):
	port = str(target.split(":")[1])
	for dl in const.dic_springboot:
		if port in dl["port"]:
			dl["func"](target)




if __name__ == '__main__':
	banner.banner()
	if len(sys.argv) == 1:
		print('\n')
		print("Usage: python3 frogAuth.py win/linux -f ip.txt")
		exit()
	else:
		parser = argparse.ArgumentParser() 
		parser.add_argument('os', help='win/linux')
		parser.add_argument('-f', help='filename', default='ip.txt')
		args = parser.parse_args()
		getsys(args.os)
	file = args.f
	port_res = port_scan(file)

	#对扫描结果进行打乱
	shuffle(port_res)

	print("unauth Scanning Low.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(unauth_low, target) for target in port_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished Low.')

	print("unauth Scanning Mid.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(unauth_mid, target) for target in port_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished Mid.')

	print("unauth Scanning High.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(unauth_high, target) for target in port_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished High.')

	print("Springboot Scanning.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(springb, target) for target in port_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished Springboot Scan.')