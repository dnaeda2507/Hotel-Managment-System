"""
Hotel Operations MCP Server
============================
Oda, rezervasyon ve operasyon araçları.
Ed Donner pattern: accounts_server.py karşılığı.
Port: 8002 (MCP_OPS_PORT env ile değiştirilebilir)

Tools:
  1. get_room_availability   – Belirtilen tarihlerde müsait odalar
  2. make_reservation        – Yeni rezervasyon oluştur (DB'ye yazar)
  3. get_upcoming_checkouts  – Yaklaşan check-out listesi
  4. get_pending_housekeeping – Temizlik bekleyen odalar
  5. get_open_maintenance    – Açık arıza/bakım talepleri
  6. suggest_room_price      – Doluluk + sezon bazlı dinamik fiyat

Resources:
  hotel://dashboard/today   – Günlük özet (doluluk, rezervasyon, puan, görevler)
  hotel://rooms/available   – Şu an müsait odaların listesi
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
load_dotenv()

MCP_OPS_PORT = int(os.getenv("MCP_OPS_PORT", "8002"))
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5500/hotel_db")

mcp = FastMCP("Hotel Operations Server")
_engine = create_engine(DB_URL)


# ── Tool 1: Oda Müsaitlik ─────────────────────────────────────────────────────
@mcp.tool()
def get_room_availability(check_in: str, check_out: str) -> str:
    """
    Belirtilen tarihlerde rezervasyon çakışması olmayan müsait odaları listele.

    Args:
        check_in:  Giriş tarihi (YYYY-MM-DD)
        check_out: Çıkış tarihi (YYYY-MM-DD)
    """
    try:
        with _engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT r.id, r.room_number, r.room_type, r.capacity,
                       r.price_per_night, r.floor, r.features
                FROM rooms r
                WHERE r.status = 'Aktif'
                  AND r.id NOT IN (
                    SELECT res.room_id FROM reservations res
                    WHERE res.status NOT IN ('iptal_edildi', 'çıkış_yapıldı')
                      AND res.check_in_date  < :co
                      AND res.check_out_date > :ci
                  )
                ORDER BY r.price_per_night
            """), {"ci": check_in, "co": check_out}).fetchall()

        if not rows:
            return f"{check_in} – {check_out} tarihleri arasında müsait oda yok."

        lines = [f"Müsait Odalar ({check_in} → {check_out}, {len(rows)} adet):"]
        for row in rows:
            features = f" | {row[6]}" if row[6] else ""
            lines.append(
                f"  Oda {row[1]} (ID:{row[0]}) | {row[2]} | {row[3]} | "
                f"Kat {row[5]} | {row[4]:.0f}₺/gece{features}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 2: Rezervasyon Oluştur ───────────────────────────────────────────────
@mcp.tool()
def make_reservation(
    room_id: int,
    guest_name: str,
    guest_email: str,
    check_in: str,
    check_out: str,
    guest_phone: str = "",
    special_requests: str = "",
) -> str:
    """
    Yeni rezervasyon oluştur ve veritabanına kaydet.
    Çakışma varsa hata döner, yoksa INSERT yapıp ID'yi döndürür.

    Args:
        room_id:          Oda ID numarası
        guest_name:       Misafirin tam adı
        guest_email:      Misafir e-posta adresi
        check_in:         Giriş tarihi (YYYY-MM-DD)
        check_out:        Çıkış tarihi (YYYY-MM-DD)
        guest_phone:      Telefon numarası (opsiyonel)
        special_requests: Özel istek veya not (opsiyonel)
    """
    try:
        ci = datetime.strptime(check_in, "%Y-%m-%d").date()
        co = datetime.strptime(check_out, "%Y-%m-%d").date()
        nights = (co - ci).days
        if nights <= 0:
            return "Hata: Çıkış tarihi, giriş tarihinden sonra olmalı."

        with _engine.connect() as conn:
            room = conn.execute(
                text("SELECT id, room_number, room_type, price_per_night FROM rooms WHERE id = :rid"),
                {"rid": room_id},
            ).fetchone()
            if not room:
                return f"Hata: ID={room_id} olan oda bulunamadı."

            conflict = conn.execute(text("""
                SELECT id FROM reservations
                WHERE room_id = :rid
                  AND status NOT IN ('iptal_edildi', 'çıkış_yapıldı')
                  AND check_in_date  < :co
                  AND check_out_date > :ci
            """), {"rid": room_id, "ci": check_in, "co": check_out}).fetchone()
            if conflict:
                return f"Hata: Oda {room[1]} bu tarihlerde dolu (Rezervasyon ID={conflict[0]})."

            price_per_night = room[3]
            total_price = price_per_night * nights

            result = conn.execute(text("""
                INSERT INTO reservations
                  (room_id, guest_name, guest_email, guest_phone,
                   check_in_date, check_out_date,
                   price_per_night, total_nights, total_price,
                   status, special_requests)
                VALUES
                  (:room_id, :guest_name, :guest_email, :guest_phone,
                   :ci, :co, :ppn, :nights, :total,
                   'beklemede', :requests)
                RETURNING id
            """), {
                "room_id":      room_id,
                "guest_name":   guest_name,
                "guest_email":  guest_email,
                "guest_phone":  guest_phone,
                "ci":           check_in,
                "co":           check_out,
                "ppn":          price_per_night,
                "nights":       nights,
                "total":        total_price,
                "requests":     special_requests,
            })
            conn.commit()
            new_id = result.fetchone()[0]

        return (
            f"Rezervasyon Oluşturuldu! ID={new_id}\n"
            f"  Misafir : {guest_name} ({guest_email})\n"
            f"  Oda     : {room[1]} ({room[2]})\n"
            f"  Tarih   : {check_in} → {check_out} ({nights} gece)\n"
            f"  Toplam  : {total_price:.0f}₺ ({price_per_night:.0f}₺/gece)\n"
            f"  Durum   : Beklemede"
        )
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 3: Yaklaşan Check-Out'lar ────────────────────────────────────────────
@mcp.tool()
def get_upcoming_checkouts(days: int = 1) -> str:
    """
    Önümüzdeki N günde check-out yapacak misafirleri listele.

    Args:
        days: Kaç gün içindeki check-out'lar (varsayılan 1 = bugün)
    """
    try:
        today = date.today().isoformat()
        until = (date.today() + timedelta(days=days)).isoformat()
        with _engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT res.id, res.guest_name, res.check_out_date,
                       r.room_number, r.room_type, res.total_price, res.status
                FROM reservations res
                JOIN rooms r ON r.id = res.room_id
                WHERE res.check_out_date BETWEEN :today AND :until
                  AND res.status IN ('onaylandı', 'giriş_yapıldı')
                ORDER BY res.check_out_date, r.room_number
            """), {"today": today, "until": until}).fetchall()

        if not rows:
            return f"Önümüzdeki {days} günde check-out yok."

        lines = [f"Yaklaşan Check-Out'lar ({days} gün, {len(rows)} misafir):"]
        for row in rows:
            lines.append(
                f"  Res#{row[0]} | Oda {row[3]} ({row[4]}) | "
                f"{row[1]} | Çıkış: {row[2]} | {row[5]:.0f}₺ | {row[6]}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 4: Temizlik Görevleri ────────────────────────────────────────────────
@mcp.tool()
def get_pending_housekeeping() -> str:
    """
    Temizlik bekleyen veya devam eden oda görevlerini listele.
    Check-out olan odalar otomatik bu listeye düşer.
    """
    try:
        with _engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT ht.id, r.room_number, r.floor, ht.status, ht.notes, ht.created_at
                FROM housekeeping_tasks ht
                JOIN rooms r ON r.id = ht.room_id
                WHERE ht.status IN ('beklemede', 'temizleniyor')
                ORDER BY ht.created_at
            """)).fetchall()

        if not rows:
            return "Tüm odalar temiz — bekleyen temizlik görevi yok."

        lines = [f"Temizlik Bekleyen Odalar ({len(rows)} adet):"]
        for row in rows:
            notes   = f" — {row[4]}" if row[4] else ""
            date_str = str(row[5])[:16] if row[5] else "?"
            lines.append(
                f"  Görev#{row[0]} | Oda {row[1]} (Kat {row[2]}) | {row[3]} | {date_str}{notes}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 5: Bakım Talepleri ───────────────────────────────────────────────────
@mcp.tool()
def get_open_maintenance() -> str:
    """
    Açık veya devam eden teknik arıza/bakım taleplerini öncelik sırasıyla listele.
    """
    try:
        with _engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT mt.id, r.room_number, mt.title, mt.priority, mt.status, mt.created_at
                FROM maintenance_tickets mt
                JOIN rooms r ON r.id = mt.room_id
                WHERE mt.status IN ('açık', 'devam_ediyor')
                ORDER BY
                    CASE mt.priority
                        WHEN 'kritik' THEN 1
                        WHEN 'orta'   THEN 2
                        WHEN 'düşük'  THEN 3
                        ELSE 4
                    END,
                    mt.created_at
            """)).fetchall()

        if not rows:
            return "Açık teknik arıza talebi yok."

        lines = [f"Açık Bakım Talepleri ({len(rows)} adet):"]
        for row in rows:
            date_str = str(row[5])[:10] if row[5] else "?"
            lines.append(
                f"  Ticket#{row[0]} | Oda {row[1]} | [{row[3]}] {row[2]} | {row[4]} | {date_str}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


# ── Tool 6: Dinamik Fiyat Önerisi ─────────────────────────────────────────────
@mcp.tool()
def suggest_room_price(room_id: int) -> str:
    """
    Doluluk oranı, sezon ve hafta sonu çarpanlarına göre dinamik fiyat önerisi hesapla.

    Args:
        room_id: Fiyat önerisi istenecek oda ID'si
    """
    try:
        with _engine.connect() as conn:
            room = conn.execute(
                text("SELECT room_number, room_type, price_per_night FROM rooms WHERE id = :rid"),
                {"rid": room_id},
            ).fetchone()
            if not room:
                return f"Hata: ID={room_id} olan oda bulunamadı."

            occ = conn.execute(text("""
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN is_occupied THEN 1 ELSE 0 END) AS occupied
                FROM rooms WHERE status = 'Aktif'
            """)).fetchone()

        total    = occ[0] or 1
        occupied = occ[1] or 0
        occ_rate = occupied / total

        base = room[2]

        if occ_rate >= 0.90:
            occ_mult, occ_label = 1.35, "Çok Yüksek (≥%90)"
        elif occ_rate >= 0.75:
            occ_mult, occ_label = 1.20, "Yüksek (≥%75)"
        elif occ_rate >= 0.50:
            occ_mult, occ_label = 1.10, "Orta (≥%50)"
        elif occ_rate < 0.25:
            occ_mult, occ_label = 0.90, "Düşük (<%25)"
        else:
            occ_mult, occ_label = 1.00, "Normal"

        month = datetime.now().month
        if month in (6, 7, 8, 12):
            season_mult, season_label = 1.25, "Yüksek Sezon"
        elif month in (1, 2, 11):
            season_mult, season_label = 0.90, "Düşük Sezon"
        else:
            season_mult, season_label = 1.00, "Normal Sezon"

        is_weekend = datetime.now().weekday() >= 5
        weekend_mult = 1.10 if is_weekend else 1.00

        suggested = round(base * occ_mult * season_mult * weekend_mult, -1)

        return (
            f"Fiyat Önerisi — Oda {room[0]} ({room[1]})\n"
            f"  Baz Fiyat     : {base:.0f}₺/gece\n"
            f"  Doluluk       : %{occ_rate * 100:.0f} ({occ_label}) → ×{occ_mult:.2f}\n"
            f"  Sezon         : {season_label} → ×{season_mult:.2f}\n"
            f"  Hafta Sonu    : {'Evet' if is_weekend else 'Hayır'} → ×{weekend_mult:.2f}\n"
            f"  Önerilen Fiyat: {suggested:.0f}₺/gece"
        )
    except Exception as e:
        return f"Hata: {e}"


# ── Resource 1: Günlük Dashboard ──────────────────────────────────────────────
@mcp.resource("hotel://dashboard/today")
def today_dashboard() -> str:
    """
    Günlük otel özeti: doluluk, check-in/out sayısı, ortalama puan, bekleyen görevler.
    Agent konuşma başında bu kaynağı bağlam olarak okur.
    """
    try:
        today = date.today().isoformat()
        with _engine.connect() as conn:
            occ = conn.execute(text("""
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN is_occupied THEN 1 ELSE 0 END) AS occupied
                FROM rooms WHERE status = 'Aktif'
            """)).fetchone()

            checkins = conn.execute(text("""
                SELECT COUNT(*) FROM reservations
                WHERE check_in_date = :today AND status != 'iptal_edildi'
            """), {"today": today}).fetchone()

            checkouts = conn.execute(text("""
                SELECT COUNT(*) FROM reservations
                WHERE check_out_date = :today
                  AND status IN ('onaylandı', 'giriş_yapıldı')
            """), {"today": today}).fetchone()

            avg_rating = conn.execute(text("""
                SELECT ROUND(AVG(rating)::numeric, 1) FROM reviews
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)).fetchone()

            pending_clean = conn.execute(text("""
                SELECT COUNT(*) FROM housekeeping_tasks WHERE status = 'beklemede'
            """)).fetchone()

            open_maint = conn.execute(text("""
                SELECT COUNT(*) FROM maintenance_tickets WHERE status = 'açık'
            """)).fetchone()

        total    = occ[0] or 0
        occupied = occ[1] or 0
        occ_pct  = (occupied / total * 100) if total else 0

        return (
            f"=== OTEL GÜNLÜK ÖZET — {today} ===\n"
            f"Doluluk     : {occupied}/{total} oda (%{occ_pct:.0f})\n"
            f"Bugün Giriş : {checkins[0]} rezervasyon\n"
            f"Bugün Çıkış : {checkouts[0]} rezervasyon\n"
            f"Ort. Puan   : {avg_rating[0] or 'Veri yok'}/5 (son 30 gün)\n"
            f"Temizlik    : {pending_clean[0]} oda bekliyor\n"
            f"Bakım       : {open_maint[0]} açık ticket"
        )
    except Exception as e:
        return f"Dashboard yüklenemedi: {e}"


# ── Resource 2: Şu An Müsait Odalar ──────────────────────────────────────────
@mcp.resource("hotel://rooms/available")
def available_rooms_now() -> str:
    """
    Bugün itibariyle boş olan ve aktif rezervasyonu bulunmayan odaların listesi.
    """
    try:
        today = date.today().isoformat()
        with _engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT r.room_number, r.room_type, r.capacity, r.price_per_night, r.floor
                FROM rooms r
                WHERE r.status = 'Aktif'
                  AND r.is_occupied = false
                  AND r.id NOT IN (
                    SELECT res.room_id FROM reservations res
                    WHERE res.status IN ('onaylandı', 'giriş_yapıldı')
                      AND res.check_in_date  <= :today
                      AND res.check_out_date  > :today
                  )
                ORDER BY r.price_per_night
            """), {"today": today}).fetchall()

        if not rows:
            return "Şu an müsait oda yok."

        lines = [f"Şu An Müsait Odalar ({len(rows)} adet):"]
        for row in rows:
            lines.append(
                f"  Oda {row[0]} | {row[1]} | {row[2]} | Kat {row[4]} | {row[3]:.0f}₺/gece"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"Hata: {e}"


if __name__ == "__main__":
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = MCP_OPS_PORT
    mcp.run(transport="sse")
