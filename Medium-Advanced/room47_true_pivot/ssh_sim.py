#!/usr/bin/env python3
import socket, threading, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8103
FLAG = "THM{true_p1v0t_ch4in}"

def handle(conn, addr):
    try:
        conn.sendall(b"SSH-2.0-TruePivot\r\nlogin: ")
        user = conn.recv(1024).decode().strip()
        if user != 'developer':
            conn.sendall(b"Permission denied.\r\n"); conn.close(); return
        conn.sendall(b"Password: ")
        pwd = conn.recv(1024).decode().strip()
        if pwd != 'dev123':
            conn.sendall(b"Permission denied.\r\n"); conn.close(); return

        conn.sendall(b"\r\nWelcome developer. Type 'sudo -l' for priv info.\r\ndeveloper@server:~$ ")

        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd: break
            if cmd == 'sudo -l':
                conn.sendall(b"(root) NOPASSWD: /usr/bin/find\r\n")
            elif cmd.startswith('sudo find ') and '/root/flag.txt' in cmd and '-exec' in cmd:
                conn.sendall(f"{FLAG}\n".encode())
            elif cmd in ('ls', 'pwd', 'whoami'):
                out = {'ls':'root','pwd':'/home/developer','whoami':'developer'}[cmd]
                conn.sendall(out.encode()+b'\r\n')
            else:
                conn.sendall(b"Command not found.\r\n")
            conn.sendall(b"developer@server:~$ ")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print("SSH sim on", PORT, flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
