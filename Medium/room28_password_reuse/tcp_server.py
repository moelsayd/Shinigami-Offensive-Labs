#!/usr/bin/env python3
import sys, socket, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6071
FLAG = "THM{p4ssw0rd_r3us3_p1vot}"
CREDS = {"admin": "admin123"}

def handle_client(conn, addr):
    try:
        conn.sendall(b"Internal FTP Service v1.0\r\nLogin: ")
        user = conn.recv(1024).decode().strip()
        conn.sendall(b"Password: ")
        pwd = conn.recv(1024).decode().strip()
        if user in CREDS and CREDS[user] == pwd:
            conn.sendall(b"\r\nAccess granted. Commands: LIST, READ <file>, QUIT\r\n> ")
            while True:
                cmd = conn.recv(1024).decode().strip()
                if not cmd:
                    break
                if cmd.upper() == "QUIT":
                    conn.sendall(b"Goodbye.\n")
                    break
                elif cmd.upper() == "LIST":
                    conn.sendall(b"flag.txt\r\n")
                elif cmd.upper().startswith("READ "):
                    fname = cmd[5:].strip()
                    if fname == "flag.txt":
                        conn.sendall(f"Flag: {FLAG}\r\n".encode())
                    else:
                        conn.sendall(b"File not found.\r\n")
                else:
                    conn.sendall(b"Unknown command.\r\n> ")
        else:
            conn.sendall(b"Access denied.\r\n")
    except:
        pass
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", PORT))
    s.listen(5)
    print(f"TCP service listening on 127.0.0.1:{PORT}", flush=True)
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
