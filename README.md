# spn-runtime — arhiva de release a calculatorului de taxe M1-C01 (SPN STOICA)

Depozitul este DOAR arhivă de release. Sursa de execuție pentru instanțe este skill-ul montat `spn-taxe-m1c01` (V1_14); GitHub se folosește doar ca ultimă treaptă a cascadei, cu verificarea hash-ului pinuit.

## Release curent: M1C01_RUNTIME_V4.14.zip (25.08.2026)
- SHA-256: `da65465519d4e92dd8363e6468a0045113d679e81445f8cc497ef0099fd115fc`
- Lanț: motor V1.17 · orchestrator V3.7 · generator ofertă V3.6 · schema intrare V1.13 · schema ieșire V1.1 · reguli V1.12 · FX gate V2.1 · registru FX V2.0
- Manifest intern: `RUNTIME_SHA256_MANIFEST.txt` (13 fișiere) — publicat alături pentru verificare fără skill.
- V4.14 (am.110): pe ramura radierii rândul de carte funciară se numește «Taxă de radiere din cartea funciară — N radieri x 75,00 lei» (generator V3.6).
- V4.13 (am.109) față de V4.10: cantitățile declarației de radiere (`radiere_information_extracts`, `radiere_notation_count`) ajung în motor; QA-ul generatorului acceptă rândul de notare la radiere. Speța de referință: 2 extrase + 4 radieri → 1383,00 lei.
- V4.11 / V4.12: numere rezervate unor specificații neexecutate; nu există ca release.

## Verificare
```
sha256sum M1C01_RUNTIME_V4.14.zip      # = da65465519d4e92dd8363e6468a0045113d679e81445f8cc497ef0099fd115fc
unzip -q M1C01_RUNTIME_V4.14.zip && cd M1C01_RUNTIME_V4_14 && sha256sum -c RUNTIME_SHA256_MANIFEST.txt   # 13/13 OK
```
