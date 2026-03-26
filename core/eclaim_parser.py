"""e-Claim CSV Parser — Parse real e-Claim export files into CathLabClaim objects."""

import csv
import io
from datetime import datetime

from core.cathlab_models import CathLabClaim


def _parse_datetime(s: str) -> datetime | None:
    if not s or s == "-":
        return None
    for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None


def _parse_float(s: str) -> float:
    if not s or s == "-":
        return 0.0
    return float(s.replace(",", "").strip())


def _parse_list(s: str) -> list[str]:
    if not s or s == "-":
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def parse_eclaim_csv(content: str) -> tuple[list[CathLabClaim], list[dict]]:
    """Parse e-Claim CSV export into CathLabClaim objects.

    Returns (claims, skipped) where skipped is a list of {"row": int, "error": str}.

    Format based on real file: eclaim_11855_IP_25690316_085002242.ecd
    Header row starts with: REP No., ลำดับที่, TRAN_ID, HN, AN, PID, ...
    """
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    # Find header row (contains "REP No." or "TRAN_ID")
    header_idx = None
    for i, row in enumerate(rows):
        row_text = ",".join(row)
        if "REP No." in row_text or "TRAN_ID" in row_text:
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("ไม่พบ header row ในไฟล์ e-Claim CSV")

    # Column mapping based on real e-Claim format
    # REP No.(0), ลำดับที่(1), TRAN_ID(2), HN(3), AN(4), PID(5),
    # ชื่อ-สกุล(6), ประเภทผู้ป่วย(7), วันเข้ารักษา(8), วันจำหน่าย(9),
    # ยอดสุทธิ(10), (11), ยอดค้าง(12), Error Code(13),
    # กองทุนหลัก(14), กองทุนย่อย(15), ประเภทบริการ(16),
    # ... DRG(34), RW(35), ...

    claims = []
    skipped = []

    for row_num, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
        if len(row) < 36:
            continue

        # Skip empty rows
        if not row[3] or not row[4]:  # HN and AN must exist
            continue
        if row[3].strip() == "" or row[4].strip() == "":
            continue

        try:
            admit = _parse_datetime(row[8])
            discharge = _parse_datetime(row[9])

            if not admit or not discharge:
                continue

            # Parse deny codes from กองทุนย่อย column
            deny_codes = _parse_list(row[15]) if len(row) > 15 else []

            # Parse denied items from ประเภทบริการ column
            denied_items = _parse_list(row[16]) if len(row) > 16 else []

            # Check if denied
            is_denied = "DENY" in ",".join(row[:20]).upper()

            claim = CathLabClaim(
                rep_no=row[0].strip() if row[0].strip() else None,
                tran_id=row[2].strip() if len(row) > 2 else None,
                hn=row[3].strip(),
                an=row[4].strip(),
                pid=row[5].strip(),
                patient_name=row[6].strip() if len(row) > 6 else None,
                patient_type=row[7].strip() if len(row) > 7 else "IP",
                admit_date=admit,
                discharge_date=discharge,
                charge_amount=_parse_float(row[10]) if len(row) > 10 else 0,
                principal_dx="",  # Not in CSV — needs HIS lookup
                fund=row[22].strip() if len(row) > 22 else "UCS",
                drg=row[34].strip() if len(row) > 34 else None,
                rw=_parse_float(row[35]) if len(row) > 35 else None,
                deny_codes=deny_codes if is_denied else [],
                denied_items=denied_items if is_denied else [],
            )

            claims.append(claim)

        except (ValueError, IndexError) as e:
            skipped.append({"row": row_num, "error": str(e)})
            continue

    return claims, skipped


def parse_eclaim_csv_file(file_path: str) -> list[CathLabClaim]:
    """Parse e-Claim CSV file from path."""
    with open(file_path, encoding="utf-8-sig") as f:
        content = f.read()
    return parse_eclaim_csv(content)
