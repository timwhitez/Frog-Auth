#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

from pocs import const, runtime


pathlist = ["/autoconfig", "/beans", "/configprops", "/dump", "/health", "/info", "/mappings", "/metrics", "/trace"]
HD = runtime.DEFAULT_HEADERS
requests.packages.urllib3.disable_warnings()


def saveinfo(result):
    runtime.save_result(result)


def _report(message):
    runtime.report(message)


def _text(resp):
    return runtime.response_text(resp)


def Jolokiacheck(url):
    try:
        url_tar = url + "/jolokia/list"
        resp = runtime.get(url_tar, allow_redirects=False)
        if resp.status_code != 200:
            return
        body = _text(resp)
        _report(f"springboot-jolokia未授权：{url_tar}")
        if "reloadByURL" in body:
            _report(f"springboot-jolokia 端点存在reloadByURL方法,可进行XXE/RCE测试：{url_tar}")
        if "createJNDIRealm" in body:
            _report(f"springboot-jolokia 端点存在createJNDIRealm方法,可进行JNDI注入RCE测试：{url_tar}")
    except Exception:
        return


def Envcheck_1(url):
    try:
        url_tar = url + "/env"
        resp = runtime.get(url_tar, allow_redirects=False)
        if resp.status_code != 200:
            return
        body = _text(resp)
        _report(f"springboot-env未授权访问：{url_tar}")
        if "spring.cloud.bootstrap.location" in body:
            _report(f"springboot-env 端点spring.cloud.bootstrap.location属性开启,可进行环境属性覆盖RCE测试：{url_tar}")
        if "eureka.client.serviceUrl.defaultZone" in body:
            _report(f"springboot-env 端点eureka.client.serviceUrl.defaultZone属性开启,可进行XStream反序列化RCE测试：{url_tar}")
    except Exception:
        return


def sb1_Actuator(url):
    key = 0
    Envcheck_1(url)
    Jolokiacheck(url)
    for path in pathlist:
        try:
            url_tar = url + path
            resp = runtime.get(url_tar, allow_redirects=False)
            if resp.status_code == 200:
                _report(f"springboot-{path.replace('/', '')} 端点的未授权访问：{url_tar}")
                key = 1
        except Exception:
            continue
    return key


def Envcheck_2(url):
    try:
        url_tar = url + "/actuator/env"
        resp = runtime.get(url_tar, allow_redirects=False)
        if resp.status_code != 200:
            return
        body = _text(resp)
        _report(f"springboot-env 未授权访问：{url_tar}")
        if "spring.cloud.bootstrap.location" in body:
            _report(f"springboot-env 端点spring.cloud.bootstrap.location属性开启,可进行环境属性覆盖RCE测试：{url_tar}")
        if "eureka.client.serviceUrl.defaultZone" in body:
            _report(f"springboot-env 端点eureka.client.serviceUrl.defaultZone属性开启,可进行XStream反序列化RCE测试：{url_tar}")
    except Exception:
        return


def sb2_Actuator(url):
    Envcheck_2(url)
    Jolokiacheck(url + "/actuator")
    for path in pathlist:
        try:
            url_tar = url + "/actuator" + path
            resp = runtime.get(url_tar, allow_redirects=False)
            if resp.status_code == 200:
                _report(f"springboot-{path.replace('/', '')}未授权访问：{url_tar}")
        except Exception:
            continue


def sbcheck(url):
    try:
        resp = runtime.get(url + "/404", allow_redirects=False)
        if resp.status_code in (403, 404):
            body = _text(resp)
            return 1 if "Whitelabel Error Page" in body or "There was an unexpected error" in body else 0
        return 0
    except requests.exceptions.RequestException:
        return 0
    except Exception:
        return 0


def sb_Actuator(target):
    try:
        url = runtime.base_url(target, const.https_ports_set)
        if sbcheck(url) != 1:
            return
        if sb1_Actuator(url) == 0:
            sb2_Actuator(url)
    except Exception:
        return
