#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(ascii_only.lower().split())


def get_field(row: dict[str, str], *aliases: str) -> str:
    normalized_row = {normalize_key(k): v for k, v in row.items()}
    for alias in aliases:
        result = normalized_row.get(normalize_key(alias), "")
        if result:
            return result
    return ""


def bool_text(name: str, default: bool) -> str:
    value = env(name, "true" if default else "false").lower()
    return "true" if value in {"1", "true", "yes", "da"} else "false"


def parse_csv(csv_path: Path) -> list[dict[str, str]]:
    encodings = ("utf-8-sig", "cp1250", "latin-1")
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            with csv_path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle, delimiter=";")
                rows = [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in reader]
                return rows
        except UnicodeDecodeError as exc:
            last_error = exc
    raise RuntimeError(f"Napaka pri branju CSV ({csv_path}): {last_error}")


def add_text(parent: ET.Element, tag: str, value: str) -> None:
    elem = ET.SubElement(parent, tag)
    elem.text = value


def sklic_value(prefix: str, idx: int) -> str:
    if "{id}" in prefix:
        return prefix.format(id=idx)
    return f"{prefix}{idx}"


def build_xml(rows: list[dict[str, str]]) -> ET.Element:
    root = ET.Element(
        "ArrayOfUPN",
        {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        },
    )

    tip_dokumenta = env("TIP_DOKUMENTA", "Nalog_za_placilo")
    dobro_iban = env("DOBRO_IBAN")
    dobro_model = env("DOBRO_MODEL", "SI00")
    dobro_sklic_prefix = env("DOBRO_SKLIC_PREFIX", "2026-")
    dobro_ime = env("DOBRO_IME")
    dobro_ulica = env("DOBRO_ULICA")
    dobro_kraj = env("DOBRO_KRAJ")
    znesek = env("ZNESEK", "20.00")
    namen = env("NAMEN_PLACILA", "Clanarina 2026")
    koda_namena = env("KODA_NAMENA", "ADMG")
    rok_placila_dni = env("ROK_PLACILA_DNI", "0")
    nujno = bool_text("NUJNO", False)
    brez_zneska = bool_text("BREZ_ZNESKA", False)
    brez_placnika = bool_text("BREZ_PLACNIKA", False)
    natisni_qr = bool_text("NATISNI_QR", True)

    fixed_breme_iban = env("BREME_IBAN")
    fixed_breme_model = env("BREME_MODEL")
    fixed_breme_sklic = env("BREME_SKLIC")
    fixed_breme_ime = env("BREME_IME")
    fixed_breme_ulica = env("BREME_ULICA")
    fixed_breme_kraj = env("BREME_KRAJ")

    for i, row in enumerate(rows, start=1):
        upn = ET.SubElement(root, "UPN")

        ime = get_field(row, "Ime")
        priimek = get_field(row, "Priimek")
        naslov = get_field(row, "Naslov")
        postna = get_field(row, "Postna stevilka", "Postna")
        posta_naziv = get_field(row, "Posta naziv", "Kraj")
        breme_ime = fixed_breme_ime or f"{ime} {priimek}".strip()
        breme_ulica = fixed_breme_ulica or naslov
        breme_kraj = fixed_breme_kraj or f"{postna} {posta_naziv}".strip()

        add_text(upn, "ID", str(i))
        add_text(upn, "TipDokumenta", tip_dokumenta)
        add_text(upn, "BremeIBAN", fixed_breme_iban)
        add_text(upn, "BremeModel", fixed_breme_model)
        add_text(upn, "BremeSklic", fixed_breme_sklic)
        add_text(upn, "BremeIme", breme_ime)
        add_text(upn, "BremeUlica", breme_ulica)
        add_text(upn, "BremeKraj", breme_kraj)
        add_text(upn, "DobroIBAN", dobro_iban)
        add_text(upn, "DobroModel", dobro_model)
        add_text(upn, "DobroSklic", sklic_value(dobro_sklic_prefix, i))
        add_text(upn, "DobroIme", dobro_ime)
        add_text(upn, "DobroUlica", dobro_ulica)
        add_text(upn, "DobroKraj", dobro_kraj)
        add_text(upn, "Znesek", znesek)
        add_text(upn, "DatumPlacila", "")
        add_text(upn, "NamenPlacila", namen)
        add_text(upn, "KodaNamena", koda_namena)
        add_text(upn, "RokPlacila", "")
        add_text(upn, "RokPlacilaDni", rok_placila_dni)
        add_text(upn, "Nujno", nujno)
        add_text(upn, "BrezZneska", brez_zneska)
        add_text(upn, "BrezPlacnika", brez_placnika)
        add_text(upn, "NatisniQR", natisni_qr)

    return root


def main() -> None:
    base = Path(__file__).resolve().parent
    load_env_file(base / ".env")

    csv_file = Path(env("CSV_FILE", "2026.csv"))
    if not csv_file.is_absolute():
        csv_file = base / csv_file

    output_name = env("OUTPUT_TXT", "") or env("OUTPUT_XML", "2026.txt")
    output_file = Path(output_name)
    if not output_file.is_absolute():
        output_file = base / output_file

    rows = parse_csv(csv_file)
    root = build_xml(rows)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-16", xml_declaration=True)
    print(f"Ustvarjeno: {output_file} (UPN zapisov: {len(rows)})")


if __name__ == "__main__":
    main()
