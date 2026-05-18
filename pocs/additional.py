#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pocs import const, runtime


def _url(target, path="/"):
    return runtime.url_for(target, path, const.https_ports_set)


def _json(resp):
    return runtime.response_json(resp)


def _text(resp):
    return runtime.response_text(resp)


def prometheus(target):
    try:
        build_url = _url(target, "/api/v1/status/buildinfo")
        resp = runtime.get(build_url, allow_redirects=False)
        data = _json(resp) or {}
        if resp.status_code == 200 and data.get("status") == "success" and "version" in data.get("data", {}):
            runtime.report(f"{build_url} prometheus未授权/公开访问")
    except Exception:
        return


def alertmanager(target):
    try:
        status_url = _url(target, "/api/v2/status")
        resp = runtime.get(status_url, allow_redirects=False)
        data = _json(resp) or {}
        if resp.status_code == 200 and ("versionInfo" in data or "cluster" in data):
            runtime.report(f"{status_url} alertmanager未授权/公开访问")
    except Exception:
        return


def grafana(target):
    try:
        health_url = _url(target, "/api/health")
        search_url = _url(target, "/api/search")
        health = runtime.get(health_url, allow_redirects=False)
        health_json = _json(health) or {}
        if health.status_code != 200 or "version" not in health_json:
            return
        search = runtime.get(search_url, allow_redirects=False)
        if search.status_code == 200 and isinstance(_json(search), list):
            runtime.report(f"{search_url} grafana匿名访问/未授权API")
    except Exception:
        return


def consul(target):
    try:
        leader_url = _url(target, "/v1/status/leader")
        services_url = _url(target, "/v1/catalog/services")
        leader = runtime.get(leader_url, allow_redirects=False)
        services = runtime.get(services_url, allow_redirects=False)
        if leader.status_code == 200 and services.status_code == 200 and isinstance(_json(services), dict):
            runtime.report(f"{services_url} consul未授权")
    except Exception:
        return


def etcd(target):
    try:
        version_url = _url(target, "/version")
        version = runtime.get(version_url, allow_redirects=False)
        version_json = _json(version) or {}
        if version.status_code == 200 and ("etcdserver" in version_json or "etcdcluster" in version_json):
            keys_url = _url(target, "/v2/keys/")
            keys = runtime.get(keys_url, allow_redirects=False)
            if keys.status_code == 200 and "node" in (_json(keys) or {}):
                runtime.report(f"{keys_url} etcd未授权")
            else:
                runtime.report(f"{version_url} etcd公开访问")
    except Exception:
        return


def kubernetes_api(target):
    try:
        version_url = _url(target, "/version")
        api_url = _url(target, "/api")
        version = runtime.get(version_url, allow_redirects=False)
        api = runtime.get(api_url, allow_redirects=False)
        version_json = _json(version) or {}
        api_json = _json(api) or {}
        if version.status_code == 200 and api.status_code == 200 and "gitVersion" in version_json and api_json.get("kind") == "APIVersions":
            runtime.report(f"{api_url} kubernetes api未授权/公开访问")
    except Exception:
        return


def jupyter(target):
    try:
        api_url = _url(target, "/api")
        contents_url = _url(target, "/api/contents")
        api = runtime.get(api_url, allow_redirects=False)
        contents = runtime.get(contents_url, allow_redirects=False)
        api_json = _json(api)
        contents_json = _json(contents) or {}
        if api.status_code == 200 and isinstance(api_json, dict) and contents.status_code == 200 and "type" in contents_json:
            runtime.report(f"{contents_url} jupyter未授权")
    except Exception:
        return


def swagger(target):
    candidates = (
        ("/v3/api-docs", ("openapi", "paths")),
        ("/v2/api-docs", ("swagger", "paths")),
        ("/swagger-ui/index.html", ("Swagger UI",)),
        ("/swagger-ui.html", ("Swagger UI",)),
    )
    for path, markers in candidates:
        try:
            url = _url(target, path)
            resp = runtime.get(url, allow_redirects=False)
            body = _text(resp)
            data = _json(resp)
            haystack = data if isinstance(data, dict) else body
            if resp.status_code == 200 and all(marker in str(haystack) for marker in markers):
                runtime.report(f"{url} swagger/openapi文档公开访问")
                return
        except Exception:
            continue


def nacos(target):
    candidates = (
        "/nacos/v1/console/server/state",
        "/nacos/v1/ns/operator/metrics",
    )
    for path in candidates:
        try:
            url = _url(target, path)
            resp = runtime.get(url, allow_redirects=False)
            body = _text(resp)
            if resp.status_code == 200 and ("version" in body.lower() or "status" in body.lower() or "serviceCount" in body):
                runtime.report(f"{url} nacos未授权/公开访问")
                return
        except Exception:
            continue


def rabbitmq_management(target):
    try:
        url = _url(target, "/api/overview")
        resp = runtime.get(url, allow_redirects=False)
        data = _json(resp) or {}
        if resp.status_code == 200 and "rabbitmq_version" in data:
            runtime.report(f"{url} rabbitmq-management未授权")
    except Exception:
        return


def jaeger(target):
    try:
        url = _url(target, "/api/services")
        resp = runtime.get(url, allow_redirects=False)
        data = _json(resp) or {}
        if resp.status_code == 200 and "data" in data and isinstance(data.get("data"), list):
            runtime.report(f"{url} jaeger未授权/公开访问")
    except Exception:
        return


def zipkin(target):
    try:
        url = _url(target, "/api/v2/services")
        resp = runtime.get(url, allow_redirects=False)
        data = _json(resp)
        if resp.status_code == 200 and isinstance(data, list):
            runtime.report(f"{url} zipkin未授权/公开访问")
    except Exception:
        return
