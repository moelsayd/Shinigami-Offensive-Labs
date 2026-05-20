#!/usr/bin/env python3
import socket, sys, time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 2222
FLAG = "THM{ssh_w34k_p4ss}"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', PORT))
s.listen(1)
print(f"READY {PORT}", flush=True)   # إشارة تحقق لـ start.sh

while True:
    conn, addr = s.accept()
    with conn:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.10\r\n")
        time.sleep(0.2)
        conn.sendall(b"Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.5.0-14-generic x86_64)\r\n")
        time.sleep(0.2)
        conn.sendall(b"\r\nlogin: ")
        username = conn.recv(1024).decode().strip()
        conn.sendall(b"Password: ")
        password = conn.recv(1024).decode().strip()
        
        if username == "test" and password == "1234":
            conn.sendall(f"\r\nAccess granted! Flag: {FLAG}\r\n".encode())
        else:
            conn.sendall(b"\r\nAccess denied\r\n")
