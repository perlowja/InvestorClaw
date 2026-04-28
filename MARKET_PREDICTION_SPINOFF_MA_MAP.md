# Spinoff & M&A Event Mapping (1970-2026)

**Purpose:** Document major corporate events affecting the 55-ticker universe. Used to validate historical data continuity and handle survivorship bias in training.

**Categories:**
1. **Spinoffs** — Parent company divides into separate entities
2. **Mergers/Acquisitions** — Companies combine or cease to exist as independent
3. **Breakups** — Regulatory or strategic dissolution (AT&T, Ma Bell)
4. **Major Divestitures** — Significant business unit separated

---

## Critical Events (Affecting Model Training)

### AT&T (T) — 1984 Divestiture (BREAKUP)

**Event:** Antitrust breakup of AT&T monopoly into AT&T (long-distance) + Baby Bells (regional)

**Date:** January 1, 1984

**Impact:** 
- Pre-1984: Ticker T = entire AT&T monopoly
- Post-1984: Ticker T = long-distance only; regional telephone companies (Bell Atlantic → VZ, Pacific Bell → SBC → AT&T today, etc.)
- **Data handling**: T pre-1984 and post-1984 are different companies; track separately or adjust for business mix change

**Baby Bells created (map to modern tickers):**
- Bell Atlantic → Verizon Communications (VZ) — our universe
- Pacific Bell → SBC → AT&T (merged back 2005)
- Southwestern Bell → SBC → AT&T
- NYNEX → Bell Atlantic → Verizon (VZ)
- US West → partially acquired
- South Western Bell → SBC
- BellSouth → AT&T (merged 2006)

**Our mapping:**
- Use T for pre-1984 AT&T (monopoly era, different economics)
- Use T for post-1984 AT&T (long-distance carrier)
- Track VZ separately (1984+, started as Bell Atlantic)
- **Note**: Pre-1984 T and post-1984 T have different business models; model should learn this regime shift

---

### Lucent Technologies (LU) — 1996 Spinoff from AT&T

**Event:** AT&T spins off equipment manufacturing division as Lucent Technologies

**Date:** September 30, 1996

**Impact:**
- AT&T (T) pre-1996 = telecom services + equipment manufacturing
- AT&T (T) post-1996 = telecom services only
- LU 1996-2006 = independent equipment company (Bell Labs, telecom equipment)
- LU post-2006 = bankruptcy, liquidation, acquired by Alcatel

**Our mapping:**
- Use T pre-1996 with caveat: includes equipment business (different economics)
- Use T post-1996: services-only (cleaner comparison)
- Track LU 1996-2006: independent company (data available)
- Flag LU post-2006 as unavailable (bankruptcy, merger into Alcatel-Lucent, later dissolved)
- **Event to label in events.csv**: "AT&T Lucent spinoff Sep 30 1996" → equipment sector divergence signal

---

### Motorola (MOT) — 2011 Spinoff

**Event:** Motorola splits into Motorola Mobility (handsets/devices) and Motorola Solutions (equipment/infrastructure)

**Date:** January 4, 2011

**Impact:**
- MOT pre-2011 = diversified telecom equipment + mobile phones
- MOT post-2011 = infrastructure/enterprise solutions (renamed to MSI later)
- Motorola Mobility 2011-2014 = handsets (acquired by Google, resold)

**Our mapping:**
- Use MOT pre-2011 (though most historical focus is infrastructure)
- Use MSI post-2011: Motorola Solutions (our universe)
- Track split as telecommunications/equipment sector divergence
- **Event to label**: "Motorola split Jan 4 2011" → infrastructure-focused MSI created

---

### Hewlett-Packard (HPQ) — 2015 Split

**Event:** HP splits into HP Inc. (consumer/commercial PCs/printers) and HP Enterprise (servers/services)

**Date:** November 1, 2015

**Impact:**
- HPQ pre-2015 = diversified tech hardware + enterprise
- HPQ post-2015 = consumer/commercial hardware (printers, PCs, peripherals)
- HPE (new) = enterprise servers, storage, services (not in our 55 because enterprise-only)

**Our mapping:**
- Use HPQ for full history (though business mix changes 2015)
- Don't include HPE separately (not in our 55 — focused on diversified large-cap)
- **Event to label**: "HP split Nov 1 2015" → understand HPQ as consumer-hardware focused post-2015

**Status**: We do NOT include HPQ in final 55 (prefer diversified industrials CAT, BA, DE, MMM, HON instead)

---

### General Electric (GE) — Serial Divestitures (2016-2024)

**Event:** GE divests major business units over ~8 year period

**Timeline:**
- 2016-2020: Sells power generation, oil&gas
- 2020: Sells BioPharma to Pfizer
- 2023: Spins off GE HealthCare (GEHC) as independent company
- 2024: Spins off GE Aerospace (GEA) as independent company
- Remaining: GE = aviation engines (core business)

**Our mapping:**
- Use GE for full history, but note: GE pre-2016 = conglomerate (appliances, power, oil, finance, healthcare, aerospace)
- GE post-2024 = aerospace engines only (much smaller, different valuation)
- **Event labeling**: Mark each divestiture in events.csv for regime understanding

**Status**: We do NOT include GE in final 55 (divestitures make it unreliable; prefer CAT for industrial cycle signal)

---

### 3M (MMM) — 2024 Divestiture

**Event:** 3M spins off healthcare division (spin-co: Solventum Technologies, ticker SOLV)

**Date:** April 2, 2024

**Impact:**
- MMM pre-2024 = industrial + healthcare + safety + consumer (conglomerate)
- MMM post-2024 = industrial + safety (diversified industrial)
- SOLV (new) = healthcare/medical devices (not in our 55)

**Our mapping:**
- Use MMM for full history (2024 divestiture is very recent; training data 1970-2023 unaffected)
- Note: MMM post-2024 has different margins, revenue, business mix
- **Event labeling**: "3M spins healthcare to SOLV Apr 2 2024" → industrial sector divergence signal

**Status**: Include MMM in final 55 (divestiture happens after most training data)

---

### Exelon (EXC) — Formation via Merger

**Event:** EXELON created via merger of Commonwealth Edison (ComEd) and Unicom

**Date:** October 10, 2000

**Impact:**
- EXC pre-2000 = does not exist
- ComEd pre-2000 = Chicago-area nuclear utility (merged into EXC)
- Exelon post-2000 = large nuclear utility (ComEd + Unicom)

**Our mapping:**
- Start EXC data from 2000+ (yfinance should have this)
- Note: EXC is young compared to older utilities (NEE, DUK, SO, AEP, WEC all 1970+)
- EXC is critical for nuclear reactor signal (largest US nuclear utility)

**Status**: Include EXC in final 55 (starting 2000, acceptable gap pre-2000)

---

## Minor Events (Track but Not Critical)

### UnitedHealth Group (UNH) — Spinoff from Uniphi (1986)

- **Event**: Spun off from parent (historical; 1986)
- **Impact**: UNH 1986+ = independent health insurance/services
- **Our mapping**: Use UNH from 1986+ (yfinance available)

### Cisco Systems (CSCO) — IPO (1990)

- **Event**: IPO, not spinoff
- **Impact**: Limited pre-1990 data; CSCO 1990+ = networking equipment leader
- **Our mapping**: Use CSCO from 1990+

### Johnson & Johnson (JNJ) — Multiple Divestitures (2023-2024)

- **Event**: Splits consumer health division (J&J Consumer) as separate company
- **Date**: August 2023 (Kenvue, ticker KVUE)
- **Impact**: JNJ post-2023 = pharma/medical devices only (higher margin)
- **Our mapping**: JNJ 1970-2026 (divestiture post-training; minimal impact)

### Thermo Fisher (TMO) — Acquisitions (ongoing)

- **Event**: Series of acquisitions (2010-2020) that expanded scope significantly
- **Impact**: TMO pre-2010 and post-2010 = different companies
- **Our mapping**: Use TMO for full 1970-2026 (acquisitions pre-training); note business model change

---

## Summary: Data Handling Strategy

### For Training (1970-2026)

1. **Track spinoffs as regime markers**
   - AT&T breakup (1984) → fundamental shift in T, creation of VZ
   - Lucent spinoff (1996) → T loses equipment business
   - Motorola split (2011) → telecom equipment concentrated in MSI

2. **Handle breakup companies carefully**
   - Pre/post-split treated as different entities (different business models)
   - Model learns 1984 as regime shift for T (monopoly → competitive)

3. **Account for divestitures**
   - GE, 3M, JNJ lose business units → post-divestiture margin different
   - Either: (a) use adjusted historical data (complex), or (b) note regime shift and let model learn it

4. **Skip companies with critical unreliability**
   - LU (bankruptcy 2006) → use data 1996-2006, exclude post-2006
   - HPQ (multiple splits, business model unclear) → exclude from 55
   - GE (too many divestitures, unrecognizable post-2024) → exclude from 55

### For Feature Alignment

- **events.csv**: Label spinoffs/mergers with severity (medium-high for major regime shifts)
- **Example**: 
  ```
  1984-01-01,spinoff,telecom,"AT&T breakup: divestiture of Baby Bells",T;VZ,high
  1996-09-30,spinoff,telecom,"Lucent spinoff from AT&T",T;LU,high
  2011-01-04,spinoff,telecom,"Motorola splits into MSI + Mobility",MOT;MSI,medium
  2024-04-02,spinoff,industrial,"3M spins healthcare to SOLV",MMM;SOLV,medium
  ```

---

## Final 55 Ticker M&A/Spinoff Status

| Ticker | Critical Events | Status |
|--------|---|---|
| T | AT&T breakup 1984, Lucent spinoff 1996 | ✅ Include; note regime shifts |
| VZ | Creation via Bell Atlantic spinoff 1984 | ✅ Include; start 1984 |
| LU | Spinoff 1996, bankruptcy 2006 | ⚠️ Use 1996-2006 data only |
| MSI | Motorola split 2011 | ✅ Include; start 2011 |
| JNJ | Kenvue spinoff 2023 | ✅ Include; post-divestiture regime |
| MMM | SOLV healthcare spinoff 2024 | ✅ Include; recent, minimal impact |
| EXC | Merger 2000 | ✅ Include; start 2000 |
| TMO | Multiple acquisitions pre-2010 | ✅ Include; business model change noted |
| All others (43) | None material | ✅ Include; straightforward histories |

---

## References

- SEC EDGAR filings (8-K forms, proxy statements)
- Wall Street Journal archives
- Kenneth French dataset (historical event timelines)
- CRSP database (delisting codes, event dates)

