#!/usr/bin/env python3
import socket, threading, sys, bcrypt, os, subprocess, re

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11222
ROOM_DIR = os.path.dirname(os.path.abspath(__file__))
FLAG_REAL = "THM{adb_escape_root_flag}"

with open(os.path.join(ROOM_DIR, "adb_hash.txt")) as f:
    HASH = f.read().strip().encode()

def handle_client(conn, addr):
    try:
        conn.settimeout(120)
        conn.sendall(b"Android Debug Bridge (ADB) Shell\r\nPassword: ")
        pwd = conn.recv(1024).decode().strip()
        if not bcrypt.checkpw(pwd.encode(), HASH):
            conn.sendall(b"Authentication failed.\r\n"); conn.close(); return
        conn.sendall(b"\r\nshell@android:/ $ ")
        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                conn.sendall(b"shell@android:/ $ ")
                continue
            if cmd in ('exit', 'quit'):
                conn.sendall(b"Goodbye.\r\n"); break
            # أوامر محدودة
            if cmd == 'id':
                conn.sendall(b"uid=2000(shell) gid=2000(shell)\r\n")
            elif cmd == 'ls':
                conn.sendall(b"acct\r\ncache\r\nconfig\r\ndata\r\ndev\r\netc\r\nmnt\r\nproc\r\nroot\r\nsbin\r\nsdcard\r\nsys\r\nsystem\r\nvendor\r\n")
            elif cmd == 'pwd':
                conn.sendall(b"/\r\n")
            elif cmd == 'whoami':
                conn.sendall(b"shell\r\n")
            elif cmd == 'ps':
                conn.sendall(b"USER           PID  PPID     VSZ   RSS WCHAN            ADDR S NAME\r\n")
                conn.sendall(b"root             1     0   12345  6789 SyS_epoll      0000 S init\r\n")
                conn.sendall(b"shell        1234     1   54321 23456 SyS_epoll      0000 S adbd\r\n")
            elif cmd == 'getprop':
                conn.sendall(b"[ro.build.version.sdk]: [30]\r\n[ro.debuggable]: [1]\r\n")
            elif cmd == 'mount':
                conn.sendall(b"rootfs on / type rootfs (ro)\r\n/dev/root on / type ext4 (ro)\r\n")
            elif cmd == 'uname -a':
                conn.sendall(b"Linux localhost 5.4.0-generic #1 SMP PREEMPT arm64\r\n")
            elif cmd == 'ls /data/system':
                conn.sendall(b"flag.txt\r\n")
            elif cmd.startswith('cat /data/system/flag.txt'):
                conn.sendall(b"cat: /data/system/flag.txt: Permission denied\r\n")
            elif cmd.startswith('find') and '-exec' in cmd:
                # محاكاة SUID find: تنفيذ الأمر بصلاحيات root
                # استخراج الأمر بعد -exec وحتى النهاية
                try:
                    parts = cmd.split('-exec')[1].strip()
                    # نهاية الأمر هي \; أو ; أو +
                    end = parts.find(';')
                    if end != -1:
                        to_exec = parts[:end].strip()
                    else:
                        to_exec = parts.strip()
                    # تنفيذ الأمر كـ subprocess (ولكن هنا نقرأ العلم فقط)
                    # لأغراض تعليمية، نحاكي أن find يسمح بقراءة أي ملف
                    if 'cat' in to_exec:
                        if '/data/system/flag.txt' in to_exec:
                            conn.sendall(FLAG_REAL.encode() + b"\r\n")
                        else:
                            conn.sendall(f"Simulated: {to_exec} executed as root\r\n".encode())
                    else:
                        conn.sendall(f"Simulated: {to_exec} executed as root\r\n".encode())
                except Exception as e:
                    conn.sendall(f"Error: {e}\r\n".encode())
            else:
                conn.sendall(b"rbash: command not found: " + cmd.encode() + b"\r\n")
            conn.sendall(b"shell@android:/ $ ")
    except (ConnectionResetError, socket.timeout, OSError):
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
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
