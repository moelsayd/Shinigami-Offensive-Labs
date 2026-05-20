#!/usr/bin/env python3
import socket, threading, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7503
FLAG_REAL = "THM{cr0ss_s3rv1ce_r3us3}"

def handle(conn, addr):
    try:
        conn.sendall(b"MySQL 5.7.42-community\r\nUser: ")
        user = conn.recv(1024).decode().strip()
        conn.sendall(b"Password: ")
        pwd = conn.recv(1024).decode().strip()
        if user == "admin" and pwd == "MyS3cr3tP@ss":
            conn.sendall(b"Welcome to MySQL.\r\nmysql> SHOW DATABASES;\r\n+-------------------+\r\n| secret_db         |\r\n+-------------------+\r\nmysql> USE secret_db;\r\nmysql> SELECT flag FROM secrets;\r\n+--------------------------+\r\n| ")
            conn.sendall(f"{FLAG_REAL}".encode())
            conn.sendall(b" |\r\n+--------------------------+\r\n")
        else:
            conn.sendall(b"Access denied.\r\n")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"DB active", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
