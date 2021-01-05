#!/usr/bin/python3
# -*- coding:utf8 -*-
import subprocess
import sys
import argparse
import os
from random import shuffle
from pocs import const
from banner import banner
from concurrent.futures import ThreadPoolExecutor,wait, ALL_COMPLETED

naabu = 'naabu_linux'
httpxname = 'httpx_linux'


#读取文件输出list
def readf(fname):
	li = []
	try:
		f = open(fname)
		for text in f.readlines():
			data1 = text.strip('\n')
			if data1 != '':
				li.append(data1)
		f.close()
	except:
		return None
	return li


#设置两种系统
def getsys(sys0):
	global naabu
	global httpxname
	if sys0.lower() == 'linux':
		naabu = 'naabu_linux'
		httpxname = 'httpx_linux'
	if sys0.lower() == 'win':
		naabu = 'naabu_win.exe'
		httpxname = 'httpx_win.exe'

#写入
def prefil(strw):
	try:
		f = open('tmp.txt','a')
		f.write(strw)
		f.write('\n')
	finally:
		f.close()


#写入
def pFile(strw):
	try:
		f = open('ports.txt','a')
		f.write(strw)
		f.write('\n')
	finally:
		f.close()


#写入
def hFile(strw):
	try:
		f = open('http.txt','a')
		f.write(strw)
		f.write('\n')
	finally:
		f.close()

# 从文件读取扫描结果
def getresult(filename):
    file = open(filename,'r',encoding='utf-8')
    s = file.readlines()
    s=[x.strip() for x in s if x.strip()!='']
    return s



#端口扫描
def port_scan(file_name):
	portL = []
	cmd = ["./ports/"+naabu, "-iL", file_name, "-p", const.all_ports, "-nC", "-privileged", "-silent", "-ping", "false",  "-rate", "1000", "-no-probe"]
	#print(cmd)
	print("Ports Scanning.")
	try:
		output = subprocess.check_output(cmd)
	except Exception as e:
		print(e)
		sys.exit(1)
	print("Finish Ports Scan.")
	portL = str(output).split("\\n")
	try:
		portL[0] = portL[0].split("'")[1]
		del portL[-1]
	except:
		pass
	for pl in portL:
		pFile(pl)

	return portL

#httpx扫描
def httpx(target):
	cmd = ["./httpx/"+ httpxname, "-l", target, "-ports", "80,443,8080,8090,8443,9090,8880,2052,2082,2086,2095,2053,2083,2087,2096", "-mc","200","-threads", "600", "-silent", "-no-color", "-follow-redirects"]
	print("Httpx Scanning.")
	try:
		output = subprocess.check_output(cmd)
	except Exception as e:
		print(e)
		sys.exit(1)
	print("Finish Httpx Scan.")
	portL = str(output).split("\\n")
	httpL = []
	try:
		portL[0] = portL[0].split("'")[1]
		del portL[-1]
	except:
		pass
	for i in portL:
		if i is not None:
			i = i.split("//")[1].strip("/")
			httpL.append(i)
	for pl in httpL:
		hFile(pl)
	return httpL



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
#high level
def vulnscan(target):
	port = str(target.split(":")[1])
	for dl in const.dic_vuln:
		if port in dl["port"]:
			dl["func"](target)

#删除文件
def delf(fname):
	try:
		os.remove(fname)
	except:
		return


if __name__ == '__main__':
	banner.banner()
	if len(sys.argv) == 1:
		print('\n')
		print("Usage: python3 frogAuth.py win/linux -f ip.txt")
		exit()
	else:
		parser = argparse.ArgumentParser() 
		parser.add_argument('os', help='win/linux')
		parser.add_argument('-m',help='scan/file',default='scan')
		parser.add_argument('-f', help='filename', default='ip.txt')
		args = parser.parse_args()
		getsys(args.os)
	file = args.f
	module = args.m
	delf("tmp.txt")
	# 获取扫描结果
	if module == 'file':
		port_res = getresult(file)	
	else:
		port_res = port_scan(file)
	#对扫描结果进行打乱
	port_res = list(set(port_res))
	shuffle(port_res)
    
	fileL = readf(file)

	for f in fileL:
		try:
			if f.split(".")[-1].isalpha():
				prefil(f)
		except:
			continue
	if os.path.exists("tmp.txt"):
		http_res = httpx("tmp.txt")
		http_res = list(set(http_res))
		shuffle(http_res)
	else:
		http_res = ['']
	
	print("unauth Scanning Low.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(unauth_low, target) for target in port_res]
		all_task = [pool.submit(unauth_low, target) for target in http_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished Low.')

	print("unauth Scanning Mid.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(unauth_mid, target) for target in port_res]
		all_task = [pool.submit(unauth_mid, target) for target in http_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished Mid.')

	print("unauth Scanning High.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(unauth_high, target) for target in port_res]
		all_task = [pool.submit(unauth_high, target) for target in http_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished High.')

	print("Springboot Scanning.")
	with ThreadPoolExecutor(max_workers=100) as pool:
		all_task = [pool.submit(springb, target) for target in port_res]
		all_task = [pool.submit(springb, target) for target in http_res]
		wait(all_task, return_when=ALL_COMPLETED)
	print('Finished Springboot Scan.')
	delf("tmp.txt")
