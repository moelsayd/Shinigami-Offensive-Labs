### ☠ Shinigami Offensive Labs

> Realistic offline offensive security labs for hackers, pentesters, and cybersecurity learners.



Shinigami Offensive Labs is a fully local, internet-independent cyber security training platform built to simulate realistic penetration testing scenarios, enterprise environments, authentication systems, API abuse, Android exploitation, privilege escalation, and chained attack paths.

Designed for:

Cybersecurity students

Red teamers

Bug bounty hunters

CTF players

Pentesting enthusiasts

Self-hosted lab lovers


Runs directly on:

📱 Android (Termux)

🐉 Kali Linux

🐧 Most Linux distributions

💻 Low-resource systems


No heavy virtualization required.
No cloud dependency.
No internet required after setup.


---

# 🔥 Why This Project Exists

Most beginner labs teach:

one vulnerability

one flag

one obvious path


Real-world penetration testing does not work like that.

Real environments contain:

misleading clues

reused credentials

inconsistent authorization

partial leaks

chained vulnerabilities

hidden trust boundaries

internal services

race conditions

business logic flaws

ambiguous attack paths


This project was built to train:

analytical thinking

attack chaining

realistic enumeration

offensive decision making

persistence

adversarial reasoning



---

⚡ Core Features

🧠 Realistic attack chains instead of isolated vulnerabilities

🌐 Offline-first architecture

📱 Android/Termux compatible

🐧 Lightweight Linux-native labs

🔐 JWT, OAuth, GraphQL, WebSocket, SSRF, XXE, NoSQLi, SSTI, Race Conditions, and more

🧩 Progressive level unlocking system

🎯 Interactive launcher with scoreboards and room management

🕵️ Deception techniques and fake artifacts

🔥 Enterprise-style infrastructure simulation

⚙️ Minimal hardware requirements

🚫 No Docker dependency required for most rooms

💀 Blackbox and ambiguous penetration testing simulations



---

🧱 Difficulty Structure

Level	Rooms	Focus

🟢 Easy	18	Enumeration, basic web flaws, simple chaining
🟡 Medium	18	JWT, SSRF, SQLi, chaining, internal services
🟠 Medium-Advanced	18	Logic flaws, NoSQLi, SSTI, advanced attack paths
🔴 Hard	18	Enterprise-grade ambiguity, async systems, deserialization
📱 Android-Exam	1	Android APK, ADB, mobile exploitation
♾ Blackbox-Reality-Exam	1	Full blackbox infrastructure simulation


Total Labs: 75


---

🗺 Full Lab Roadmap

🟢 Easy Level

#	Room	Focus

1	Web Enumeration	HTML comments & source inspection
2	Service Fingerprinting	TCP service discovery
3	Hidden Directory	Directory fuzzing
4	Weak Login	Default credentials
5	Info Leakage	backup.zip exposure
6	Robots.txt Discovery	Hidden paths
7	Command Injection	OS command execution
8	Open Directory Listing	File enumeration
9	API Manipulation	Parameter tampering
10	Weak SSH Simulation	Password guessing
11	Default Creds + Hint Leak	Developer notes leakage
12	Git Exposure	Exposed .git repository
13	Combo Exploit	Login + LFI chain
14	Backup Extension Hunting	.bak / .old discovery
15	HTTP Header Leak	Hidden response headers
16	LFI Easy	Path traversal
17	Open ADB Port	Android shell access
18	Easy Final Exam	Multi-step compromise



---

🟡 Medium Level

#	Room	Focus

19	Multi-Stage Leak Chain	robots.txt → backup chain
20	Hidden Admin via JS	JavaScript leakage
21	Weak JWT	Token forgery
22	Combo Attack	Fuzzing + tampering
23	Exposed .env	Sensitive config leaks
24	Mass Assignment	JSON privilege abuse
25	Blind Error SQLi	SQL error inference
26	Upload + SQLi → RCE	Chained exploitation
27	Internal Endpoint Exposure	BOLA / IDOR
28	Password Reuse + Pivoting	Credential reuse
29	Web → SSH → Escape	Multi-service compromise
30	SSRF + Internal Services	Internal pivoting
31	SSRF Filter Bypass	Decimal IP bypass
32	Path Traversal System Leak	Sensitive file exposure
33	Race Condition Login	Session timing abuse
34	Full Pentest Sim	SSH + sudo exploitation
35	Insecure APK Analysis	Android credential extraction
36	Medium Final Exam	Full enterprise chain



---

🟠 Medium-Advanced Level

#	Room	Focus

37	Shadow Data Leak	Archive extraction
38	Frontend Attack Surface	JS config leaks
39	JWT Trust Boundary Break	alg=none abuse
40	API Surface Expansion	API fuzzing
41	Cloud Misconfiguration	AWS key abuse
42	Business Logic PrivEsc	Negative values
43	Blind System Inference	Timing attacks
44	Upload → Execution Chain	MIME bypass
45	Internal Dev Exposure	Metrics token abuse
46	Cross-Service Reuse	Shared credentials
47	True Pivot Attack Chain	SSH pivoting
48	Full Web → System Chain	MD5 cracking + sudo
49	Logic-Based Exploitation	Role confusion
50	SSRF → Cloud Pivot	Metadata abuse
51	Traversal → System Exposure	Config extraction
52	Race Condition + IDOR	Parallel requests
53	ADB + Burp + JWT	Mobile/API chaining
54	Enterprise Capstone	Multi-stage compromise
55	NeoCorp Production Exam	Advanced chain



---

🔴 Hard Level

#	Room	Focus

56	Partial Exposure	Pickle deserialization
57	Authorization Drift	OAuth + WebSocket
58	Token Replay	GraphQL auth flaws
59	Ghost Endpoint Behavior	Cache poisoning
60	Business Logic Conflicts	XXE + refund abuse
61	Inconsistent File Access	Padding Oracle
62	API Schema Mismatch	TOCTOU + CSRF
63	Conditional Logic Injection	YAML deserialization
64	Async Processing Exploit	Container escape
65	Shadow Internal API	Prototype pollution
66	Ambiguous Pre-Exam	SSRF + Pickle
67	Microservice Identity Confusion	JWT kid injection
68	Internal Graph Pivoting	Reverse proxy abuse
69	Race + Logic Hybrid	Multi-layer exploitation
70	Permission Propagation Failure	Auth drift
71	Enterprise Ambiguous Pentest	CRLF + bcrypt
72	ADB Escape & PrivEsc	SUID exploitation
73	EclipseCorp Final Exam	Distributed services



---

📱 Android Exam

#	Room	Focus

74	Compromised Android Enterprise	APK reversing + JWT



---

♾ Blackbox Reality Exam

#	Room	Focus

75	Blackbox Reality Simulation	Full blackbox infrastructure



---

# ⚙ Runtime Requirements

Core Requirements

Bash

Python 3.8+

curl

sqlite3

netcat

unzip

strings

openssl



---

📦 Python Dependencies

Install manually or using:

pip install -r requirements.txt

Main libraries:

jinja2
websockets
pycryptodome
flask
bcrypt


---

🛠 Recommended Pentesting Tools

Tool	Termux	Kali

nmap	pkg install nmap	Preinstalled
gobuster	pkg install gobuster	apt install gobuster
john	pkg install john	apt install john
hashcat	Limited	apt install hashcat
jadx	pkg install jadx	apt install jadx
metasploit	pkg install metasploit	Preinstalled



---

📱 Termux Installation

pkg update -y && pkg upgrade -y

pkg install -y \
bash \
python \
git \
curl \
wget \
netcat-openbsd \
nmap \
openssl \
grep \
sed \
awk \
findutils \
coreutils \
unzip \
tar \
sqlite

pip install --upgrade pip


---

🐉 Kali Linux Installation

sudo apt update

sudo apt install -y \
python3 \
python3-pip \
curl \
wget \
netcat \
sqlite3 \
nmap \
gobuster \
john \
hashcat \
openssl \
unzip


---

🚀 Launching The Platform

1) Clone or extract the project

git clone <repo-url> ~/ctf-labs

or manually place the folder in:

~/ctf-labs


---

2) Make the launcher executable

chmod +x ~/ctf-labs/launcher.sh


---

3) Start the launcher

~/ctf-labs/launcher.sh


---

🎮 Platform Features

The launcher includes:

Interactive menus

Automatic room startup/shutdown

Progressive unlocking

Integrated scoreboard

Hint system

Offline room management

Terminal UI

Support for Android & Linux environments



---

🧠 Design Philosophy

> “Real penetration testing is ambiguous.”



Advanced rooms intentionally contain:

false positives

misleading artifacts

dead ends

incomplete context

hidden trust relationships

indirect exploitation paths


The goal is not just exploitation.

The goal is learning:

how attackers think

how systems fail

how trust breaks

how small leaks become full compromises



---

🔒 Safety Notice

This project is intended strictly for:

local practice

offline training

controlled environments

cybersecurity education


Do not deploy these labs on public infrastructure.


---

❤️ Community Support

Shinigami Offensive Labs is community-supported.

If the labs helped you learn, improve, or grow:

contribute ideas

improve rooms

report bugs

or support future infrastructure & development


📱 Vodafone Cash / Wallet:

01093963670


---

📜 License

Open-source educational project.

Use it. Modify it. Expand it. Break it. Learn from it.


---

☠ Shinigami Offensive Labs v1.0

> Built for hackers, learners, and architects of chaos. 💀🔥
