#!/usr/bin/env python3
import socket, threading, sys, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6073
FLAG = "THM{r34l_ch4in_ssh_escape}"  # We'll place this in /opt/flag.txt later

# Allowed commands: ls, pwd, less, more, clear, exit
ALLOWED = {b'ls', b'pwd', b'less', b'more', b'clear', b'exit'}

def handle_client(conn, addr):
    try:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1\r\n")
        conn.sendall(b"limited@localhost's password: ")
        pwd = conn.recv(1024).decode().strip()
        if pwd != 'limited123':
            conn.sendall(b"Permission denied.\r\n")
            conn.close()
            return
        conn.sendall(b"\r\nWelcome to Ubuntu 22.04 LTS (GNU/Linux)\r\n")
        conn.sendall(b"limited@localhost:~$ ")

        restricted = True
        while restricted:
            cmd = conn.recv(1024).strip()
            if not cmd:
                break

            # Split command and arguments
            parts = cmd.split()
            if not parts:
                continue
            base = parts[0].lower()

            if base == b'exit':
                conn.sendall(b"logout\r\n")
                break

            if base not in ALLOWED:
                conn.sendall(b"rbash: " + base + b": command not found\r\n")
                conn.sendall(b"limited@localhost:~$ ")
                continue

            # Handle less/more for /opt/flag.txt (allow only if argument is /opt/flag.txt)
            if base in (b'less', b'more'):
                if len(parts) > 1 and parts[1] == b'/opt/flag.txt':
                    # Simulate pager: show flag content directly (like cat) but they need to escape?
                    # In real less, they could do !cat /opt/flag.txt, but here we just output flag.
                    # To make it slightly harder, we require them to type '!cat /opt/flag.txt' inside less.
                    # We'll implement a mini less emulation.
                    conn.sendall(b"Simulating less... Press q to quit, or type !cat /opt/flag.txt and Enter.\r\n")
                    conn.sendall(b"(END) ")
                    # Wait for command inside less
                    inner = conn.recv(1024).strip()
                    if inner.startswith(b'!cat /opt/flag.txt'):
                        conn.sendall(f"Flag: {FLAG}\r\n".encode())
                    else:
                        conn.sendall(b"Unrecognized command.\r\n")
                    conn.sendall(b"limited@localhost:~$ ")
                    continue
                else:
                    conn.sendall(b"Missing file argument.\r\n")
                    conn.sendall(b"limited@localhost:~$ ")
                    continue

            # ls, pwd, clear
            if base == b'ls':
                conn.sendall(b"opt\r\n")
            elif base == b'pwd':
                conn.sendall(b"/home/limited\r\n")
            elif base == b'clear':
                conn.sendall(b"\033[2J\033[H")
            conn.sendall(b"limited@localhost:~$ ")

    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"SSH simulator listening on 127.0.0.1:{PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
