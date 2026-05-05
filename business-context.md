# IPPSAnalytics Business Context & Data Dictionary

This file is a running reference of business logic, Oracle field meanings, hardcoded values, and domain facts discovered while auditing project repos. Use it to write better inline comments and to understand why code is written the way it is.

Update this file whenever you encounter a new fact during a `/full-review`, `/audit-project`, or `/sync-readme` pass.

---

## Oracle OFC — Suppliers & Sites

| Fact | Source |
|---|---|
| `pssa.PRC_BU_ID = '300000002352016'` identifies UCSD non-foundation procurement sites | 572 |
| `vendor_id = '-999'` means the payee is outside of OFC (not a real supplier record) | 572 |
| `LENGTH(pha.SEGMENT1) >= 8` filters to valid PO numbers; shorter values are abnormal and don't appear in the OFC UI | 572 |
| `pssa.VENDOR_SITE_CODE LIKE 'PAYMT%'` = payment sites; `LIKE 'PO%'` = purchasing sites | 572 |
| `ps.attribute2` = employee employment status; `ps.attribute_date1` = employee separation date | 572 |
| Employee status codes on `ps.attribute2`: `A`=Active, `L`=Unpaid Leave of Absence, `P`=Paid Leave of Absence, `W`=Short Work Break, `T`=Terminated, `R`=Retired, `D`=Deceased | 572 |
| Invoice sources `UCSD Sophia` and `UCSD Epic Tapestry` on `ap_invoices_all.source` indicate clinical/hospital system suppliers — these are typically excluded from inactivation and other bulk changes | 572 |
| The following 18 supplier numbers are permanently excluded from inactivation per business owner decision: `10633`, `25507`, `56600`, `141557`, `141556`, `24470`, `22241`, `24982`, `22251`, `56598`, `25418`, `24981`, `21963`, `25666`, `24079`, `25535`, `14005`, `25503` | 572 |

---

## Oracle OFC — Key Tables

| Table | What it contains |
|---|---|
| `poz_suppliers` | Supplier header records (one row per supplier) |
| `poz_supplier_sites_all_m` | Supplier site records (payment and purchasing sites) |
| `hz_parties` | Party names and IDs — join to `poz_suppliers` on `PARTY_ID` to get supplier name |
| `ap_checks_all` | Payment records — use `check_date` for most recent payment date |
| `ap_invoices_all` | Invoice records — includes `source` field for invoice origin system |
| `po_headers_all` | Purchase order headers — `SEGMENT1` is the PO number |
| `POR_REQUISITION_HEADERS_ALL` | Requisition headers |
| `POR_REQUISITION_LINES_ALL` | Requisition lines — join to headers on `REQUISITION_HEADER_ID` |

---

## PaymentWorks (Supplier Onboarding Portal)

| Fact | Source |
|---|---|
| PaymentWorks is UCSD's supplier onboarding and registration portal | 725 |
| Registration types: Full, Partial, Edit | 725 |
| Registration statuses include: Connected, Rejected, Returned, Pending | 725 |
| `G-755-Supplier_Details.csv` is a global Oracle OFC supplier/site extract maintained by project 755 and reused across multiple projects | 725 |
| UCSD business hours for cycle time calculations: 8:00am–4:30pm, Mon–Fri (days 5=Sat and 6=Sun excluded) | 725 |
| `Payee_Time_Business_Hours` = time from invitation sent to registration submitted (payee set-up time) | 725 |
| `IPPS_Time_Business_Hours` = time from registration submitted to connected (IPPS internal processing time) | 725 |

---

## File Naming Conventions

| Prefix | Meaning |
|---|---|
| `Q-[ID]-*` | Oracle query (data extraction) |
| `S-[ID]-*` | Script/transformation notebook |
| `P-[ID]-*` | Stored procedure |
| `T-[ID]-*` | Temp/test file — candidate for removal |
| `R-[ID]-*` | Raw input report file (e.g. PaymentWorks exports) |
| `F-[ID]-*` | Final output file |
| `G-[ID]-*` | Global/shared data source file (used across projects) |
| `V-[ID]-*` | Intermediate/unclean version of an output file |

---

## BI Publisher

| Fact | Source |
|---|---|
| BI Publisher Excel exports include 5 metadata rows before the column header row and 2 more rows before data starts — use `iloc[5]` to set headers and `[7:]` to slice to data | 572 |
