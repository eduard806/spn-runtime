# spn-runtime — arhiva de release a calculatorului de taxe M1-C01 (SPN STOICA)

Depozitul este DOAR arhivă de release. Sursa de execuție pentru instanțe este skill-ul montat `spn-taxe-m1c01` (V1_13); GitHub se folosește doar ca ultimă treaptă a cascadei, cu verificarea hash-ului pinuit.

## Release curent: M1C01_RUNTIME_V4.13.zip (25.08.2026)
- SHA-256: `1c97f831e7eaa6ffda7b4994cdf27d0290cce939b975a6e060f8769a7ef350df`
- Lanț: motor V1.17 · orchestrator V3.7 · generator ofertă V3.5 · schema intrare V1.13 · schema ieșire V1.1 · reguli V1.12 · FX gate V2.1 · registru FX V2.0
- Manifest intern: `RUNTIME_SHA256_MANIFEST.txt` (13 fișiere) — publicat alături pentru verificare fără skill.
- Ce repară V4.13 față de V4.10: cantitățile declarației de radiere (`radiere_information_extracts`, `radiere_notation_count`) ajung în motor; QA-ul generatorului acceptă rândul de notare la radiere. Speța de referință: 2 extrase + 4 radieri → 1383,00 lei.
- V4.11 / V4.12: numere rezervate unor specificații neexecutate; nu există ca release.

## Verificare
```
sha256sum M1C01_RUNTIME_V4.13.zip      # = 1c97f831e7eaa6ffda7b4994cdf27d0290cce939b975a6e060f8769a7ef350df
unzip -q M1C01_RUNTIME_V4.13.zip && cd M1C01_RUNTIME_V4_13 && sha256sum -c RUNTIME_SHA256_MANIFEST.txt   # 13/13 OK
```
