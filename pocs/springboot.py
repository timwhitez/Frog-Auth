#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

'''
 ____	    _	  _	_ _   __  __	       _
|  _ \ __ _| |__ | |__ (_) |_|  \/  | __ _ ___| | __
| |_) / _` | '_ \| '_ \| | __| |\/| |/ _` / __| |/ /
|  _ < (_| | |_) | |_) | | |_| |  | | (_| \__ \   <
|_| \_\__,_|_.__/|_.__/|_|\__|_|  |_|\__,_|___/_|\_\
'''
import requests

pathlist=['/autoconfig','/beans','/configprops','/dump','/health','/info','/mappings','/metrics','/trace',]
HD = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
		   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

requests.packages.urllib3.disable_warnings()

def saveinfo(result):
	if result:
		fw=open('results.txt','a')
		fw.write(result+'\n')
		fw.close()


#大多数Actuator仅支持GET请求并仅显示敏感的配置数据,如果使用了Jolokia端点，可能会产生XXE、甚至是RCE安全问题。
#通过查看/jolokia/list 中存在的 Mbeans，是否存在logback 库提供的reloadByURL方法来进行判断。
def Jolokiacheck(url):
	url_tar = url + '/jolokia/list'
	r = requests.get(url_tar, headers=HD, timeout=10, verify=False, allow_redirects=False)
	if r.status_code == 200:
		print("springboot-jolokia未授权：{}".format(url_tar))
		saveinfo("springboot-jolokia未授权：{}".format(url_tar))
		if 'reloadByURL' in r.text:
			print("springboot-jolokia存在reloadByURL方法,可进行XXE/RCE测试：{}".format(url_tar))
			saveinfo("springboot-jolokia 端点存在reloadByURL方法,可进行XXE/RCE测试：{}".format(url_tar))
		if 'createJNDIRealm' in r.text:
			print("springboot-jolokia存在createJNDIRealm方法,可进行JNDI注入RCE测试：{}".format(url_tar))
			saveinfo("springboot-jolokia 端点存在createJNDIRealm方法,可进行JNDI注入RCE测试：{}".format(url_tar))


#Spring Boot env端点存在环境属性覆盖和XStream反序列化漏洞
def Envcheck_1(url):
	url_tar = url + '/env'
	r = requests.get(url_tar, headers=HD, timeout=10, verify=False, allow_redirects=False)
	if r.status_code == 200:
		print("springboot-env未授权访问：{}".format(url_tar))
		saveinfo("springboot-env未授权访问：{}".format(url_tar))
		if 'spring.cloud.bootstrap.location' in r.text:
			print("springboot-env 端点spring.cloud.bootstrap.location属性开启,可进行环境属性覆盖RCE测试：{}".format(url_tar))
			saveinfo("springboot-env 端点spring.cloud.bootstrap.location属性开启,可进行环境属性覆盖RCE测试：{}".format(url_tar))
		if 'eureka.client.serviceUrl.defaultZone' in r.text:
			print("springboot-env 端点eureka.client.serviceUrl.defaultZone属性开启,可进行XStream反序列化RCE测试：{}".format(url_tar))
			saveinfo("springboot-env 端点eureka.client.serviceUrl.defaultZone属性开启,可进行XStream反序列化RCE测试：{}".format(url_tar))


#Spring Boot 1.x版本端点在根URL下注册。
def sb1_Actuator(url):
	key=0
	Envcheck_1(url)
	Jolokiacheck(url)
	for i in pathlist:
		url_tar = url+i
		r = requests.get(url_tar, headers=HD, timeout=10, verify=False, allow_redirects=False)
		if r.status_code==200:
			print("springboot-{} 端点的未授权访问：{}".format(i.replace('/',''),url_tar))
			saveinfo("springboot-{} 端点的未授权访问：{}".format(i.replace('/',''),url_tar))
			key=1
	return key

#Spring Boot 2.x版本存在H2配置不当导致的RCE，目前非正则判断，测试阶段
#另外开始我认为环境属性覆盖和XStream反序列化漏洞只有1.*版本存在
#后来证实2.*也是存在的，data需要以json格式发送，这个我后边会给出具体exp
def Envcheck_2(url):
	url_tar = url + '/actuator/env'
	r = requests.get(url_tar, headers=HD, timeout=10, verify=False, allow_redirects=False)
	if r.status_code == 200:
		print("springboot-env 未授权访问：{}".format(url_tar))
		saveinfo("springboot-env 未授权访问：{}".format(url_tar))
		if 'spring.cloud.bootstrap.location' in r.text:
			print("springboot-env 端点spring.cloud.bootstrap.location属性开启,可进行环境属性覆盖RCE测试：{}".format(url_tar))
			saveinfo("springboot-env 端点spring.cloud.bootstrap.location属性开启,可进行环境属性覆盖RCE测试：{}".format(url_tar))
		if 'eureka.client.serviceUrl.defaultZone' in r.text:
			print("springboot-env 端点eureka.client.serviceUrl.defaultZone属性开启,可进行XStream反序列化RCE测试：{}".format(url_tar))
			saveinfo("springboot-env 端点eureka.client.serviceUrl.defaultZone属性开启,可进行XStream反序列化RCE测试：{}".format(url_tar))
		headers["Cache-Control"]="max-age=0"
		rr = requests.post(url+'/actuator/restart', headers=headers, verify=False, timeout=10, allow_redirects=False)
		if rr.status_code == 200:
			print("springboot-env 端点支持restart端点访问,可进行H2 RCE测试：{}".format(url+'/actuator/restart'))
			saveinfo("springboot-env 端点支持restart端点访问,可进行H2 RCE测试：{}".format(url+'/actuator/restart'))



#Spring Boot 2.x版本端点移动到/actuator/路径。
def sb2_Actuator(url):
	Envcheck_2(url)
	Jolokiacheck(url+'/actuator')
	for i in pathlist:
		url_tar = url+'/actuator'+i
		r = requests.get(url_tar, headers=HD,timeout=10, verify=False, allow_redirects=False)
		if r.status_code==200:
			print("springboot-{}未授权访问：{}".format(i.replace('/',''),url_tar))
			saveinfo("springboot-{}未授权访问：{}".format(i.replace('/', ''), url_tar))



def sbcheck(url):
	try:
		r = requests.get(url+ '/404', headers=HD, timeout=10,verify=False, allow_redirects=False)
		if r.status_code==404 or r.status_code==403:
			if 'Whitelabel Error Page' in r.text  or 'There was an unexpected error'in r.text:
				return 1
			else:
				return 0
		else:
			return 0
	except requests.exceptions.ConnectTimeout:
		return 0
	except requests.exceptions.ConnectionError:
		return 0




def sb_Actuator(target):
	ip = target.split(":")[0]
	port = target.split(":")[1]
	if "443" in str(port):
		url = 'https://'+str(target)
	else:
		url = 'http://'+str(target)
	flag = 0
	flag = sbcheck(url)
	if flag != 1:
		return
	else:
		try:
			if sb1_Actuator(url)==0:
				sb2_Actuator(url)
		except:
			return
