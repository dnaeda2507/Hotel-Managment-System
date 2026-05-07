"""
Backend Başlatıcı
==================
MCP server'ı SSE/HTTP modunda başlatır, ardından uvicorn'u çalıştırır.
Windows uyumlu: asyncio subprocess YOK, subprocess.Popen kullanılır.

Kullanım (her platformda):
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

_SERVER_DIR = Path(__file__).parent
_MCP_SERVER = _SERVER_DIR / "hotel_mcp_server.py"

# MCP server'ı SSE modunda başlat (subprocess.Popen — Windows güvenli)
print(f"[run.py] MCP server başlatılıyor: {_MCP_SERVER}")
mcp_proc = subprocess.Popen(
    [sys.executable, str(_MCP_SERVER)],
    cwd=str(_SERVER_DIR),
)
time.sleep(2)  # Server'ın dinlemeye başlaması için bekle

if mcp_proc.poll() is not None:
    print("[run.py] HATA: MCP server başlatılamadı, çıkılıyor.")
    sys.exit(1)

print(f"[run.py] MCP server PID={mcp_proc.pid} çalışıyor (port 8001)")

import uvicorn

def _shutdown(signum, frame):
    print("\n[run.py] Kapatılıyor...")
    mcp_proc.terminate()
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
    mcp_proc.terminate()
    mcp_proc.wait()
    print("[run.py] MCP server durduruldu.")
