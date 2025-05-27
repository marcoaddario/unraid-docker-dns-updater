#!/usr/bin/env python3
import json
import os
import re
import sys
import signal
import time
import docker
import logging
import threading
import requests

CONFIG_PATH = "/boot/config/plugins/dns-watcher/config.json"
client = docker.from_env()
logger = logging.getLogger("dns-watcher")
logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address="/dev/log")
logger.addHandler(handler)

def log(msg): logger.info(f"dns-watcher: {msg}")

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def sanitize(name):
    return re.sub(r"[^a-z0-9-]", "", name.lower())

def build_fqdn(labels, container_name, config):
    hostname = labels.get("dns.hostname", container_name)
    domain = labels.get("dns.domain", config.get("DEFAULT_DOMAIN", ""))
    hostname = sanitize(config.get("hostname_prefix", "") + hostname + config.get("hostname_suffix", ""))
    domain = sanitize(domain)
    if not hostname or not domain:
        return None
    return f"{hostname}.{domain}"

def register_dns(fqdn, ip, record_type, config):
    url = config["DNS_API_URL"]
    headers = { "Authorization": f"Bearer {config['API_KEY']}" }
    payload = {
        "records": [{
            "name": fqdn,
            "type": record_type,
            "value": ip
        }]
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            log(f"✅ Registered {fqdn} → {ip}")
        else:
            log(f"❌ Failed to register {fqdn}: {r.text}")
    except Exception as e:
        log(f"❌ Exception: {e}")

def handle_event(event, config):
    if event["Type"] != "container" or event["Action"] != "start":
        return
    try:
        container = client.containers.get(event["id"])
        labels = container.labels
        if labels.get("dns-watcher.enable", "false").lower() != "true":
            return
        fqdn = build_fqdn(labels, container.name, config)
        if not fqdn:
            log(f"⚠️ Invalid FQDN for {container.name}")
            return
        ip = container.attrs['NetworkSettings']['IPAddress']
        record_type = labels.get("dns.type", "A")
        register_dns(fqdn, ip, record_type, config)
    except Exception as e:
        log(f"❌ Error handling event: {e}")

def watch_config(reload_cb):
    last = os.stat(CONFIG_PATH).st_mtime
    while True:
        time.sleep(2)
        if os.stat(CONFIG_PATH).st_mtime != last:
            last = os.stat(CONFIG_PATH).st_mtime
            reload_cb()

def main():
    config = load_config()
    def reload_config(): nonlocal config; config = load_config(); log("🔄 Reloaded config")
    threading.Thread(target=watch_config, args=(reload_config,), daemon=True).start()
    log("🔍 Watching Docker events...")
    for event in client.events(decode=True):
        handle_event(event, config)

def handle_signal(sig, frame):
    log("👋 Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    main()
