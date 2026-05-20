#!/usr/bin/env python3
import subprocess
import socket
import sys
import os
import threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7777
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_FILE = os.path.join(ROOM_DIR, "flag.txt")

def get_flag():
    try:
        with open(FLAG_FILE, 'r') as f:
            return f.read().strip()
    except:
        return "FLAG_NOT_FOUND"

FLAG = get_flag()

def handle_client(conn, addr):
    try:
        conn.settimeout(30)
        conn.sendall(b"Welcome to the command injection lab!\n")
        conn.sendall(b"Try commands like: ls, whoami, cat flag.txt\n")
        conn.sendall(b"Enter command: ")
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                conn.sendall(b"Enter command: ")
                continue
            if data.lower() in ('exit', 'quit'):
                conn.sendall(b"Goodbye.\n")
                break
            try:
                output = subprocess.check_output(
                    data, shell=True, stderr=subprocess.STDOUT, timeout=10
                )
                conn.sendall(output)
            except subprocess.CalledProcessError as e:
                conn.sendall(e.output)
            except subprocess.TimeoutExpired:
                conn.sendall(b"[!] Command timed out.\n")
            except Exception as e:
                conn.sendall(f"[!] Error: {e}\n".encode())
            conn.sendall(b"\nEnter command: ")
    except (ConnectionResetError, socket.timeout, OSError):
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"Vulnerable server listening on 127.0.0.1:{PORT}", file=sys.stderr)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
