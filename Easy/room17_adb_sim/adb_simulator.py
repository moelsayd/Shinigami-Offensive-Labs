#!/usr/bin/env python3
import socket, sys, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5555
FLAG = "THM{adb_op3n_d00r}"
BANNER = b"Android Debug Bridge version 1.0.41\n"
SHELL_PROMPT = b"\x1b[1;32m$ \x1b[0m"

def handle_client(conn, addr):
    try:
        conn.sendall(BANNER)
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            if data == "shell":
                conn.sendall(b"Entering shell...\n")
                # fake shell loop
                while True:
                    conn.sendall(SHELL_PROMPT)
                    cmd = conn.recv(1024).decode().strip()
                    if not cmd:
                        break
                    if cmd == "exit":
                        conn.sendall(b"Shell closed.\n")
                        break
                    elif cmd == "cat /sdcard/flag.txt":
                        conn.sendall(f"{FLAG}\n".encode())
                    elif cmd == "ls":
                        conn.sendall(b"flag.txt\n")
                    elif cmd == "pwd":
                        conn.sendall(b"/\n")
                    else:
                        conn.sendall(b"command not found\n")
                break
            else:
                conn.sendall(b"Unknown command. Use 'shell'.\n")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', PORT))
    s.listen(5)
    print(f"ADB simulator listening on 127.0.0.1:{PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
