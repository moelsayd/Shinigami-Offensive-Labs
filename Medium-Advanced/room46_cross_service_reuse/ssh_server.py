#!/usr/bin/env python3
import socket, threading, sys ,os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7502
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{cr0ss_s3rv1ce_r3us3}"

CREDS = {"admin": "MyS3cr3tP@ss"}  # معاد استخدامها

def handle(conn, addr):
    try:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1\r\nlogin: ")
        user = conn.recv(1024).decode().strip()
        conn.sendall(b"Password: ")
        pwd = conn.recv(1024).decode().strip()
        if user in CREDS and CREDS[user] == pwd:
            conn.sendall(b"\r\nWelcome. You have mail: ")
            conn.sendall(f"Flag: {FLAG_REAL}\r\n".encode())
        else:
            conn.sendall(b"Permission denied.\r\n")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"SSH active", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
