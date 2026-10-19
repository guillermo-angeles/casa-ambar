import base64
import json
import os
import socket
import ssl
from urllib.parse import urlsplit
import struct
import subprocess
import sys

URL = urlsplit(os.environ.get("HA_URL", "http://homeassistant.invalid:8123"))


def send(sock, payload):
    data = json.dumps(payload).encode()
    header = bytearray([0x81])
    n = len(data)
    if n < 126:
        header.append(0x80 | n)
    elif n < 65536:
        header.append(0x80 | 126)
        header += struct.pack(">H", n)
    else:
        header.append(0x80 | 127)
        header += struct.pack(">Q", n)
    mask = os.urandom(4)
    sock.sendall(bytes(header) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def read_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("closed")
        buf += chunk
    return buf


def recv(sock):
    message = b""
    while True:
        b1, b2 = read_exact(sock, 2)
        n = b2 & 0x7F
        if n == 126:
            n = struct.unpack(">H", read_exact(sock, 2))[0]
        elif n == 127:
            n = struct.unpack(">Q", read_exact(sock, 8))[0]
        message += read_exact(sock, n)
        if b1 & 0x80:
            return json.loads(message)


def connect():
    if URL.scheme not in ("http", "https") or not URL.hostname or URL.hostname.endswith(".invalid") or URL.path not in ("", "/") or URL.query or URL.fragment or URL.username or URL.password:
        raise ValueError("Configura HA_URL con el origen HTTP(S) de HA, sin credenciales ni ruta")
    token = subprocess.run(["security", "find-generic-password", "-s", os.environ.get("HA_TOKEN_SERVICE", "casa-ambar-token"), "-w"], capture_output=True, text=True, check=True).stdout.strip()
    if not token:
        raise ValueError("Token no disponible en el Llavero")
    sock = socket.create_connection((URL.hostname, URL.port or (443 if URL.scheme == "https" else 80)), timeout=600)
    if URL.scheme == "https":
        sock = ssl.create_default_context().wrap_socket(sock, server_hostname=URL.hostname)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall(f"GET /api/websocket HTTP/1.1\r\nHost: {URL.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(1)
        if not chunk or len(resp) > 16384:
            raise ConnectionError("Handshake incompleto")
        resp += chunk
    recv(sock)
    send(sock, {"type": "auth", "access_token": token})
    if recv(sock).get("type") != "auth_ok":
        sys.exit("auth failed")
    return sock


def main():
    sock = connect()
    commands = json.load(sys.stdin)
    results = []
    for i, cmd in enumerate(commands, start=1):
        send(sock, {"id": i, **cmd})
        while True:
            msg = recv(sock)
            if msg.get("id") == i and msg.get("type") == "result":
                results.append({"success": msg.get("success"), "result": msg.get("result"), "error": msg.get("error")})
                break
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
