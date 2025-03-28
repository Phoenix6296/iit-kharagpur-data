
---

# 🚀 **BlinkDB: In-Memory Key-Value Store using RESP-2 Protocol**

## 🛠️ **Getting Started**

### 1. **Prerequisites**
- g++ (with C++17 support)
- `make` utility
- `redis-cli` for client interaction (install via `brew install redis` or `apt-get install redis-tools`)

---

## 🏗️ **Build and Run**

### 1. **Generate Documentation**
```bash
make doc
```
- HTML documentation available at `docs/html/index.html`
- PDF documentation available at `docs/latex/report.pdf` (if LaTeX is enabled)

### 2. **Run the Server**
```bash
make run
```
- The server will start listening on **port 9001**.

### 3. **Create Documentation and Run the Server**
```bash
make
```
- The server will create the documentation and start listening on **port 9001**.

---

## 🔥 **Client Interaction**

1. Open a **new terminal** and run:
```bash
redis-cli -p 9001
```
2. Start issuing commands:
```bash
SET key1 "value1"
GET key1
DEL key1
```

---

## 📊 **Benchmarking**

To run performance benchmarks using `redis-benchmark`:
```bash
make benchmark
```
- Results are stored in the `../result` directory.

---

## 🛑 **Troubleshooting**

### 1. **Port Already in Use Error**
If you encounter:
```
bind failed: Address already in use
```
Kill the process using the port:
```bash
lsof -i :9001
```
Then kill the process:
```bash
kill -9 <process_id>
```

### 2. **Failed to Bind Server**
If the server fails to start:
- Verify that no other service is running on port `9001` by checking:
```bash
lsof -i :9001
```

---

## 🧹 **Cleaning Up**
To clean the build files and benchmark reports:
```bash
make clean
```