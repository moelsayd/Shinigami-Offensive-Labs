#!/usr/bin/env python3
import socket, sys, threading, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
FLAG = "THM{service_fingerprint_basic}"
BANNER = "Welcome to backup service v1.3\r\nEnter command: "

def handle_client(conn, addr):
    try:
        conn.sendall(BANNER.encode())
        data = conn.recv(1024).decode().strip()
        if not data:
            return
        cmd = data.upper()
        if cmd == "HELP":
            resp = "Commands: HELP, STATUS, GET FLAG\r\n"
        elif cmd == "STATUS":
            resp = "Status: Operational\r\n"
        elif cmd == "GET FLAG":
            resp = f"Flag: {FLAG}\r\n"
        else:
            resp = "Unknown command. Type HELP for list.\r\n"
        conn.sendall(resp.encode())
    except Exception:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"Service listening on 127.0.0.1:{PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
