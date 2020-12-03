#!/usr/bin/python3
# coding: utf-8
import socket
import pymongo
import requests
import ftplib
import pymysql
import logging
logging.captureWarnings(True)
from pocs import const
from pyzabbix import ZabbixAPI

HD = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

#添加写入
def rFile(strw):
	try:
		f = open('results.txt','a')
		f.write(strw)
		f.write('\n')
	finally:
		f.close()

def redis(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		socket.setdefaulttimeout(10)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		s.send(bytes("INFO\r\n", 'UTF-8'))
		result = s.recv(1024).decode()
		if "redis_version" in result:
			print(target + " redis未授权")
			rFile(str(target) + " redis未授权")
		s.close()
	except:
		return



def mongodb(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		conn = pymongo.MongoClient(ip, port, socketTimeoutMS=4000)
		dbname = conn.list_database_names()
		print(target + " mongodb未授权")
		rFile(str(target) + " mongodb未授权")
		conn.close()
	except:
		return



def memcached(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		socket.setdefaulttimeout(10)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		s.send(bytes('stats\r\n', 'UTF-8'))
		if 'version' in s.recv(1024).decode():
			print(target + " memcached未授权")
			rFile(str(target) + " memcached未授权")
		s.close()
	except:
		return


def elasticsearch(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url0 = 'https://'+str(target) +'/'
			url = 'https://'+str(target) +'/_cat'
		else:
			url0 = 'http://'+str(target) +'/'
			url = 'http://'+str(target) +'/_cat'
		r0 = requests.get(url0, headers = HD, timeout=10,verify=False, allow_redirects=False)
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'You Know, for Search' in r0.content.decode() and '/_cat/master' in r.content.decode():
			print(url + " elasticsearch未授权")
			rFile(str(url) + " elasticsearch未授权")
	except:
		return


def zookeeper(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		socket.setdefaulttimeout(10)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		s.send(bytes('envi', 'UTF-8'))
		data = s.recv(1024).decode()
		s.close()
		if 'Environment' in data:
			print(target + " zookeeper未授权")
			rFile(str(target) + " zookeeper未授权")
	except:
		return


def ftp(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		ftp = ftplib.FTP.connect(ip,port,timeout=10)
		ftp.login('anonymous', 'Aa@12345678')
		print(target + " FTP未授权")
		rFile(str(target) + " FTP未授权")
	except:
		return


def CouchDB(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/_config'
		else:
			url = 'http://'+str(target) +'/_config'
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'httpd_design_handlers' in r.content.decode() and 'external_manager' in r.content.decode() and 'replicator_manager' in r.content.decode():
			print(url + " CouchDB未授权")
			rFile(str(url) + " CouchDB未授权")
	except:
		return


def docker(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url0 = 'https://'+str(target) +'/info'
			url = 'https://'+str(target) +'/version'
		else:
			url0 = 'http://'+str(target) +'/info'
			url = 'http://'+str(target) +'/version'
		r0 = requests.get(url0, headers = HD, timeout=10,verify=False, allow_redirects=False)
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'ApiVersion' in r.content.decode() and 'KernelVersion' in r0.content.decode() and 'RegistryConfig' in r0.content.decode():
			print(url0 + " docker api未授权")
			rFile(str(url0) + " docker api未授权")
	except:
		return


def Hadoop(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/dfshealth.html'
		else:
			url = 'http://'+str(target) +'/dfshealth.html'
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'hadoop.css' in r.content.decode():
			print(url + " Hadoop未授权")
			rFile(str(url) + " Hadoop未授权")
	except:
		return



def hadoop_yarn(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/ws/v1/cluster/info'
		else:
			url = 'http://'+str(target) +'/ws/v1/cluster/info'
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		if 'resourceManagerVersionBuiltOn' in r.content.decode() and 'hadoopVersion'in r.content.decode():
			print(url + " Hadoop yarn未授权")
			rFile(str(url) + " Hadoop yarn未授权")
	except:
		return





def docker_reg(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url0 = 'https://'+str(target) +'/v2/'
			url = 'https://'+str(target) +'/v2/_catalog'
		else:
			url0 = 'http://'+str(target) +'/v2/'
			url = 'http://'+str(target) +'/v2/_catalog'
		r0 = requests.get(url0, headers = HD, timeout=10,verify=False, allow_redirects=False)
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'docker-distribution-api-version' in str(r0.headers) and 'repositories' in r.content.decode():
			print(url0 + " docker-registry-api未授权")
			rFile(str(url0) + " docker-registry-api未授权")
	except:
		return

def zabbix(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url0 = 'https://'+str(target) +'/zabbix'
			url = 'https://'+str(target) +'/'
		else:
			url0 = 'http://'+str(target) +'/zabbix'
			url = 'http://'+str(target) +'/'
	except:
		return
	try:
		r = requests.get(url0, headers = HD, timeout=10,verify=False, allow_redirects=True)
		r0 = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=True)
	except:
		return
	if "zabbix" in r.content.decode().lower() or "zabbix" in r0.content.decode().lower():
		try:
			zapi = ZabbixAPI(url0)
			zapi.session.verify = False
			zapi.timeout = 10
			zapi.login("Admin", "zabbix")
			print(url0 + "zabbix默认密码Admin/zabbix")
			rFile(url0 + "zabbix默认密码Admin/zabbix")
		except:
			try:
				zapi = ZabbixAPI(url)
				zapi.session.verify = False
				zapi.timeout = 10
				zapi.login("Admin", "zabbix")
				print(url + "zabbix默认密码Admin/zabbix")
				rFile(url + "zabbix默认密码Admin/zabbix")
			except:
				return
	else:
		return


def influxdb(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url0 = 'https://'+str(target) +'/ping'
			url = 'https://'+str(target) +'/query?q=show%20users'
		else:
			url0 = 'http://'+str(target) +'/ping'
			url = 'http://'+str(target) +'/query?q=show%20users'
		r0 = requests.get(url0, headers = HD, timeout=10,verify=False)
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		if 'X-Influxdb-Version' in str(r0.headers) and 'columns' in r.content.decode() and 'user' in r.content.decode():
			print(url + " influxdb未授权")
			rFile(str(url) + " influxdb未授权")
	except:
		return


def druid(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/druid/index.html'
		else:
			url = 'http://'+str(target) +'/druid/index.html'
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		if 'Druid Stat Index' in r.content.decode() and 'DruidVersion' in r.content.decode() and 'DruidDrivers' in r.content.decode():
			print(url + " druid-monitor未授权")
			rFile(str(url) + " druid-monitor未授权")
	except:
		return


def jboss(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/jmx-console/'
		else:
			url = 'http://'+str(target) +'/jmx-console/'
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'jboss.management.local' in r.content.decode() and 'jboss.web' in r.content.decode():
			print(url + " jboss未授权")
			rFile(str(url) + " jboss未授权")
	except:
		return


def jenkins(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/systemInfo'
		else:
			url = 'http://'+str(target) +'/systemInfo'
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if 'jenkins.war' in r.content.decode() and 'JENKINS_HOME' in r.content.decode():
			print(url + " jenkins未授权")
			rFile(str(url) + " jenkins未授权")
	except:
		return



def rsync(target):
	try:
		print(target + " 可能存在rsync未授权")
		rFile(str(target) + " 可能存在rsync未授权")
	except:
		pass


def mysql(target):
	try:
		ip = target.split(":")[0]
		port0 = target.split(":")[1]
		conn = pymysql.connect(host=ip, port=port0, user='root', password='', charset='utf8', autocommit=True)
		print(target + " 存在mysql空口令漏洞")
		rFile(target + " 存在mysql空口令漏洞")
	except:
		try:
			conn = pymysql.connect(host=ip, port=port0, user='root', password='root', charset='utf8', autocommit=True)
			print(target + " 存在mysql root:root口令漏洞")
			rFile(target + " 存在mysql root:root口令漏洞")
		except:
			pass
		return



def kibana(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or "5601" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/app/kibana'
		else:
			url = 'http://'+str(target) +'/app/kibana'
		r = requests.get(url, headers = HD, timeout=10,verify=False, allow_redirects=False)
		if '.kibanaWelcomeView' in r.content.decode():
			print(url + " kibana未授权")
			rFile(str(url) + " kibana未授权")
	except:
		return


def kong(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/'
			url0 = 'https://'+str(target) +'/status'
		else:
			url = 'http://'+str(target) +'/'
			url0 = 'https://'+str(target) +'/status'
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		r0 = requests.get(url0, headers = HD, timeout=10,verify=False)
		if 'kong_env' in r.content.decode() and 'kong_db_cache_miss' in r0.content.decode():
			print(url0 + " kong未授权")
			rFile(str(url0) + " kong未授权")
	except:
		return


def spark_api(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		url0 = 'https://'+str(target) +'/v1/submissions'
		url = 'http://'+str(target) +'/v1/submissions'
		try:
			r0 = requests.get(url0, headers = HD, timeout=10,verify=False)
			if r0.status_code == 400 and 'serverSparkVersion' in r0.content.decode():
				print(url0 + " spark_api未授权")
				rFile(str(url0) + " spark_api未授权")
		except:
			pass
		try:
			r = requests.get(url, headers = HD, timeout=10,verify=False)
			if r.status_code == 400 and 'serverSparkVersion' in r.content.decode():
				print(url + " spark_api未授权")
				rFile(str(url) + " spark_api未授权")
		except:
			pass
	except:
		return


def spark(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/'
		else:
			url = 'http://'+str(target) +'/'
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		if '<title>Spark' in r.content.decode() and '<strong>URL:</strong> spark:' in r.content.decode():
			print(url + " spark未授权")
			rFile(str(url) + " spark未授权")
	except:
		return


def tensorboard(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url0 = 'https://'+str(target) +'/'
			url = 'https://'+str(target) +'/data/plugins_listing'
		else:
			url0 = 'http://'+str(target) +'/'
			url = 'https://'+str(target) +'/data/plugins_listing'
		r0 = requests.get(url0, headers = HD, timeout=10,verify=False)
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		if 'The TensorFlow Authors. All Rights Reserved.' in r0.content.decode() and 'distributions' in r.content.decode() and 'profile' in r.content.decode():
			print(url + " tensorboard未授权")
			rFile(str(url) + " tensorboard未授权")
	except:
		return



def flink(target):
	try:
		ip = target.split(":")[0]
		port = target.split(":")[1]
		if "443" in str(port) or str(port) in const.https_ports:
			url = 'https://'+str(target) +'/jars/'
		else:
			url = 'http://'+str(target) +'/jars/'
		r = requests.get(url, headers = HD, timeout=10,verify=False)
		if r.status_code == 200 and "application/json" in r.headers['Content-Type'] and 'address' in r.content.decode():
			print(url + " flink未授权")
			rFile(str(url) + " flink未授权")
	except:
		return



def solr(target):
	solrpath=['/solr','/Solr','/']
	for i in solrpath:
		try:
			ip = target.split(":")[0]
			port = target.split(":")[1]
			if "443" in str(port) or str(port) in const.https_ports:
				url = 'https://'+str(target) +i
			else:
				url = 'http://'+str(target) +i
			r = requests.get(url, headers = HD, timeout=10,verify=False)
			if r.status_code == 200 and ("<title>Solr Admin</title>" in r.content.decode() or "app_config.solr_path" in r.content.decode() or "<span>Solr Query Syntax</span>" in r.content.decode()):
				print(url + " solr未授权")
				rFile(str(url) + " solr未授权")
				return
		except:
			pass
