#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import requests


DEFAULT_USER_AGENT = "Frog-Auth/2.0 (+https://github.com/timwhitez/Frog-Auth)"
DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class RateLimiter:
    def __init__(self, rate: float = 0):
        self.set_rate(rate)
        self._lock = threading.Lock()
        self._next_at = 0.0

    def set_rate(self, rate: float) -> None:
        self.rate = max(float(rate or 0), 0.0)
        self.interval = 1.0 / self.rate if self.rate else 0.0

    def wait(self) -> None:
        if not self.interval:
            return
        with self._lock:
            now = time.monotonic()
            if self._next_at > now:
                time.sleep(self._next_at - now)
                now = time.monotonic()
            self._next_at = now + self.interval


@dataclass
class RuntimeConfig:
    output: Path = Path("results.txt")
    timeout: float = 6.0
    verify_ssl: bool = False
    user_agent: str = DEFAULT_USER_AGENT
    verbose: bool = False
    http_rate: float = 0.0


CONFIG = RuntimeConfig()
_result_lock = threading.Lock()
_result_seen = set()
_thread_local = threading.local()
_rate_limiter = RateLimiter(0)


def configure(
    output: str = "results.txt",
    timeout: float = 6.0,
    verify_ssl: bool = False,
    user_agent: str = DEFAULT_USER_AGENT,
    verbose: bool = False,
    http_rate: float = 0.0,
    append: bool = False,
) -> None:
    global CONFIG, _result_seen
    CONFIG = RuntimeConfig(
        output=Path(output),
        timeout=float(timeout),
        verify_ssl=verify_ssl,
        user_agent=user_agent or DEFAULT_USER_AGENT,
        verbose=verbose,
        http_rate=float(http_rate or 0),
    )
    CONFIG.output.parent.mkdir(parents=True, exist_ok=True)
    if not append:
        CONFIG.output.write_text("", encoding="utf-8")
        _result_seen = set()
    else:
        if CONFIG.output.exists():
            _result_seen = set(x.strip() for x in CONFIG.output.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip())
        else:
            CONFIG.output.touch()
            _result_seen = set()
    socket.setdefaulttimeout(CONFIG.timeout)
    _rate_limiter.set_rate(CONFIG.http_rate)


def headers(extra: Optional[dict] = None) -> dict:
    merged = dict(DEFAULT_HEADERS)
    merged["User-Agent"] = CONFIG.user_agent
    if extra:
        merged.update(extra)
    return merged


def session() -> requests.Session:
    sess = getattr(_thread_local, "session", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update(headers())
        _thread_local.session = sess
    return sess


def request(method: str, url: str, **kwargs) -> requests.Response:
    _rate_limiter.wait()
    kwargs["headers"] = headers(kwargs.get("headers"))
    kwargs["timeout"] = CONFIG.timeout
    kwargs["verify"] = CONFIG.verify_ssl
    return session().request(method, url, **kwargs)


def get(url: str, **kwargs) -> requests.Response:
    return request("GET", url, **kwargs)


def save_result(message: str) -> bool:
    message = str(message).strip()
    if not message:
        return False
    with _result_lock:
        if message in _result_seen:
            return False
        _result_seen.add(message)
        with CONFIG.output.open("a", encoding="utf-8") as fw:
            fw.write(message + "\n")
        return True


def report(message: str) -> None:
    if save_result(message):
        print(message)


def split_target(target: str):
    target = target.strip().strip("/")
    if target.startswith("["):
        host, _, rest = target[1:].partition("]")
        port = rest[1:] if rest.startswith(":") else ""
        return host, port
    if target.count(":") > 1 and not target.rsplit(":", 1)[-1].isdigit():
        return target, ""
    host, sep, port = target.rpartition(":")
    if sep and port.isdigit():
        return host, port
    return target, ""


def is_https_port(port: str, https_ports: Iterable[str]) -> bool:
    return str(port) in {str(p) for p in https_ports}


def base_url(target: str, https_ports: Iterable[str]) -> str:
    host, port = split_target(target)
    scheme = "https" if is_https_port(port, https_ports) else "http"
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    netloc = f"{host}:{port}" if port else host
    return f"{scheme}://{netloc}"


def url_for(target: str, path: str, https_ports: Iterable[str]) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return base_url(target, https_ports) + path


def response_text(resp: requests.Response) -> str:
    try:
        return resp.text or ""
    except Exception:
        return ""


def response_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return None
