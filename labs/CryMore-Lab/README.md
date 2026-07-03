# CryMore Lab

<img width="1024" height="576" alt="image" src="https://github.com/user-attachments/assets/310b6f6c-7766-4e0b-8549-00ed90b2a249" />

A technical analysis and exploit demonstration for the "CryMore" challenge. This lab focuses on intercepting network traffic to bypass a binary's internal killswitch logic.

---

## 🖥️ Machine Specifications

* Target Name: CryMore
* Author: b0bd0g (Everdoh)
* Platform: Multiplatform
* Architecture: x86 
* Language: C/C
* Difficulty: 🟢 1.3/6.0 
* Quality: ⭐ 4.0/5.0 
* Download: https://crackmes.one/download/crackme/69778aa352ed08086d855c77
* Password: crackmes.one

---

## 🔍 Technical Analysis

### 1. Network Behavior
Upon execution, the program attempts to open a TCP connection to `127.0.0.1:44333`. It sends a specific HTTP GET request:
* `GET /neutralize HTTP/1.1`
* `User-Agent: crackme.one` 

### 2. Logic Analysis
The binary uses `strstr` to scan the server's response for the substring `200 OK`. 
* If the substring is found, the "neutralized" path is triggered.
* The response does not need to be a valid HTTP structure; only the literal string must be present.

---

## 🔓 Exploit: Local TCP Spoofing

The bypass was achieved by running a minimal local TCP listener using **Netcat** that replies with the required success string.

### Command:
```bash
while true; do
  printf "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n" | nc -l 127.0.0.1 44333
done
```
### Output
```
Malware successfully neutralized. Good job.
```
