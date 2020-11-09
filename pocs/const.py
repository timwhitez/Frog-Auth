#!/usr/bin/python3
# coding: utf-8
from pocs import pocs
from pocs import springboot

https_ports = "443,2053,2083,2087,2096,8443,9443,18443"

#端口扫描列表
all_ports = "21,80,81,443,616,873,990,993,2181,2375,2376,2600,3000,3001,3306,3307,3310,3311,3312,3333,4040,4443,5000,5001,5060,5601,5984,5986,6006,6060,6066,6379,6699,6779,6969,7000,7001,7002,7402,7777,8000,8001,8010,8020,8025,8030,8042,8080,8081,8082,8083,8085,8086,8088,8089,8090,8099,8181,8443,8480,8886,8888,8983,9000,9002,9003,9080,9090,9200,9300,9443,9527,9870,9999,10000,11211,15000,15001,15002,18081,20000,27017,27018,28017,32768,50000,50030,50070,50075,50090,21502"

#各种服务对应的端口
RD = ["6379","7001","7002","7000","32768","7777","6969","6699","10000","6779","80","443","616"]
MDB = ["27017", "28017", "20000", "27018", "10000"]
MC = ["11211", "2600", "15000", "15001", "3000", "9002", "15002", "9003"]
ES = ["9200", "80", "9527", "8090", "8080", "9300", "9000"]
ZK = ["2181"]
DK = ["2375", "80", "443", "8088", "8080", "8443"]
HDP = ["50070", "50090", "9870", "50075", "50030", "80", "443", "8088", "8030", "9000", "8010", "8480", "8025", "8042", "8020"]
RS = ["873"]
FP = ["21", "990"]
CDB = ["5984", "5986", "80", "443", "8088", "8080", "8443"]
DKR = ["5000", "5001", "2375", "993", "9000", "9200", "80", "443", "8080", "2376"]
HDY = ["8088", "8090", "8089", "8099", "3000", "3001", "4040", "8080"]
IDB = ["8086", "8083", "3000", "80", "443", "8085", "8080", "9999"]
DRD = ["8888", "8081", "8090", "443", "80", "8080", "8443", "9080", "9443"]
JBS = ["80", "443", "8080", "8081", "8443", "9200", "5601", "8000", "8888", "9080", "9443"]
JKS = ["8080", "443", "80", "50000", "8081", "9090", "8888", "8090", "8088", "9080", "9443"]
MYS = ["3306", "3307", "3310", "3333", "3311", "3312"]
KBN = ["5601", "443", "80", "8080"]
KO = ["443", "80", "8000", "8001", "8443"]
SPAPI = ["6066", "6066"]
SP = ["8081", "8080", "443", "4040", "80", "18081"]
TB = ["443", "80", "6006", "8080", "8888", "8000"]
SB = ["80", "443", "8080", "8081", "8088", "9080", "9443","7000","21502"]
ZBX = ["80","81","443","3000","4040","8080","8081","8090","8181","8081","8443","9090","4443","7402","5060","6060","9002","15001"]
FL = ["8080","8081","8082","18081","80","443","8443","8083","8088","8089","8085"]
SLR = ["8983","80","8090","8080","443","8886","8083","8081","8082","20000","8085","8888"]

#端口与函数的对应
dicRD = {"port":RD,"func":pocs.redis}
dicMDB = {"port":MDB,"func":pocs.mongodb}
dicMC = {"port":MC,"func":pocs.memcached}
dicZK = {"port":ZK,"func":pocs.zookeeper}
dicHDP = {"port":HDP,"func":pocs.Hadoop}
dicDK = {"port":DK,"func":pocs.docker}
#dicRS = {"port":RS,"func":pocs.rsync}


dicMYS = {"port":MYS,"func":pocs.mysql}
dicFP = {"port":FP,"func":pocs.ftp}
dicSP = {"port":SP,"func":pocs.spark}
dicKBN = {"port":KBN,"func":pocs.kibana}
dicKO = {"port":KO,"func":pocs.kong}
dicES = {"port":ES,"func":pocs.elasticsearch}
dicCDB = {"port":CDB,"func":pocs.CouchDB}
dicDKR = {"port":DKR,"func":pocs.docker_reg}

dicIDB = {"port":IDB,"func":pocs.influxdb}
dicHDY = {"port":HDY,"func":pocs.hadoop_yarn}
dicJKS = {"port":JKS,"func":pocs.jenkins}
dicDRD = {"port":DRD,"func":pocs.druid}
dicSPAPI = {"port":SPAPI,"func":pocs.spark_api}
dicTB = {"port":TB,"func":pocs.tensorboard}
dicJBS = {"port":JBS,"func":pocs.jboss}

dicSB = {"port":SB,"func":springboot.sb_Actuator}

dicZBX = {"port":ZBX,"func":pocs.zabbix}
dicFL = {"port":FL,"func":pocs.flink}
dicSLR = {"port":SLR,"func":pocs.solr}


dic_list_low = [dicRD,dicMDB,dicMC,dicZK,dicDK]
#dic_list_low = [dicRD,dicMDB,dicMC,dicZK,dicDK,dicRS]
dic_list_mid = [dicMYS,dicFP,dicSP,dicKBN,dicKO,dicES,dicCDB,dicDKR,dicZBX]
dic_list_high = [dicIDB,dicHDY,dicJKS,dicDRD,dicSPAPI,dicTB,dicJBS,dicHDP,dicFL,dicSLR]
dic_springboot = [dicSB]
