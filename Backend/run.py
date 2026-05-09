"""
Backend Başlatıcı
==================
İki MCP server'ı SSE modunda başlatır, ardından uvicorn'u çalıştırır.
Windows uyumlu: asyncio subprocess YOK, subprocess.Popen kullanılır.

  MCP Review Server → port 8001 (hotel_mcp_server.py)
  MCP Ops Server    → port 8002 (hotel_ops_server.py)
  FastAPI           → port 8000 (app.main:app)

Kullanım:
    python run.py
"""

import sys
import asyncio
import subprocess
import time
import signal
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

_DIR = Path(__file__).parent
_MCP_DIR = _DIR / "app" / "agents" / "mcp"

_SERVERS = [
    (_MCP_DIR / "hotel_mcp_server.py", "8001", "Review"),
    (_MCP_DIR / "hotel_ops_server.py", "8002", "Ops"),
]

procs = []

for server_path, port, label in _SERVERS:
    print(f"[run.py] MCP {label} server başlatılıyor (port {port}): {server_path.name}")
    proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        cwd=str(_DIR),
    )
    procs.append((proc, label, port))

time.sleep(2)

for proc, label, port in procs:
    if proc.poll() is not None:
        print(f"[run.py] HATA: MCP {label} server başlatılamadı, çıkılıyor.")
        for p, _, _ in procs:
            p.terminate()
        sys.exit(1)
    print(f"[run.py] MCP {label} server PID={proc.pid} çalışıyor (port {port})")

import uvicorn


def _shutdown(signum, frame):
    print("\n[run.py] Kapatılıyor...")
    for proc, label, port in procs:
        proc.terminate()
        print(f"[run.py] MCP {label} server durduruldu (port {port})")
    sys.exit(0)


signal.signal(signal.SIGINT, _shutdown)
if sys.platform != "win32":
    signal.signal(signal.SIGTERM, _shutdown)

try:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
finally:
    for proc, label, port in procs:
        proc.terminate()
        proc.wait()
        print(f"[run.py] MCP {label} server durduruldu (port {port})")
