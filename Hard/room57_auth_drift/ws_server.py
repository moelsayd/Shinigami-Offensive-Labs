#!/usr/bin/env python3
import asyncio, websockets, sys, subprocess

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9203
FLAG = "THM{dr1ft_0auth_ws}"
SECRET = "weak_auth_secret"

import json, base64, hmac, hashlib
def b64d(d):
    d += '=' * (4 - len(d) % 4)
    return base64.urlsafe_b64decode(d)
def jwt_verify(token):
    try:
        h, p, sig = token.split(".")
        expected = base64.urlsafe_b64encode(hmac.new(SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
        if sig != expected: return None
        return json.loads(b64d(p))
    except: return None

async def handle(websocket, path):
    token = await websocket.recv()
    payload = jwt_verify(token)
    if not payload or payload.get("role") != "admin":
        await websocket.send("Auth failed")
        return
    while True:
        cmd = await websocket.recv()
        if cmd == "flag":
            await websocket.send(FLAG)
        else:
            try:
                out = subprocess.check_output(cmd, shell=True, timeout=5).decode()
                await websocket.send(out)
            except Exception as e:
                await websocket.send(str(e))

async def main():
    async with websockets.serve(handle, "127.0.0.1", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
