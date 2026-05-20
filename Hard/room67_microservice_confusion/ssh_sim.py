#!/usr/bin/env python3
import socket, threading, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 10203
FLAG = "THM{m1cr0_id_c0nfus10n}"

def handle(conn, addr):
    try:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1\r\nlogin: ")
        user = conn.recv(1024).decode().strip()
        if user != 'operator': conn.sendall(b"Permission denied.\r\n"); conn.close(); return
        conn.sendall(b"Password: ")
        pwd = conn.recv(1024).decode().strip()
        if pwd != 'micro_pass': conn.sendall(b"Permission denied.\r\n"); conn.close(); return
        conn.sendall(b"\r\noperator@server:~$ ")
        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd: break
            if cmd == 'sudo -l':
                conn.sendall(b"(root) NOPASSWD: /usr/bin/find\r\n")
            elif cmd.startswith('sudo find ') and '/root/flag.txt' in cmd:
                conn.sendall(f"{FLAG}\n".encode())
            elif cmd in ('ls','pwd','whoami'):
                out = {'ls':'root','pwd':'/home/operator','whoami':'operator'}[cmd]
                conn.sendall(out.encode()+b'\r\n')
            else:
                conn.sendall(b"Command not found\r\n")
            conn.sendall(b"operator@server:~$ ")
    except: pass
    finally: conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"SSH on {PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle, args=(conn, addr))
        t.daemon = True; t.start()

if __name__ == "__main__":
    main()
