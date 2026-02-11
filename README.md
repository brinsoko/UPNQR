# Clanarina - postopek od CSV do tiska

Ta dokument opisuje celoten prakticen tok dela.

## 1. Izvoz iz Vulkana

1. V Vulkanu odpri `Clani -> Poljubne poizvedbe`.
2. Izberi polja:
   - `Ime`
   - `Priimek`
   - `Datum rojstva`
   - `Naslov`
   - `Kraj`
   - `Postna stevilka`
   - `Posta naziv`
3. Po potrebi ze tukaj omeji nabor (starost, izlocitev castnih clanov ipd.).
4. Izvozi.

## 2. Uredi CSV v Excelu

1. Odpri izvoženo datoteko v Excelu.
2. Odstrani člane, ki ne placujejo clanarine.
3. Po potrebi popravi posamezne podatke (naslov, kraj, posta).
4. Shrani v CSV.

Pomembno:
- ohrani enako glavo in vrstni red stolpcev,
- uporabljaj iste nazive stolpcev kot v izvozu.

## 3. Nastavi `.env`

V `.env` vpisi:
- podatke drustva (IBAN, naziv, naslov, kraj, model/sklic, namen, znesek),
- poti do vhodne in izhodne datoteke.

Primer kljucnih nastavitev:
- `CSV_FILE=2026.csv`
- `OUTPUT_TXT=2026.txt`
- `DOBRO_*` polja za podatke drustva

## 4. Zazeni pretvorbo CSV -> TXT (UPN XML vsebina)

Zazeni skripto:

```powershell
python csv_to_xml.py
```

Rezultat je `2026.txt` (XML struktura za UPN, koncnica `.txt`).

## 5. Uvoz v UPN QR program

1. Odpri program: `https://www.zbs-giz.si/placilni-promet/`
2. Uvozi `2026.txt`.
3. Rocno preveri nekaj primerov (ime, naslov, sklic, znesek).

Opomba:
- ce je nekaj nakljucnih primerov pravilnih, je obicajno pravilen tudi celoten uvoz.

## 6. Izpis PDF iz UPN QR programa

Iz UPN QR programa izvozi PDF (npr. `2026_izpis.pdf`).

## 7. Tisk - dve moznosti

### Moznost 1: tisk na pripravljeno ozadje

- Natisni `2026_izpis.pdf` neposredno na predtiskan UPN obrazec.
- Pri tiskanju uporabi `Actual size / 100%` (brez `Fit to page`).

### Moznost 2: navaden A4 papir + ozadje v PDF

- Uporabi `align_pdf.py` in zdruzi izpis z `ozadje_UPN.pdf`.
- Primer:

```powershell
python align_pdf.py --input .\2026_izpis.pdf --overlay .\ozadje_UPN.pdf --output .\2026_skupaj.pdf --x-mm 3 --y-mm 0 --scale 1.000 --mode background
```

- Po potrebi fino nastavi:
  - `--x-mm` (levo/desno),
  - `--y-mm` (gor/dol),
  - `--scale` (npr. `0.999` ali `1.001`).

## 8. Kontrola pred koncnim tiskom

1. Testno natisni 1-3 strani.
2. Preveri poravnavo QR kode in polj.
3. Ko je poravnano, izpisi celoten paket.
