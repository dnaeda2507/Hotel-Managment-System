#!/usr/bin/env python
"""
Sadece local test için.
Terminalde çalıştır:
    python main.py
    python main.py --start 2025-08-01 --end 2025-08-07
"""
import sys
import os
import argparse
from datetime import date, timedelta

# Backend root'u path'e ekle (app.* import'ları çalışsın)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.database import SessionLocal
from run import run_pricing_crew


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, help="YYYY-MM-DD")
    parser.add_argument("--end",   type=str, help="YYYY-MM-DD")
    args = parser.parse_args()

    start = args.start or (date.today() + timedelta(days=1)).isoformat()
    end   = args.end   or (date.today() + timedelta(days=7)).isoformat()

    db = SessionLocal()
    try:
        result = run_pricing_crew(start, end, db)
        print("\n=== PRICE SUGGESTIONS ===")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        db.close()