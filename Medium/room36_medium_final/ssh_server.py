#!/usr/bin/env python3
import socket, threading, sys, subprocess

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6089
FLAG = "THM{medium_level_chain_complete}"

def handle_client(conn, addr):
    try:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1\r\n")
        conn.sendall(b"login as: ")
        username = conn.recv(1024).decode().strip()
        if username != 'limited':
            conn.sendall(b"Permission denied.\r\n"); conn.close(); return

        conn.sendall(b"limited@localhost's password: ")
        password = conn.recv(1024).decode().strip()
        if password != 'limited123':
            conn.sendall(b"Permission denied.\r\n"); conn.close(); return

        conn.sendall(b"\r\nWelcome to Ubuntu 22.04 LTS (GNU/Linux)\r\n")
        conn.sendall(b"limited@server:~$ ")

        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                break
            if cmd == 'exit':
                conn.sendall(b"logout\r\n"); break
            elif cmd == 'sudo -l':
                conn.sendall(b"User limited may run the following commands on this host:\n    (root) NOPASSWD: /usr/bin/find\r\n")
            elif cmd.startswith('sudo find '):
                # السماح بقراءة العلم عبر -exec cat أو -exec cat {}
                if '/root/flag.txt' in cmd and ('-exec' in cmd or 'cat' in cmd):
                    conn.sendall(f"{FLAG}\n".encode())
                else:
                    conn.sendall(b"find: missing argument to `-exec'\r\n")
            elif cmd == 'ls -la /root':
                conn.sendall(b"-rw------- 1 root root 33 May 10 12:00 flag.txt\r\n")
            elif cmd in ('ls', 'pwd', 'whoami', 'id'):
                output = {'ls': 'home  root', 'pwd': '/home/limited', 'whoami': 'limited', 'id': 'uid=1000(limited)'}[cmd]
                conn.sendall(output.encode() + b'\r\n')
            else:
                # محاكاة أوامر shell عادية (مقيدة)
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=2, cwd='/tmp')
                    conn.sendall(result)
                except:
                    conn.sendall(b"Command not found\r\n")
            conn.sendall(b"limited@server:~$ ")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"SSH server on 127.0.0.1:{PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
