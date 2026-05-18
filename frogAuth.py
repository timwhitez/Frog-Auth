#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import ipaddress
import os
import random
import stat
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit

from banner import banner
from pocs import const, runtime

ROOT = Path(__file__).resolve().parent
TOOL_NAMES = {
    "linux": {"naabu": "naabu_linux", "httpx": "httpx_linux"},
    "win": {"naabu": "naabu_win.exe", "httpx": "httpx_win.exe"},
}
DEFAULT_HTTPX_PORTS = "80,443,8080,8090,8443,9090,8880,2052,2082,2086,2095,2053,2083,2087,2096,3000,5000,5601,8000,8001,8848,8888,9000,9411,15672,16686"


def readf(fname):
    return read_targets(fname)


def read_targets(fname):
    path = Path(fname)
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {fname}")
    seen = set()
    targets = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        item = line.strip()
        if not item or item.startswith("#") or item in seen:
            continue
        seen.add(item)
        targets.append(item)
    return targets


def write_lines(path, lines, append=False):
    mode = "a" if append else "w"
    with Path(path).open(mode, encoding="utf-8") as fw:
        for line in lines:
            if line:
                fw.write(str(line).strip() + "\n")


def tool_path(os_name, tool):
    os_name = os_name.lower()
    if os_name not in TOOL_NAMES:
        raise ValueError("os must be linux or win")
    folder = "ports" if tool == "naabu" else "httpx"
    path = ROOT / folder / TOOL_NAMES[os_name][tool]
    if not path.exists():
        raise FileNotFoundError(f"missing {tool} binary: {path}")
    if os_name == "linux" and not os.access(path, os.X_OK):
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return str(path)


def run_external(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(detail or f"command failed: {' '.join(cmd)}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def normalize_target(value):
    value = str(value).strip().strip("'").strip('"')
    if not value:
        return None
    if "://" in value:
        parsed = urlsplit(value)
        if not parsed.hostname:
            return None
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        host = parsed.hostname
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        return f"{host}:{port}"
    value = value.split("/", 1)[0].strip()
    host, port = runtime.split_target(value)
    if host and port.isdigit():
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        return f"{host}:{port}"
    return None


def normalize_targets(values):
    seen = set()
    normalized = []
    for value in values:
        target = normalize_target(value)
        if target and target not in seen:
            seen.add(target)
            normalized.append(target)
    return normalized


def is_domain_input(value):
    value = value.strip()
    if not value:
        return False
    if "://" in value:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
    else:
        host = value.split("/", 1)[0].split(":", 1)[0]
    try:
        ipaddress.ip_network(host, strict=False)
        return False
    except ValueError:
        return any(ch.isalpha() for ch in host)


def port_scan(file_name, args):
    cmd = [
        tool_path(args.os, "naabu"),
        "-iL",
        str(file_name),
        "-p",
        args.ports,
        "-no-color",
        "-silent",
        "-ping",
        "false",
        "-rate",
        str(args.rate),
    ]
    print("Ports scanning.")
    lines = run_external(cmd)
    targets = normalize_targets(lines)
    write_lines(args.ports_output, targets, append=args.append)
    print(f"Finish ports scan: {len(targets)} open services.")
    return targets


def httpx_scan(inputs, args):
    if args.no_httpx:
        return []
    domains = [item for item in inputs if is_domain_input(item)]
    if not domains:
        return []
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
        tmp.write("\n".join(domains) + "\n")
        tmp_name = tmp.name
    try:
        cmd = [
            tool_path(args.os, "httpx"),
            "-l",
            tmp_name,
            "-ports",
            args.httpx_ports,
            "-threads",
            str(args.httpx_threads),
            "-silent",
            "-no-color",
            "-follow-redirects",
        ]
        print("Httpx scanning.")
        lines = run_external(cmd)
        targets = normalize_targets(lines)
        write_lines(args.http_output, targets, append=args.append)
        print(f"Finish httpx scan: {len(targets)} web services.")
        return targets
    finally:
        try:
            os.remove(tmp_name)
        except OSError:
            pass


def getresult(filename):
    return normalize_targets(read_targets(filename))


def checks_for_target(target, index):
    _, port = runtime.split_target(target)
    return index.get(str(port), [])


def run_check(check, target):
    check["func"](target)


def vulnscan(target):
    index = const.build_port_index()
    for check in checks_for_target(target, index):
        run_check(check, target)


def run_checks(targets, args):
    checks_by_port = const.build_port_index()
    tasks = []
    seen = set()
    for target in targets:
        for check in checks_for_target(target, checks_by_port):
            key = (target, check["name"])
            if key in seen:
                continue
            seen.add(key)
            tasks.append((target, check))
    if args.shuffle:
        random.shuffle(tasks)
    print(f"Component checks: {len(tasks)} tasks across {len(targets)} services, {len(const.ALL_CHECKS)} components.")
    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {pool.submit(run_check, check, target): (target, check) for target, check in tasks}
        for future in as_completed(futures):
            target, check = futures[future]
            try:
                future.result()
            except Exception as exc:
                if args.verbose:
                    print(f"[error] {target} {check['name']}: {exc}")


def build_parser():
    parser = argparse.ArgumentParser(description="Frog-Auth unauthorized access scanner")
    parser.add_argument("os", help="linux/win", choices=("linux", "win"))
    parser.add_argument("-m", help="scan/file", choices=("scan", "file"), default="scan")
    parser.add_argument("-f", help="input filename", default="ip.txt")
    parser.add_argument("-o", "--output", default="results.txt", help="result output file")
    parser.add_argument("--ports-output", default="ports.txt", help="open port output file")
    parser.add_argument("--http-output", default="http.txt", help="httpx normalized output file")
    parser.add_argument("--ports", default=const.all_ports, help="ports passed to naabu")
    parser.add_argument("--httpx-ports", default=DEFAULT_HTTPX_PORTS, help="ports passed to httpx")
    parser.add_argument("--threads", type=int, default=100, help="component check workers")
    parser.add_argument("--timeout", type=float, default=6.0, help="network timeout seconds")
    parser.add_argument("--rate", type=int, default=1000, help="naabu probe rate")
    parser.add_argument("--http-rate", type=float, default=0.0, help="global HTTP request rate limit, 0 disables")
    parser.add_argument("--httpx-threads", type=int, default=300, help="httpx worker count")
    parser.add_argument("--low-noise", action="store_true", help="lower concurrency/rate to reduce target load; not a stealth mode")
    parser.add_argument("--no-httpx", action="store_true", help="skip domain web-service enrichment")
    parser.add_argument("--append", action="store_true", help="append output files instead of overwriting")
    parser.add_argument("--shuffle", action="store_true", help="shuffle component task order")
    parser.add_argument("--user-agent", default=runtime.DEFAULT_USER_AGENT, help="HTTP User-Agent")
    parser.add_argument("--verify-ssl", action="store_true", help="verify TLS certificates")
    parser.add_argument("-v", "--verbose", action="store_true", help="print skipped dependency and check errors")
    return parser


def apply_low_noise(args):
    if not args.low_noise:
        return
    args.threads = min(args.threads, 30)
    args.httpx_threads = min(args.httpx_threads, 80)
    args.rate = min(args.rate, 200)
    if not args.http_rate:
        args.http_rate = 20
    args.timeout = min(args.timeout, 5.0)


def main(argv=None):
    banner.banner()
    parser = build_parser()
    args = parser.parse_args(argv)
    apply_low_noise(args)
    runtime.configure(
        output=args.output,
        timeout=args.timeout,
        verify_ssl=args.verify_ssl,
        user_agent=args.user_agent,
        verbose=args.verbose,
        http_rate=args.http_rate,
        append=args.append,
    )
    try:
        inputs = read_targets(args.f)
        if args.m == "file":
            port_res = getresult(args.f)
            http_res = []
        else:
            port_res = port_scan(args.f, args)
            http_res = httpx_scan(inputs, args)
        all_targets = normalize_targets(port_res + http_res)
        if not all_targets:
            print("No services to check.")
            return 0
        run_checks(all_targets, args)
        print(f"Finished. Results saved to {args.output}")
        return 0
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
