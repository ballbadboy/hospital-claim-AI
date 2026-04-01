"""DRG Calculator — Lookup RW from Thai DRG v6.3.3 Appendix G + payment calculation."""

from core.cathlab_models import DRGInfo

BASE_RATE_IN_ZONE = 8_350    # ปีงบ 69
BASE_RATE_OUT_ZONE = 9_600   # ปีงบ 69

# Cardiac DRG RW Table (MDC 05) — from Thai DRG v6.3.3 Appendix G
CARDIAC_DRG_TABLE: dict[str, dict] = {
    # PCI + Acute MI
    "05259": {"rw": 32.5414, "wtlos": 22.89, "ot": 69, "rw0d": 14.3182, "of": 1.00, "desc": "Acute MI w CAB or VSD repair w PTCA"},
    "05269": {"rw": 22.2634, "wtlos": 21.59, "ot": 65, "rw0d": 9.7959, "of": 1.00, "desc": "Acute MI w CAB or VSD repair wo PTCA"},
    "05270": {"rw": 10.0192, "wtlos": 4.31, "ot": 13, "rw0d": 9.1175, "of": 0.98, "desc": "Acute MI w multiple vessel PTCA wo sig CCC"},
    "05271": {"rw": 12.1597, "wtlos": 8.90, "ot": 27, "rw0d": 10.2141, "of": 1.00, "desc": "Acute MI w multiple vessel PTCA w min CCC"},
    "05290": {"rw": 8.6544, "wtlos": 3.57, "ot": 11, "rw0d": 7.8755, "of": 1.00, "desc": "Acute MI w single vessel PTCA wo sig CCC"},
    "05291": {"rw": 11.4820, "wtlos": 6.54, "ot": 20, "rw0d": 9.6449, "of": 1.00, "desc": "Acute MI w single vessel PTCA w min CCC"},
    # Cardiac Cath/Angiography
    "05210": {"rw": 2.7603, "wtlos": 3.87, "ot": 12, "rw0d": 2.5119, "of": 1.00, "desc": "Cardiac cath/angiography for complex Dx wo sig CCC"},
    "05211": {"rw": 5.5237, "wtlos": 8.85, "ot": 27, "rw0d": 4.6399, "of": 1.00, "desc": "Cardiac cath/angiography for complex Dx w min CCC"},
    "05212": {"rw": 9.1898, "wtlos": 13.12, "ot": 39, "rw0d": 6.2491, "of": 1.00, "desc": "Cardiac cath/angiography for complex Dx w mod CCC"},
    "05220": {"rw": 2.1360, "wtlos": 2.16, "ot": 6, "rw0d": 2.1360, "of": 0.66, "desc": "Cardiac cath/angiography wo sig CCC"},
    "05221": {"rw": 3.0615, "wtlos": 3.73, "ot": 11, "rw0d": 2.7860, "of": 0.77, "desc": "Cardiac cath/angiography w min CCC"},
    "05222": {"rw": 5.3864, "wtlos": 10.58, "ot": 32, "rw0d": 4.0937, "of": 1.00, "desc": "Cardiac cath/angiography w mod CCC"},
    # PCI with stent (non-acute)
    "05230": {"rw": 6.8786, "wtlos": 2.14, "ot": 6, "rw0d": 6.8786, "of": 1.00, "desc": "Percut cardiovas proc w stent insertion wo sig CCC"},
    "05231": {"rw": 8.0392, "wtlos": 2.56, "ot": 8, "rw0d": 8.0392, "of": 1.00, "desc": "Percut cardiovas proc w stent insertion w min CCC"},
    "05232": {"rw": 9.8158, "wtlos": 5.19, "ot": 16, "rw0d": 8.9324, "of": 1.00, "desc": "Percut cardiovas proc w stent insertion w mod CCC"},
    "05240": {"rw": 6.5804, "wtlos": 2.18, "ot": 7, "rw0d": 6.5804, "of": 1.00, "desc": "Percut cardiovas proc wo sig CCC"},
    "05241": {"rw": 7.7565, "wtlos": 2.76, "ot": 8, "rw0d": 7.7565, "of": 1.00, "desc": "Percut cardiovas proc w min CCC"},
    "05242": {"rw": 9.2851, "wtlos": 5.75, "ot": 17, "rw0d": 8.4494, "of": 1.00, "desc": "Percut cardiovas proc w mod CCC"},
    # Acute MI medical (no PCI)
    "05500": {"rw": 2.4222, "wtlos": 3.56, "ot": 11, "rw0d": 2.2042, "of": 1.00, "desc": "Acute MI w major comp w thrombol inj wo sig CCC"},
    "05501": {"rw": 6.0220, "wtlos": 10.06, "ot": 30, "rw0d": 4.5767, "of": 1.00, "desc": "Acute MI w major comp w thrombol inj w min CCC"},
    "05510": {"rw": 2.1349, "wtlos": 3.59, "ot": 11, "rw0d": 1.9428, "of": 1.00, "desc": "Acute MI w thrombol inj wo sig CCC"},
    "05511": {"rw": 2.6876, "wtlos": 5.20, "ot": 16, "rw0d": 2.4457, "of": 1.00, "desc": "Acute MI w thrombol inj w min CCC"},
    "05520": {"rw": 1.5851, "wtlos": 4.86, "ot": 15, "rw0d": 1.4424, "of": 1.00, "desc": "Acute MI w major comp not transferred wo sig CCC"},
    "05521": {"rw": 2.9432, "wtlos": 7.45, "ot": 22, "rw0d": 2.4723, "of": 1.00, "desc": "Acute MI w major comp not transferred w min CCC"},
    "05522": {"rw": 4.0802, "wtlos": 9.40, "ot": 28, "rw0d": 3.1009, "of": 1.00, "desc": "Acute MI w major comp not transferred w mod CCC"},
    "05523": {"rw": 6.7633, "wtlos": 13.91, "ot": 42, "rw0d": 4.5990, "of": 1.00, "desc": "Acute MI w major comp not transferred w maj CCC"},
    "05530": {"rw": 1.0396, "wtlos": 4.00, "ot": 12, "rw0d": 0.9460, "of": 0.89, "desc": "Acute MI not transferred wo sig CCC"},
    "05531": {"rw": 1.3637, "wtlos": 4.94, "ot": 15, "rw0d": 1.2410, "of": 0.97, "desc": "Acute MI not transferred w min CCC"},
    "05532": {"rw": 2.0671, "wtlos": 6.88, "ot": 21, "rw0d": 1.7363, "of": 1.00, "desc": "Acute MI not transferred w mod CCC"},
    "05533": {"rw": 3.2701, "wtlos": 9.33, "ot": 28, "rw0d": 2.4853, "of": 1.00, "desc": "Acute MI not transferred w maj CCC"},
    # Heart failure
    "05550": {"rw": 0.6831, "wtlos": 3.36, "ot": 10, "rw0d": 0.6216, "of": 1.00, "desc": "Heart failure and shock wo sig CCC"},
    "05551": {"rw": 1.3294, "wtlos": 5.24, "ot": 16, "rw0d": 1.2098, "of": 1.00, "desc": "Heart failure and shock w min CCC"},
    "05552": {"rw": 2.9495, "wtlos": 8.57, "ot": 26, "rw0d": 2.4776, "of": 1.00, "desc": "Heart failure and shock w mod CCC"},
    "05553": {"rw": 5.5413, "wtlos": 12.72, "ot": 38, "rw0d": 3.7681, "of": 1.00, "desc": "Heart failure and shock w maj CCC"},
    "05554": {"rw": 7.3352, "wtlos": 18.81, "ot": 56, "rw0d": 3.8143, "of": 1.00, "desc": "Heart failure and shock w ext CCC"},
    # Coronary atherosclerosis / UA
    "05590": {"rw": 0.5561, "wtlos": 2.31, "ot": 7, "rw0d": 0.5561, "of": 1.00, "desc": "Coronary atherosclerosis and UA wo sig CCC"},
    "05591": {"rw": 0.8915, "wtlos": 3.55, "ot": 11, "rw0d": 0.8113, "of": 1.00, "desc": "Coronary atherosclerosis and UA w min CCC"},
    "05592": {"rw": 1.6921, "wtlos": 5.75, "ot": 17, "rw0d": 1.5398, "of": 1.00, "desc": "Coronary atherosclerosis and UA w mod CCC"},
    "05593": {"rw": 2.9651, "wtlos": 8.20, "ot": 25, "rw0d": 2.4907, "of": 1.00, "desc": "Coronary atherosclerosis and UA w maj CCC"},
    "05594": {"rw": 6.3327, "wtlos": 12.71, "ot": 38, "rw0d": 4.3062, "of": 1.00, "desc": "Coronary atherosclerosis and UA w ext CCC"},
    # Arrhythmia
    "05630": {"rw": 0.8116, "wtlos": 2.13, "ot": 6, "rw0d": 0.8116, "of": 1.00, "desc": "Major arrhythmia and cardiac arrest wo sig CCC"},
    "05631": {"rw": 1.9084, "wtlos": 3.87, "ot": 12, "rw0d": 1.7366, "of": 1.00, "desc": "Major arrhythmia and cardiac arrest w min CCC"},
    "05632": {"rw": 3.6236, "wtlos": 6.68, "ot": 20, "rw0d": 3.0438, "of": 1.00, "desc": "Major arrhythmia and cardiac arrest w mod CCC"},
    "05633": {"rw": 7.4736, "wtlos": 12.38, "ot": 37, "rw0d": 5.0820, "of": 1.00, "desc": "Major arrhythmia and cardiac arrest w maj CCC"},
    # Hypertension
    "05600": {"rw": 0.3341, "wtlos": 1.91, "ot": 6, "rw0d": 0.3341, "of": 1.00, "desc": "Hypertension wo sig CCC"},
    "05601": {"rw": 0.8421, "wtlos": 3.45, "ot": 10, "rw0d": 0.7663, "of": 1.00, "desc": "Hypertension w min CCC"},
    # Chest pain
    "05660": {"rw": 0.3602, "wtlos": 1.63, "ot": 5, "rw0d": 0.3602, "of": 1.00, "desc": "Chest pain syncope and collapse wo sig CCC"},
    "05661": {"rw": 0.6192, "wtlos": 2.48, "ot": 7, "rw0d": 0.6192, "of": 1.00, "desc": "Chest pain syncope and collapse w min CCC"},
    # Acute MI transferred
    "05690": {"rw": 0.6719, "wtlos": 1.81, "ot": 5, "rw0d": 0.6719, "of": 1.00, "desc": "Acute MI transferred wo sig CCC"},
    "05691": {"rw": 1.6614, "wtlos": 3.90, "ot": 12, "rw0d": 1.5119, "of": 1.00, "desc": "Acute MI transferred w min CCC"},
    "05692": {"rw": 3.0483, "wtlos": 6.32, "ot": 19, "rw0d": 2.5606, "of": 1.00, "desc": "Acute MI transferred w mod CCC"},
    "05693": {"rw": 5.3159, "wtlos": 10.78, "ot": 32, "rw0d": 4.0401, "of": 1.00, "desc": "Acute MI transferred w maj CCC"},
    # Surgical
    "05039": {"rw": 29.3120, "wtlos": 21.98, "ot": 66, "rw0d": 12.8973, "of": 1.00, "desc": "Coronary bypass with PTCA"},
    "05049": {"rw": 23.1477, "wtlos": 24.44, "ot": 73, "rw0d": 10.1850, "of": 1.00, "desc": "Coronary bypass with cath"},
    "05059": {"rw": 18.1845, "wtlos": 13.75, "ot": 41, "rw0d": 12.3655, "of": 0.98, "desc": "Coronary bypass"},
    "05019": {"rw": 18.3432, "wtlos": 24.17, "ot": 73, "rw0d": 8.0710, "of": 1.00, "desc": "Valve replacement and open valvuloplasty w cath"},
    # Pacemaker / ICD
    "05110": {"rw": 3.2787, "wtlos": 4.50, "ot": 14, "rw0d": 2.9836, "of": 1.00, "desc": "Perm pacemaker proc comb wo sig CCC"},
    "05111": {"rw": 4.8684, "wtlos": 6.98, "ot": 21, "rw0d": 4.0895, "of": 1.00, "desc": "Perm pacemaker proc comb w min CCC"},
    "05112": {"rw": 7.6522, "wtlos": 13.53, "ot": 41, "rw0d": 5.2035, "of": 1.00, "desc": "Perm pacemaker proc comb w mod CCC"},
    "05120": {"rw": 4.9904, "wtlos": 3.94, "ot": 12, "rw0d": 4.5413, "of": 1.00, "desc": "Automat cardioverter proc wo sig CCC"},
    "05121": {"rw": 7.3820, "wtlos": 7.09, "ot": 21, "rw0d": 6.2008, "of": 1.00, "desc": "Automat cardioverter proc w min CCC"},
    # Peripheral stent
    "05310": {"rw": 3.9910, "wtlos": 2.42, "ot": 7, "rw0d": 3.9910, "of": 1.00, "desc": "Peripheral stent insertion wo sig CCC"},
    "05311": {"rw": 7.5004, "wtlos": 10.10, "ot": 30, "rw0d": 5.7003, "of": 1.00, "desc": "Peripheral stent insertion w min CCC"},
    # Electrophysiology
    "05149": {"rw": 5.7297, "wtlos": 3.22, "ot": 10, "rw0d": 5.2140, "of": 1.00, "desc": "Cardiac electrophysiologic proc"},
}


def lookup_drg(drg_code: str) -> DRGInfo | None:
    """Lookup DRG from cardiac RW table."""
    entry = CARDIAC_DRG_TABLE.get(drg_code)
    if not entry:
        return None
    return DRGInfo(
        drg=drg_code,
        rw=entry["rw"],
        wtlos=entry["wtlos"],
        ot=entry["ot"],
        rw0d=entry["rw0d"],
        of_factor=entry["of"],
        description=entry["desc"],
        payment_estimate_in_zone=round(entry["rw"] * BASE_RATE_IN_ZONE, 2),
        payment_estimate_out_zone=round(entry["rw"] * BASE_RATE_OUT_ZONE, 2),
    )


def calculate_payment(rw: float, los: int, drg_code: str, in_zone: bool = True) -> dict:
    """Calculate expected payment based on RW, LOS, and zone."""
    base_rate = BASE_RATE_IN_ZONE if in_zone else BASE_RATE_OUT_ZONE
    drg_info = lookup_drg(drg_code)

    adj_rw = rw
    los_adjustment = "normal"

    if drg_info:
        if los <= 1 and drg_info.rw0d > 0:
            adj_rw = drg_info.rw0d
            los_adjustment = "short_stay (RW0d)"
        elif los > drg_info.ot:
            los_adjustment = f"long_stay (>{drg_info.ot} days)"

    payment = round(adj_rw * base_rate, 2)

    return {
        "drg": drg_code,
        "rw": rw,
        "adj_rw": adj_rw,
        "los": los,
        "los_adjustment": los_adjustment,
        "base_rate": base_rate,
        "in_zone": in_zone,
        "payment": payment,
    }
