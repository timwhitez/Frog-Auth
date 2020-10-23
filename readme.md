- 本人github的项目可能目前主要分为两大类，🐸Frog系列为自动化扫描方向，🐶Doge系列为免杀及内网渗透方向

- 本系列命名为Frog可能是因为这种生物的寿命长 🐸 🤓 +1s 

- Frog-Auth为Frog系列第二个项目🐸

# 🐸Frog-Auth

Frog-Auth未授权访问检测，采用python3实现，使用subprocess加载naabu端口扫描工具，

配合全面的未授权访问pocs以及独特检测框架，支持ip/domain/CIDR输入。

- [naabu](https://github.com/projectdiscovery/naabu) golang端口扫描工具

在对大量数据整理分析过后挑选了79个未授权访问服务对应的高频端口，使用naabu进行端口扫描，

扫描结果会按开放端口情况再进行分类后按需进行乱序检测，

poc也被分成四类，大致依据我自己主观判断poc被ban的可能性。

目前有针对以下服务的未授权漏洞检测:

```
redis, mongodb, memcached, zookeeper, Hadoop, mysql, 

ftp, kibana, kong, elasticsearch, CouchDB, docker, 

docker registry api, influxdb, hadoop yarn api, 

jenkins, druid, spark, spark api, tensorboard, jboss

springboot
```
感谢RabbitMask提供的springboot poc, xray社区的部分未授权访问poc, kingkk的架构建议, cwkiller的部分未授权poc

# 常用命令
```
python3 frogAuth.py linux -f ip.txt

python3 frogAuth.py win -f ip.txt
```
ip.txt按行划分，支持ip/domain/CIDR格式

# Usage
若在linux下使用，请给 naabu_linux 可执行权限
```
python3 -m pip install requirements.txt

python3 frogAuth.py linux/win -f ip.txt

```
# 运行截图
![image]()

#todo
若有好的建议，新的未授权访问poc，程序的bug，欢迎提交issues