#!/usr/bin/python3
# -*- coding: utf-8 -*-

# HTTPS is selected only by exact port match. This avoids the old false positives
# from substring checks such as "443" in "14430".
https_ports = "443,2053,2083,2087,2096,8443,9443,18443,6443"
https_ports_set = set(https_ports.split(","))

# Service high-frequency ports
RD = ["6379", "7001", "7002", "7000", "32768", "7777", "6969", "6699", "10000", "6779", "80", "443", "616"]
MDB = ["27017", "28017", "20000", "27018", "10000"]
MC = ["11211", "2600", "15000", "15001", "3000", "9002", "15002", "9003"]
ES = ["9200", "80", "9527", "8090", "8080", "9300", "9000"]
ZK = ["2181"]
DK = ["2375", "80", "443", "8088", "8080", "8443", "2376"]
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
SPAPI = ["6066"]
SP = ["8081", "8080", "443", "4040", "80", "18081"]
TB = ["443", "80", "6006", "8080", "8888", "8000"]
SB = ["80", "443", "8080", "8081", "8088", "9080", "9443", "7000", "21502"]
ZBX = ["80", "81", "443", "3000", "4040", "8080", "8081", "8090", "8181", "8443", "9090", "4443", "7402", "5060", "6060", "9002", "15001"]
FL = ["8080", "8081", "8082", "18081", "80", "443", "8443", "8083", "8088", "8089", "8085"]
SLR = ["8983", "80", "8090", "8080", "443", "8886", "8083", "8081", "8082", "20000", "8085", "8888"]

# Newly covered read-only components
PROM = ["9090", "80", "443"]
ALERTMANAGER = ["9093", "80", "443"]
GRAFANA = ["3000", "80", "443", "8080"]
CONSUL = ["8500", "8501", "80", "443"]
ETCD = ["2379", "2380", "4001"]
K8S = ["6443", "8080", "8001"]
JUPYTER = ["8888", "8889", "8890", "80", "443"]
SWAGGER = ["80", "81", "443", "7001", "7002", "8000", "8080", "8081", "8082", "8088", "8090", "8443", "9000", "9080", "9443"]
NACOS = ["8848", "9848", "80", "443", "8080"]
RABBITMQ = ["15672", "15671", "80", "443"]
JAEGER = ["16686", "80", "443"]
ZIPKIN = ["9411", "80", "443"]


def _unique_ports(*groups):
    ports = set()
    for group in groups:
        ports.update(str(port) for port in group if str(port).strip())
    return sorted(ports, key=lambda x: (0, int(x)) if x.isdigit() else (1, x))


ALL_PORT_GROUPS = [
    RD, MDB, MC, ES, ZK, DK, HDP, RS, FP, CDB, DKR, HDY, IDB, DRD, JBS,
    JKS, MYS, KBN, KO, SPAPI, SP, TB, SB, ZBX, FL, SLR, PROM,
    ALERTMANAGER, GRAFANA, CONSUL, ETCD, K8S, JUPYTER, SWAGGER, NACOS,
    RABBITMQ, JAEGER, ZIPKIN,
]
all_ports = ",".join(_unique_ports(*ALL_PORT_GROUPS))

from pocs import additional, pocs, springboot

# Port to function registry. Kept as dictionaries for compatibility with the
# original frogAuth.py plugin model.
dicRD = {"name": "redis", "port": RD, "func": pocs.redis, "level": "low"}
dicMDB = {"name": "mongodb", "port": MDB, "func": pocs.mongodb, "level": "low"}
dicMC = {"name": "memcached", "port": MC, "func": pocs.memcached, "level": "low"}
dicZK = {"name": "zookeeper", "port": ZK, "func": pocs.zookeeper, "level": "low"}
dicDK = {"name": "docker", "port": DK, "func": pocs.docker, "level": "low"}
# dicRS = {"name": "rsync", "port": RS, "func": pocs.rsync, "level": "low"}

dicMYS = {"name": "mysql", "port": MYS, "func": pocs.mysql, "level": "mid"}
dicFP = {"name": "ftp", "port": FP, "func": pocs.ftp, "level": "mid"}
dicSP = {"name": "spark", "port": SP, "func": pocs.spark, "level": "mid"}
dicKBN = {"name": "kibana", "port": KBN, "func": pocs.kibana, "level": "mid"}
dicKO = {"name": "kong", "port": KO, "func": pocs.kong, "level": "mid"}
dicES = {"name": "elasticsearch", "port": ES, "func": pocs.elasticsearch, "level": "mid"}
dicCDB = {"name": "couchdb", "port": CDB, "func": pocs.CouchDB, "level": "mid"}
dicDKR = {"name": "docker_registry", "port": DKR, "func": pocs.docker_reg, "level": "mid"}
dicZBX = {"name": "zabbix", "port": ZBX, "func": pocs.zabbix, "level": "mid"}

dicIDB = {"name": "influxdb", "port": IDB, "func": pocs.influxdb, "level": "high"}
dicHDY = {"name": "hadoop_yarn", "port": HDY, "func": pocs.hadoop_yarn, "level": "high"}
dicJKS = {"name": "jenkins", "port": JKS, "func": pocs.jenkins, "level": "high"}
dicDRD = {"name": "druid", "port": DRD, "func": pocs.druid, "level": "high"}
dicSPAPI = {"name": "spark_api", "port": SPAPI, "func": pocs.spark_api, "level": "high"}
dicTB = {"name": "tensorboard", "port": TB, "func": pocs.tensorboard, "level": "high"}
dicJBS = {"name": "jboss", "port": JBS, "func": pocs.jboss, "level": "high"}
dicHDP = {"name": "hadoop", "port": HDP, "func": pocs.Hadoop, "level": "high"}
dicFL = {"name": "flink", "port": FL, "func": pocs.flink, "level": "high"}
dicSLR = {"name": "solr", "port": SLR, "func": pocs.solr, "level": "high"}

dicSB = {"name": "springboot", "port": SB, "func": springboot.sb_Actuator, "level": "springboot"}

dicPROM = {"name": "prometheus", "port": PROM, "func": additional.prometheus, "level": "observe"}
dicAM = {"name": "alertmanager", "port": ALERTMANAGER, "func": additional.alertmanager, "level": "observe"}
dicGF = {"name": "grafana", "port": GRAFANA, "func": additional.grafana, "level": "observe"}
dicCONSUL = {"name": "consul", "port": CONSUL, "func": additional.consul, "level": "infra"}
dicETCD = {"name": "etcd", "port": ETCD, "func": additional.etcd, "level": "infra"}
dicK8S = {"name": "kubernetes_api", "port": K8S, "func": additional.kubernetes_api, "level": "infra"}
dicJUPYTER = {"name": "jupyter", "port": JUPYTER, "func": additional.jupyter, "level": "app"}
dicSWAGGER = {"name": "swagger", "port": SWAGGER, "func": additional.swagger, "level": "app"}
dicNACOS = {"name": "nacos", "port": NACOS, "func": additional.nacos, "level": "app"}
dicRABBIT = {"name": "rabbitmq_management", "port": RABBITMQ, "func": additional.rabbitmq_management, "level": "app"}
dicJAEGER = {"name": "jaeger", "port": JAEGER, "func": additional.jaeger, "level": "observe"}
dicZIPKIN = {"name": "zipkin", "port": ZIPKIN, "func": additional.zipkin, "level": "observe"}

dic_list_low = [dicRD, dicMDB, dicMC, dicZK, dicDK]
dic_list_mid = [dicMYS, dicFP, dicSP, dicKBN, dicKO, dicES, dicCDB, dicDKR, dicZBX]
dic_list_high = [dicIDB, dicHDY, dicJKS, dicDRD, dicSPAPI, dicTB, dicJBS, dicHDP, dicFL, dicSLR]
dic_springboot = [dicSB]
dic_list_extra = [dicPROM, dicAM, dicGF, dicCONSUL, dicETCD, dicK8S, dicJUPYTER, dicSWAGGER, dicNACOS, dicRABBIT, dicJAEGER, dicZIPKIN]
ALL_CHECKS = dic_list_low + dic_list_mid + dic_list_high + dic_springboot + dic_list_extra


def build_port_index(checks=None):
    checks = checks or ALL_CHECKS
    index = {}
    for check in checks:
        for port in check["port"]:
            index.setdefault(str(port), []).append(check)
    return index
