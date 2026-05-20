#!/usr/bin/env python3
import socket, threading, sys, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8702
ROOM = os.path.dirname(os.path.abspath(__file__))
APK_PATH = os.path.join(ROOM, "fake_app.apk")

def handle(conn, addr):
    try:
        conn.settimeout(5)
        conn.sendall(b"Android Debug Bridge version 1.0.41\n")
        data = conn.recv(4096).decode(errors='ignore').strip()
        if "pull" in data and "/data/app/base.apk" in data:
            if os.path.exists(APK_PATH):
                with open(APK_PATH, "rb") as f:
                    content = f.read()
                conn.sendall(f"OKAY{len(content):08x}".encode() + content)
            else:
                conn.sendall(b"FAIL file not found")
        else:
            conn.sendall(b"ERR unknown command\n")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"ADB sim on {PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
