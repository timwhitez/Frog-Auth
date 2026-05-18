#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ftplib
import socket

from pocs import const, runtime

try:
    import pymongo
except ImportError:
    pymongo = None

try:
    import pymysql
except ImportError:
    pymysql = None

try:
    from pyzabbix import ZabbixAPI
except ImportError:
    ZabbixAPI = None


HD = runtime.DEFAULT_HEADERS


def rFile(strw):
    runtime.save_result(strw)


def _url(target, path="/"):
    return runtime.url_for(target, path, const.https_ports_set)


def _text(resp):
    return runtime.response_text(resp)


def _json(resp):
    return runtime.response_json(resp)


def _debug_missing(name):
    if runtime.CONFIG.verbose:
        print(f"[skip] {name} dependency is not installed")


def redis(target):
    try:
        ip, port = runtime.split_target(target)
        with socket.create_connection((ip, int(port)), timeout=runtime.CONFIG.timeout) as s:
            s.sendall(b"INFO\r\n")
            result = s.recv(2048).decode(errors="ignore")
        if "redis_version" in result:
            runtime.report(f"{target} redis未授权")
    except Exception:
        return


def mongodb(target):
    if pymongo is None:
        _debug_missing("pymongo")
        return
    try:
        ip, port = runtime.split_target(target)
        timeout_ms = int(runtime.CONFIG.timeout * 1000)
        conn = pymongo.MongoClient(ip, int(port), socketTimeoutMS=timeout_ms, serverSelectionTimeoutMS=timeout_ms)
        conn.list_database_names()
        runtime.report(f"{target} mongodb未授权")
        conn.close()
    except Exception:
        return


def memcached(target):
    try:
        ip, port = runtime.split_target(target)
        with socket.create_connection((ip, int(port)), timeout=runtime.CONFIG.timeout) as s:
            s.sendall(b"stats\r\n")
            result = s.recv(2048).decode(errors="ignore")
        if "version" in result:
            runtime.report(f"{target} memcached未授权")
    except Exception:
        return


def elasticsearch(target):
    try:
        root = runtime.get(_url(target, "/"), allow_redirects=False)
        cat = runtime.get(_url(target, "/_cat"), allow_redirects=False)
        if "You Know, for Search" in _text(root) and "/_cat/master" in _text(cat):
            runtime.report(f"{_url(target, '/_cat')} elasticsearch未授权")
    except Exception:
        return


def zookeeper(target):
    try:
        ip, port = runtime.split_target(target)
        with socket.create_connection((ip, int(port)), timeout=runtime.CONFIG.timeout) as s:
            s.sendall(b"envi")
            data = s.recv(2048).decode(errors="ignore")
        if "Environment" in data:
            runtime.report(f"{target} zookeeper未授权")
    except Exception:
        return


def ftp(target):
    try:
        ip, port = runtime.split_target(target)
        client = ftplib.FTP()
        client.connect(ip, int(port), timeout=runtime.CONFIG.timeout)
        client.login("anonymous", "anonymous@")
        client.quit()
        runtime.report(f"{target} FTP未授权")
    except Exception:
        return


def CouchDB(target):
    try:
        url = _url(target, "/_config")
        resp = runtime.get(url, allow_redirects=False)
        body = _text(resp)
        if resp.status_code == 200 and all(x in body for x in ("httpd_design_handlers", "external_manager", "replicator_manager")):
            runtime.report(f"{url} CouchDB未授权")
    except Exception:
        return


def docker(target):
    try:
        info_url = _url(target, "/info")
        version_url = _url(target, "/version")
        info = runtime.get(info_url, allow_redirects=False)
        version = runtime.get(version_url, allow_redirects=False)
        info_json = _json(info) or {}
        version_json = _json(version) or {}
        if "ApiVersion" in version_json and "KernelVersion" in info_json and "RegistryConfig" in info_json:
            runtime.report(f"{info_url} docker api未授权")
    except Exception:
        return


def Hadoop(target):
    try:
        url = _url(target, "/dfshealth.html")
        resp = runtime.get(url, allow_redirects=False)
        if resp.status_code == 200 and "hadoop.css" in _text(resp):
            runtime.report(f"{url} Hadoop未授权")
    except Exception:
        return


def hadoop_yarn(target):
    try:
        url = _url(target, "/ws/v1/cluster/info")
        resp = runtime.get(url)
        data = _json(resp) or {}
        body = _text(resp)
        if resp.status_code == 200 and ("resourceManagerVersionBuiltOn" in body or "clusterInfo" in data) and "hadoopVersion" in body:
            runtime.report(f"{url} Hadoop yarn未授权")
    except Exception:
        return


def docker_reg(target):
    try:
        root_url = _url(target, "/v2/")
        catalog_url = _url(target, "/v2/_catalog")
        root = runtime.get(root_url, allow_redirects=False)
        catalog = runtime.get(catalog_url, allow_redirects=False)
        catalog_json = _json(catalog) or {}
        headers = {k.lower(): v for k, v in root.headers.items()}
        if "docker-distribution-api-version" in headers and "repositories" in catalog_json:
            runtime.report(f"{root_url} docker-registry-api未授权")
    except Exception:
        return


def zabbix(target):
    if ZabbixAPI is None:
        _debug_missing("pyzabbix")
        return
    try:
        urls = [_url(target, "/zabbix"), _url(target, "/")]
        pages = []
        for url in urls:
            try:
                pages.append((url, runtime.get(url, allow_redirects=True)))
            except Exception:
                pass
        if not any("zabbix" in _text(resp).lower() for _, resp in pages):
            return
        for url, _ in pages:
            try:
                zapi = ZabbixAPI(url)
                zapi.session.verify = runtime.CONFIG.verify_ssl
                zapi.timeout = runtime.CONFIG.timeout
                zapi.login("Admin", "zabbix")
                runtime.report(f"{url} zabbix默认密码Admin/zabbix")
                return
            except Exception:
                continue
    except Exception:
        return


def influxdb(target):
    try:
        ping_url = _url(target, "/ping")
        query_url = _url(target, "/query?q=show%20users")
        ping = runtime.get(ping_url)
        query = runtime.get(query_url)
        body = _text(query)
        if "X-Influxdb-Version" in ping.headers and "columns" in body and "user" in body:
            runtime.report(f"{query_url} influxdb未授权")
    except Exception:
        return


def druid(target):
    try:
        url = _url(target, "/druid/index.html")
        resp = runtime.get(url)
        body = _text(resp)
        if resp.status_code == 200 and all(x in body for x in ("Druid Stat Index", "DruidVersion", "DruidDrivers")):
            runtime.report(f"{url} druid-monitor未授权")
    except Exception:
        return


def jboss(target):
    try:
        url = _url(target, "/jmx-console/")
        resp = runtime.get(url, allow_redirects=False)
        body = _text(resp)
        if resp.status_code == 200 and "jboss.management.local" in body and "jboss.web" in body:
            runtime.report(f"{url} jboss未授权")
    except Exception:
        return


def jenkins(target):
    try:
        url = _url(target, "/systemInfo")
        resp = runtime.get(url, allow_redirects=False)
        body = _text(resp)
        if resp.status_code == 200 and "jenkins.war" in body and "JENKINS_HOME" in body:
            runtime.report(f"{url} jenkins未授权")
    except Exception:
        return


def rsync(target):
    runtime.report(f"{target} 可能存在rsync未授权")


def mysql(target):
    if pymysql is None:
        _debug_missing("pymysql")
        return
    try:
        ip, port = runtime.split_target(target)
        for user, password, label in (("root", "", "mysql空口令漏洞"), ("root", "root", "mysql root:root口令漏洞")):
            try:
                conn = pymysql.connect(
                    host=ip,
                    port=int(port),
                    user=user,
                    password=password,
                    charset="utf8",
                    autocommit=True,
                    connect_timeout=int(runtime.CONFIG.timeout),
                    read_timeout=int(runtime.CONFIG.timeout),
                    write_timeout=int(runtime.CONFIG.timeout),
                )
                conn.close()
                runtime.report(f"{target} 存在{label}")
                return
            except Exception:
                continue
    except Exception:
        return


def kibana(target):
    try:
        candidates = [_url(target, "/app/kibana"), _url(target, "/app/home")]
        for url in candidates:
            resp = runtime.get(url, allow_redirects=False)
            body = _text(resp)
            if resp.status_code in (200, 302) and (".kibanaWelcomeView" in body or "kbn-injected-metadata" in body or "Kibana" in body):
                runtime.report(f"{url} kibana未授权/可访问")
                return
    except Exception:
        return


def kong(target):
    try:
        status_url = _url(target, "/status")
        resp = runtime.get(status_url)
        body = _text(resp)
        data = _json(resp) or {}
        if resp.status_code == 200 and ("kong_db_cache_miss" in body or "database" in data or "server" in data):
            runtime.report(f"{status_url} kong未授权")
    except Exception:
        return


def spark_api(target):
    for scheme in ("http", "https"):
        try:
            ip, port = runtime.split_target(target)
            host = f"[{ip}]" if ":" in ip and not ip.startswith("[") else ip
            url = f"{scheme}://{host}:{port}/v1/submissions"
            resp = runtime.get(url)
            if resp.status_code == 400 and "serverSparkVersion" in _text(resp):
                runtime.report(f"{url} spark_api未授权")
                return
        except Exception:
            continue


def spark(target):
    try:
        url = _url(target, "/")
        resp = runtime.get(url)
        body = _text(resp)
        if resp.status_code == 200 and "<title>Spark" in body and "<strong>URL:</strong> spark:" in body:
            runtime.report(f"{url} spark未授权")
    except Exception:
        return


def tensorboard(target):
    try:
        root_url = _url(target, "/")
        plugin_url = _url(target, "/data/plugins_listing")
        root = runtime.get(root_url)
        plugins = runtime.get(plugin_url)
        body = _text(root)
        data = _json(plugins) or {}
        if root.status_code == 200 and "TensorFlow" in body and ("profile" in str(data) or "distributions" in str(data)):
            runtime.report(f"{plugin_url} tensorboard未授权")
    except Exception:
        return


def flink(target):
    try:
        url = _url(target, "/jars/")
        resp = runtime.get(url)
        content_type = resp.headers.get("Content-Type", "")
        if resp.status_code == 200 and "application/json" in content_type and "address" in _text(resp):
            runtime.report(f"{url} flink未授权")
    except Exception:
        return


def solr(target):
    for path in ("/solr", "/Solr", "/"):
        try:
            url = _url(target, path)
            resp = runtime.get(url)
            body = _text(resp)
            if resp.status_code == 200 and (
                "<title>Solr Admin</title>" in body
                or "app_config.solr_path" in body
                or "<span>Solr Query Syntax</span>" in body
            ):
                runtime.report(f"{url} solr未授权")
                return
        except Exception:
            continue
