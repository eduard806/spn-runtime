#!/usr/bin/env python3
"""SPN STOICA AI — releul FX GitHub (V1.0, 28.08.2026).

Rulează în GitHub Actions (acces liber la BNR). Descarcă nbrfxrates10days.xml,
extrage cursul EUR pe fiecare zi de PUBLICARE și îl îmbină în
BNR_FX_REGISTRY_LIVE.json — același format și sigiliu canonic ca registrul
V2.0 din runtime (records{data_publicării → rate}, integrity.sha256 pe JSON
canonic fără câmpul integrity). Gate-ul V2.1 îl validează neschimbat.
Fail-closed: orice anomalie → exit 1, fără commit."""
import hashlib
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

URLS = ["https://curs.bnr.ro/nbrfxrates10days.xml",
        "https://www.bnr.ro/nbrfxrates10days.xml"]
REG = Path("BNR_FX_REGISTRY_LIVE.json")
XSD = "http://www.bnr.ro/xsd"


def canonical_sha256(payload: dict) -> str:
    body = {k: v for k, v in payload.items() if k != "integrity"}
    blob = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fetch_xml() -> bytes:
    last = None
    for u in URLS:
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return r.read()
        except Exception as ex:
            last = ex
    raise SystemExit(f"BNR inaccesibil pe ambele gazde: {last}")


def parse_eur(xml_bytes: bytes) -> dict:
    root = ET.fromstring(xml_bytes)
    out = {}
    for cube in root.iter(f"{{{XSD}}}Cube"):
        d = cube.get("date")
        for rate in cube.iter(f"{{{XSD}}}Rate"):
            if rate.get("currency") == "EUR" and rate.text:
                out[d] = float(rate.text)
    if not out:
        raise SystemExit("XML-ul BNR nu conține cursuri EUR — structură neașteptată.")
    return out


def load_or_init() -> dict:
    if REG.is_file():
        reg = json.loads(REG.read_text(encoding="utf-8"))
        if canonical_sha256(reg) != str((reg.get("integrity") or {}).get("sha256", "")):
            raise SystemExit("Registrul existent are sigiliul rupt — intervenție manuală necesară.")
        return reg
    return {
        "registry_id": "BNR_FX_M1C01_LIVE_V1",
        "status": "CANONICAL_GITHUB_RELAY",
        "scope": "M1-C01 — curs de referință BNR EUR, releu GitHub actualizat automat (Action zilnic)",
        "usable_in_production": True,
        "currency": "EUR",
        "publisher": "Banca Națională a României",
        "source_domain": "bnr.ro",
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "maintenance": {
            "owner": "titular SPN STOICA",
            "rule": ("Actualizat exclusiv de GitHub Action (bnr-fx-update). Sigiliul se "
                     "recalculează la fiecare scriere; sigiliu rupt = registru refuzat de gate."),
            "recompute_command": "python3 tools/update_fx_registry.py",
        },
        "coverage": {"first_publication_date": None, "last_publication_date": None,
                     "complete_archive": False},
        "records": {},
        "governance": {"core_modified": False, "automatic_send": False,
                       "automatic_propagation": False, "human_approval_required": True,
                       "fail_closed_outside_coverage": False,
                       "outside_coverage_behaviour": "NECESITA_CLARIFICARE / FX_RATE_REQUIRED"},
        "integrity": {"algorithm": "sha256-canonical-json", "sha256": ""},
    }


def main() -> int:
    reg = load_or_init()
    eur = parse_eur(fetch_xml())
    added = 0
    for d, rate in sorted(eur.items()):
        rec = {"rate": rate,
               "official_source_url": "https://curs.bnr.ro/nbrfxrates10days.xml",
               "official_source_label": (f"BNR — curs de referință publicat "
                                          f"{d[8:10]}.{d[5:7]}.{d[0:4]} (releu GitHub)")}
        existing = reg["records"].get(d)
        if existing is not None and abs(existing["rate"] - rate) > 1e-9:
            raise SystemExit(f"CONFLICT: {d} există cu alt curs "
                             f"({existing['rate']} vs {rate}) — nu suprascriu.")
        if existing != rec:
            reg["records"][d] = rec
            added += 1
    if not added:
        print("Nimic nou — registrul e la zi.")
        return 0
    days = sorted(reg["records"])
    reg["coverage"]["first_publication_date"] = days[0]
    reg["coverage"]["last_publication_date"] = days[-1]
    reg["integrity"]["sha256"] = canonical_sha256(reg)
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Adăugate {added} zile; acoperire {days[0]} → {days[-1]}; "
          f"sigiliu {reg['integrity']['sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
