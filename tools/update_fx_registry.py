#!/usr/bin/env python3
"""SPN STOICA AI — releul FX GitHub (V1.2, 28.08.2026).

V1.2: parserul XML devine tolerant la namespace (XML-ul real de pe curs.bnr.ro
folosește alt xmlns decât cel documentat) — se potrivesc elementele după numele
local Cube/Rate, indiferent de namespace. V1.1: antet de browser la descărcare.
Restul neschimbat: format și sigiliu canonic V2.0; fail-closed, fără commit la anomalie."""
import hashlib
import json
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

URLS = ["https://curs.bnr.ro/nbrfxrates10days.xml",
        "https://www.bnr.ro/nbrfxrates10days.xml",
        "https://curs.bnr.ro/nbrfxrates.xml",
        "https://www.bnr.ro/nbrfxrates.xml"]
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/126.0 Safari/537.36"),
           "Accept": "application/xml,text/xml,*/*"}
REG = Path("BNR_FX_REGISTRY_LIVE.json")


def canonical_sha256(payload: dict) -> str:
    body = {k: v for k, v in payload.items() if k != "integrity"}
    blob = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fetch_xml() -> bytes:
    diags = []
    for u in URLS:
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                print(f"OK {u} — HTTP {r.status}, {len(data)} bytes")
                return data
        except urllib.error.HTTPError as ex:
            diags.append(f"{u} → HTTP {ex.code} {ex.reason}")
        except Exception as ex:
            diags.append(f"{u} → {type(ex).__name__}: {ex}")
    print("DIAGNOSTIC — toate gazdele au eșuat:")
    for d in diags:
        print("  ", d)
    raise SystemExit("BNR inaccesibil de pe runner — vezi diagnosticul de mai sus.")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def parse_eur(xml_bytes: bytes) -> dict:
    root = ET.fromstring(xml_bytes)
    out = {}
    for el in root.iter():
        if _local(el.tag) != "Cube":
            continue
        d = el.get("date")
        if not d:
            continue
        for rate in el:
            if _local(rate.tag) != "Rate":
                continue
            if rate.get("currency") == "EUR" and rate.text and rate.text.strip():
                value = float(rate.text.strip())
                mult = rate.get("multiplier")
                if mult:
                    value = value / float(mult)
                out[d] = value
    if not out:
        seen = sorted({_local(e.tag) for e in root.iter()})
        print("DIAGNOSTIC parse — elemente găsite în XML:", ", ".join(seen[:20]))
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
