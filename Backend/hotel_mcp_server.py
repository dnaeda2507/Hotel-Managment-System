"""
Hotel Review MCP Server
========================
Otel müşteri yorumlarını analiz etmek için 6 ayrı MCP tool sunar.
Her tool farklı bir analiz perspektifi sağlar.

Tools:
  1. get_recent_reviews        – Son N günün tüm yorumları
  2. search_reviews            – Anahtar kelimeye göre yorum ara
  3. get_reviews_by_room       – Belirli oda numarasının yorumları
  4. get_reviews_by_rating     – Puan aralığına göre filtrele
  5. get_review_summary_by_category – Temizlik/yemek/personel vb. kategorili özet
  6. get_review_trends         – Haftalık trend karşılaştırması

Çalıştırma: python hotel_mcp_server.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

MCP_PORT = int(os.getenv("MCP_PORT", "8001"))
DB_URL   = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5500/hotel_db")

mcp = FastMCP("Hotel Review Server")


def _conn():
    return create_engine(DB_URL).connect()


# ── Tool 1: Son Yorumlar ──────────────────────────────────────────────────────
@mcp.tool()
def get_recent_reviews(days: int = 30) -> str:
    """
    Son N günde yazılan tüm müşteri yorumlarını getir.
    Genel memnuniyet analizi veya sorun tespiti için kullan.

    Args:
        days: Kaç günlük dönem (varsayılan 30, max önerilen 90)
    """
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with _conn() as conn:
            rows = conn.execute(text("""
                SELECT rm.room_number, rm.room_type,
                       r.text, r.rating, r.created_at
                FROM reviews r
                LEFT JOIN rooms rm ON rm.id = r.room_id
                WHERE r.created_at > :cutoff
                ORDER BY r.created_at DESC
                LIMIT 50
            """), {"cutoff": cutoff}).fetchall()

        if not rows:
            return f"Son {days} günde yorum bulunamadı."

        lines = [f"Son {days} Günün Yorumları ({len(rows)} adet):"]
        for row in rows:
            date_str  = str(row[4])[:10] if row[4] else "?"
            room_info = f"Oda {row[0]} ({row[1]})" if row[0] else "Oda ?"
            rating    = f"⭐{row[3]}/5" if row[3] else ""
            lines.append(f"  [{date_str}] {room_info} {rating}: {str(row[2])[:200]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 2: Anahtar Kelime Arama ──────────────────────────────────────────────
@mcp.tool()
def search_reviews(keyword: str, days: int = 90) -> str:
    """
    Belirtilen anahtar kelimeyi içeren yorumları ara.
    Belirli bir konuya (klima, temizlik, yemek vb.) odaklanmak için kullan.

    Args:
        keyword: Aranacak kelime veya ifade (örn: 'klima', 'kahvaltı', 'kirli')
        days:    Kaç günlük dönemde aranacak (varsayılan 90)
    """
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with _conn() as conn:
            rows = conn.execute(text("""
                SELECT rm.room_number, rm.room_type,
                       r.text, r.rating, r.created_at
                FROM reviews r
                LEFT JOIN rooms rm ON rm.id = r.room_id
                WHERE r.created_at > :cutoff
                  AND LOWER(r.text) LIKE LOWER(:pattern)
                ORDER BY r.created_at DESC
                LIMIT 30
            """), {"cutoff": cutoff, "pattern": f"%{keyword}%"}).fetchall()

        if not rows:
            return f"'{keyword}' kelimesini içeren yorum bulunamadı."

        lines = [f"'{keyword}' içeren yorumlar ({len(rows)} adet):"]
        for row in rows:
            date_str  = str(row[4])[:10] if row[4] else "?"
            room_info = f"Oda {row[0]} ({row[1]})" if row[0] else "Oda ?"
            rating    = f"⭐{row[3]}/5" if row[3] else ""
            lines.append(f"  [{date_str}] {room_info} {rating}: {str(row[2])[:200]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 3: Oda Bazlı Yorumlar ────────────────────────────────────────────────
@mcp.tool()
def get_reviews_by_room(room_number: str) -> str:
    """
    Belirli bir oda numarasına ait tüm yorumları getir.
    Hangi odanın sorunlu olduğunu veya çok beğenildiğini anlamak için kullan.

    Args:
        room_number: Oda numarası (örn: '101', '202', '301')
    """
    try:
        with _conn() as conn:
            rows = conn.execute(text("""
                SELECT rm.room_number, rm.room_type, rm.floor,
                       r.text, r.rating, r.created_at
                FROM reviews r
                JOIN rooms rm ON rm.id = r.room_id
                WHERE rm.room_number = :rnum
                ORDER BY r.created_at DESC
            """), {"rnum": room_number}).fetchall()

        if not rows:
            return f"Oda {room_number} için yorum bulunamadı."

        ratings = [row[4] for row in rows if row[4] is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        avg_str    = f"{avg_rating:.1f}/5" if avg_rating else "Puansız"

        lines = [
            f"Oda {room_number} ({rows[0][1]}, Kat {rows[0][2]}) — {len(rows)} yorum, Ort: ⭐{avg_str}:"
        ]
        for row in rows:
            date_str = str(row[5])[:10] if row[5] else "?"
            rating   = f"⭐{row[4]}/5" if row[4] else ""
            lines.append(f"  [{date_str}] {rating}: {str(row[3])[:200]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 4: Puana Göre Filtrele ───────────────────────────────────────────────
@mcp.tool()
def get_reviews_by_rating(min_rating: int = 1, max_rating: int = 5, days: int = 90) -> str:
    """
    Belirli puan aralığındaki yorumları getir.
    Düşük puanlı şikayetleri (1-2) veya yüksek puanlı övgüleri (4-5) ayrı ayrı incele.

    Args:
        min_rating: Minimum puan (1-5)
        max_rating: Maksimum puan (1-5)
        days:       Kaç günlük dönem (varsayılan 90)
    """
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with _conn() as conn:
            rows = conn.execute(text("""
                SELECT rm.room_number, rm.room_type,
                       r.text, r.rating, r.created_at
                FROM reviews r
                LEFT JOIN rooms rm ON rm.id = r.room_id
                WHERE r.created_at > :cutoff
                  AND r.rating BETWEEN :min_r AND :max_r
                ORDER BY r.rating ASC, r.created_at DESC
                LIMIT 40
            """), {"cutoff": cutoff, "min_r": min_rating, "max_r": max_rating}).fetchall()

        if not rows:
            return f"{min_rating}-{max_rating} puan aralığında yorum bulunamadı."

        label = "Düşük Puanlı" if max_rating <= 2 else ("Yüksek Puanlı" if min_rating >= 4 else "Orta Puanlı")
        lines = [f"{label} Yorumlar ({min_rating}–{max_rating} ⭐, {len(rows)} adet):"]
        for row in rows:
            date_str  = str(row[4])[:10] if row[4] else "?"
            room_info = f"Oda {row[0]}" if row[0] else "?"
            lines.append(f"  [{date_str}] {room_info} ⭐{row[3]}/5: {str(row[2])[:200]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 5: Tüm Yorumları Getir (LLM analiz eder) ────────────────────────────
@mcp.tool()
def get_all_reviews_for_analysis(days: int = 30) -> str:
    """
    Son N günün tüm yorum metnini ve puanını ham olarak döndür.
    LLM bu veriyi okuyarak kendi anlayışıyla kategorize eder ve analiz eder.
    Keyword eşleştirme yapmaz — tüm yorumlar eksiksiz gelir.

    Args:
        days: Kaç günlük dönem (varsayılan 30)
    """
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with _conn() as conn:
            rows = conn.execute(text("""
                SELECT rm.room_number, r.text, r.rating, r.created_at
                FROM reviews r
                LEFT JOIN rooms rm ON rm.id = r.room_id
                WHERE r.created_at > :cutoff
                ORDER BY r.created_at DESC
                LIMIT 100
            """), {"cutoff": cutoff}).fetchall()

        if not rows:
            return f"Son {days} günde yorum bulunamadı."

        lines = [f"Son {days} Günün Yorumları ({len(rows)} adet) — ham veri:"]
        for i, row in enumerate(rows, 1):
            date_str  = str(row[3])[:10] if row[3] else "?"
            room_info = f"Oda {row[0]}" if row[0] else "Oda ?"
            rating    = f"{row[2]}/5 yıldız" if row[2] else "puan yok"
            lines.append(f"\n[{i}] {room_info} | {rating} | {date_str}")
            lines.append(f"    \"{row[1]}\"")
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 6: Trend Analizi ─────────────────────────────────────────────────────
@mcp.tool()
def get_review_trends(weeks: int = 4) -> str:
    """
    Haftalık bazda yorum sayısı ve puan trendini göster.
    Memnuniyetin zamanla artıp azaldığını analiz etmek için kullan.

    Args:
        weeks: Kaç haftalık trend (varsayılan 4, max 12)
    """
    try:
        weeks = min(weeks, 12)
        results = []
        with _conn() as conn:
            for i in range(weeks - 1, -1, -1):
                week_start = datetime.now() - timedelta(weeks=i + 1)
                week_end   = datetime.now() - timedelta(weeks=i)
                row = conn.execute(text("""
                    SELECT COUNT(*), AVG(rating)
                    FROM reviews
                    WHERE created_at >= :ws AND created_at < :we
                """), {"ws": week_start.isoformat(), "we": week_end.isoformat()}).fetchone()

                count  = row[0] or 0
                avg_r  = round(float(row[1]), 1) if row[1] else None
                label  = f"Hafta -{i}" if i > 0 else "Bu Hafta"
                start_str = week_start.strftime("%m/%d")
                results.append((label, start_str, count, avg_r))

        if all(r[2] == 0 for r in results):
            return f"Son {weeks} haftada yorum bulunamadı."

        lines = [f"Son {weeks} Haftalık Yorum Trendi:"]
        lines.append(f"  {'Dönem':<12} {'Tarih':<8} {'Yorum':<8} {'Ort Puan'}")
        lines.append("  " + "-" * 38)
        for label, start_str, count, avg_r in results:
            avg_str = f"⭐{avg_r}/5" if avg_r else "  -  "
            bar     = "█" * count if count <= 15 else "█" * 15 + f"+{count - 15}"
            lines.append(f"  {label:<12} {start_str:<8} {count:<8} {avg_str}  {bar}")

        # Trend yönü
        counts = [r[2] for r in results]
        if len(counts) >= 2:
            trend = "↑ Artıyor" if counts[-1] > counts[0] else ("↓ Azalıyor" if counts[-1] < counts[0] else "→ Sabit")
            lines.append(f"\n  Yorum sayısı trendi: {trend}")

        avgs = [r[3] for r in results if r[3] is not None]
        if len(avgs) >= 2:
            trend_r = "↑ İyileşiyor" if avgs[-1] > avgs[0] else ("↓ Kötüleşiyor" if avgs[-1] < avgs[0] else "→ Sabit")
            lines.append(f"  Memnuniyet trendi: {trend_r}")

        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


if __name__ == "__main__":
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = MCP_PORT
    mcp.run(transport="sse")
