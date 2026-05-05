# IPPSAnalytics Business Context & Data Dictionary

This file is a running reference of business logic, Oracle field meanings, hardcoded values, and domain facts discovered while auditing project repos. Use it to write better inline comments and to understand why code is written the way it is.

Update this file whenever you encounter a new fact during a `/full-review`, `/audit-project`, or `/sync-readme` pass.

---

## Oracle OFC — Business Units

| Fact | Source |
|---|---|
| `org_id / PRC_BU_ID = '300000002352016'` = UCSD Campus (non-foundation procurement org) | 572, 409 |
| `org_id = '300000002352096'` = UCSD Foundation | 409 |
| These are the only two org IDs presented to users in BI Publisher parameter prompts for business unit selection | 409 |

---

## Oracle OFC — Suppliers & Sites

| Fact | Source |
|---|---|
| `vendor_id = '-999'` means the payee is outside of OFC (not a real supplier record) | 572 |
| `LENGTH(pha.SEGMENT1) >= 8` filters to valid PO numbers; shorter values are abnormal and don't appear in the OFC UI | 572 |
| Valid PO number patterns in scope: `segment1 LIKE 'PUR%'` or `segment1 LIKE '9%'` | 739 |
| Excluded PO statuses across projects: `'CLOSED'`, `'FINALLY CLOSED'`, `'CANCELED'` | 739 |
| `pssa.VENDOR_SITE_CODE LIKE 'PAYMT%'` = payment sites; `LIKE 'PO%'` = purchasing sites | 572 |
| `ps.attribute2` = employee employment status; `ps.attribute_date1` = employee separation date | 572 |
| Employee status codes on `ps.attribute2`: `A`=Active, `L`=Unpaid Leave of Absence, `P`=Paid Leave of Absence, `W`=Short Work Break, `T`=Terminated, `R`=Retired, `D`=Deceased | 572 |
| Invoice sources `UCSD Sophia` and `UCSD Epic Tapestry` on `ap_invoices_all.source` indicate clinical/hospital system suppliers — excluded from inactivation and bulk changes | 572 |
| The following 18 supplier numbers are permanently excluded from inactivation per business owner: `10633`, `25507`, `56600`, `141557`, `141556`, `24470`, `22241`, `24982`, `22251`, `56598`, `25418`, `24981`, `21963`, `25666`, `24079`, `25535`, `14005`, `25503` | 572 |
| `poz_suppliers.VENDOR_TYPE_LOOKUP_CODE = 'ELECTRONIC_SUPPLIER_CXML'` = supplier receives POs via cXML; requires Buyer-Initiated change order instead of self-service | 739 |
| `poz_suppliers_pii.income_tax_id` = supplier TIN for 1099 reporting | 409 |
| `poz_suppliers.tax_reporting_name` = name used on 1099 forms; may differ from trading name | 409 |
| `poz_suppliers.organization_type_lookup_code` = tax organization type (corporation, individual, etc.) | 409 |
| `ap_checks_all.status_lookup_code = 'VOIDED'` identifies voided payments | 409 |
| `pha.attribute7 = 'Yes'` on `po_headers_all` = PO required buyer review | 758 |
| `paaf.ASSIGNMENT_NUMBER NOT LIKE '%_WT'` excludes work-type assignment rows; `!= 'ET1'` excludes a duplicate "UC San Diego" employee record | 758 |

---

## Oracle OFC — Key Tables

| Table | What it contains |
|---|---|
| `poz_suppliers` | Supplier header records (one row per supplier) |
| `poz_supplier_sites_all_m` | Supplier site records (payment and purchasing sites) |
| `poz_suppliers_pii` | Supplier PII including `income_tax_id` (TIN); join on `vendor_id` |
| `poz_business_classifications_v` | Supplier business classifications; `DISPLAYED_FIELD` = human-readable name; `LOOKUP_CODE` = backend code |
| `poz_all_supplier_contacts_v` | Supplier contact names and emails |
| `hz_parties` | Party names and IDs — join to `poz_suppliers` on `PARTY_ID` to get supplier name |
| `hz_party_sites` | Maps `hz_parties` to physical locations via `location_id`; `party_site_id` used as join key |
| `hz_locations` | Physical address fields (address1–4, city, postal_code, state, country) |
| `ap_checks_all` | Payment records — use `check_date` for most recent payment date |
| `ap_invoices_all` | Invoice records — includes `source` field for invoice origin system |
| `ap_invoice_lines_all` | Invoice line detail — includes tax code (`tax`), user-defined fiscal class, accounting date, 1099 type |
| `ap_invoice_distributions_all` | Distribution-level amounts, AWT flags (`awt_flag`), gross AWT amounts (`awt_gross_amount`) |
| `ap_invoice_payments_all` | Links `ap_invoices_all` to `ap_checks_all` via `invoice_id` / `check_id` |
| `ap_terms_tl` | Payment terms names (e.g. `'Immediate'`, `'Net 30'`) |
| `ap_terms_lines` | Payment terms due-day values |
| `AP_INV_APRVL_HIST_ALL` | Invoice approval workflow history — `RESPONSE` codes, `approver_id`, `CREATION_DATE`, `action_date` |
| `po_headers_all` | Purchase order headers — `SEGMENT1` is the PO number |
| `po_distributions_all` | PO distribution lines — includes `PJC_TASK_ID` (Oracle Projects link) and GL segment references |
| `gl_code_combinations` | GL account code combinations — see segment meanings table below |
| `GL_SEG_VAL_HIER_CF` | Financial unit hierarchy — `DEP27`–`DEP30` columns, `TREE_CODE = 'UCSD_FIN_UNIT_T'` |
| `fnd_vs_typed_values_vl` | Valid financial unit codes — filter: `value_set_code = 'UCSD_FIN_UNIT_VS'`, `LENGTH(value) = 7`, numeric, `!= '0000000'` |
| `POR_REQUISITION_HEADERS_ALL` | Requisition headers — `PREPARER_ID` = person who submitted the req |
| `POR_REQUISITION_LINES_ALL` | Requisition lines — `requester_id` = person who requested goods/services; join to headers on `REQUISITION_HEADER_ID` |
| `PJF_PROJECTS_ALL_VL` | Oracle Projects — project header view (`segment1` = project number, `project_status_code`) |
| `PJF_PROJ_ELEMENTS_VL` | Oracle Projects — task elements (`ELEMENT_NUMBER` = task number; filter `object_type = 'PJF_TASKS'`) |
| `per_email_addresses` | Employee email addresses — `email_type = 'W1'` = work email |
| `per_person_names_f` | Employee name history — use `ROW_NUMBER() OVER (PARTITION BY person_id ORDER BY EFFECTIVE_START_DATE DESC) = 1` to get most recent name |
| `hr_organization_units_f_tl` | Org unit names and IDs — used for business unit parameter prompts |

---

## Oracle OFC — GL Segment Meanings

| Segment | Meaning |
|---|---|
| `segment2` | Fund |
| `segment3` | Financial Unit Number |
| `segment4` | Expenditure Type |
| `segment5` | Function Number |
| `segment7` | Location Number |
| `segment8` | Project Number — value `'0000000'` means no project associated |

---

## Oracle OFC — Withholding Tax

| Fact | Source |
|---|---|
| `ap_invoice_lines_all.tax = 'AWT'` identifies automatic withholding tax lines | 409 |
| `ap_invoice_lines_all.user_defined_fisc_class` is NULL on tax (AWT) lines — filtering on this field directly would eliminate non-tax sibling lines | 409 |
| `Q-409-UserDefined.sql` moves the tax type filter into a subquery to avoid dropping non-tax lines that share the same invoice | 409 |
| `Q-409-VoidedChecks.sql` uses `LAG(check_number)` and `LAG(check_date)` partitioned by `invoice_id` to identify the original pre-void check | 409 |

---

## Oracle Projects

| Fact | Source |
|---|---|
| `pda.PJC_TASK_ID` on `po_distributions_all` links a PO distribution to its Oracle Projects task | 739 |
| `gcc.segment8 != '0000000'` filters to PO distributions with an associated project | 739 |
| Project/task dates in Oracle are stored in UTC; `+ 7/24` converts to Pacific time (UTC-7) | 739 |

---

## Invoice Approval Workflow

| Fact | Source |
|---|---|
| `AP_INV_APRVL_HIST_ALL.RESPONSE = 'INITIATED'` = workflow first initiated | 758 |
| `AP_INV_APRVL_HIST_ALL.RESPONSE = 'ORA_ASSIGNED TO'` = invoice assigned to an approver | 758 |
| `AP_INV_APRVL_HIST_ALL.RESPONSE = 'ORA_ACQUIRED BY'` = approver self-assigned | 758 |
| `AP_INV_APRVL_HIST_ALL.RESPONSE = 'ORA_RESUBMITTED'` = invoice was sent back and resubmitted; approval timestamps for these should be measured from resubmission date only | 758 |
| `approver_id LIKE '%UCSD_WF_APPROVER_JOB%'` = FinU approver via workflow role (not a named user) | 758 |
| `AP_INV_APRVL_HIST_ALL.APPROVAL_STEP = 'Tax'` = invoice required tax review | 758 |
| Tax queue approvers (hardcoded by full name in 758 SQL): `Bradley, Heather`, `Orila, Rowena`, `Wong, Kevin Ngo`, `Vongkeo, Abby`, `Swank, Thomas` | 758 |
| `po_action_history.action_code = 'APPROVE'` filters workflow history to approval actions | 739 |

---

## Payment Terms

| Fact | Source |
|---|---|
| `ap_terms_tl.name = 'Immediate'` is treated as 2 due-days in `Q-758-PO_Invoices_Approval_History_FY24.sql` but 1 due-day in `Q-758-PO_Invoices_Paid_FY24.sql` — inconsistency to verify with business owner | 758 |
| Due date = `invoice_date + due_days` from `ap_terms_tl` / `ap_terms_lines` | 758 |
| FBDI site imports for SB suppliers previously hardcoded `Payment Terms = 'Net 15'`; SB suppliers have since moved to Immediate terms — this value may be outdated | 458 |

---

## Financial Unit Hierarchy

| Fact | Source |
|---|---|
| `GL_SEG_VAL_HIER_CF` columns `DEP27`–`DEP30` represent FinU hierarchy levels: `DEP27` = leaf level, `DEP30` = broadest | 758 |
| `TREE_CODE = 'UCSD_FIN_UNIT_T'` is the Oracle tree for the FinU hierarchy; get the latest version with `ROW_NUMBER() OVER(PARTITION BY TREE_CODE ORDER BY CREATION_DATE DESC) = 1` | 758 |
| When `DEP30_PK1_VALUE_NAME = 'All Projects'`, remap to `'Academic Affairs'` for display | 758 |
| Financial unit codes in project 589 are 7-digit numeric; Excel may read them as floats — truncate to 7 chars via `str[:7]` | 589 |
| Financial unit codes with `-(SD)` suffix in the name indicate San Diego campus units | 589 |

---

## BI Publisher

| Fact | Source |
|---|---|
| BI Publisher Excel exports include 5 metadata rows before the column header row and 2 more rows before data starts — use `iloc[5]` to set headers and `[7:]` to slice to data | 572 |
| Optional parameter NULL-check pattern: `(:p_param IS NULL) OR (field = :p_param)` allows a report to run without filtering when no value is selected | 409 |
| Date parameters follow the same pattern: `(:p_start_date IS NULL) OR (date_field BETWEEN :p_start_date AND :p_end_date)` | 409 |
| Parameter prompt queries return display/value pairs — e.g. show `org_name`, pass `organization_id` | 409 |

---

## BI Publisher Email Bursting (Project 739)

| Fact | Source |
|---|---|
| Bursting control query columns: `KEY`, `TEMPLATE`, `locale`, `output_format`, `del_channel`, `OUTPUT_NAME`, `parameter1`=To, `parameter2`=CC, `parameter3`=From, `parameter4`=Subject, `parameter5`=Body (HTML), `parameter6`=true | 739 |
| `split_by_col` key format for 739: `'[days]-[po_number]'` — encodes the days-to-expiry bucket (0, 7, or 30) and PO number for per-PO email splitting | 739 |
| From address for project validation hold emails: `noreply-accountspayable@messaging.ucsd.edu` | 739 |
| Three email body variants: (1) cXML supplier → Buyer-Initiated change order via ServiceNow; (2) non-cXML not invoiced → self-service via KB0032957; (3) non-cXML partially invoiced → add line or reduce+replace | 739 |

---

## ServiceNow KBA References

| KBA | Purpose |
|---|---|
| KB0032957 | How to create a Change Order to Edit POET Information |
| KB0034363 | How to add a new line to an existing PO |
| KB0032063 | How to close a PO |

---

## PaymentWorks (Supplier Onboarding Portal)

| Fact | Source |
|---|---|
| PaymentWorks is UCSD's supplier onboarding and registration portal | 725 |
| Registration types: Full, Partial, Edit | 725 |
| Registration statuses: Connected, Rejected, Returned, Pending | 725 |
| `Payee_Time_Business_Hours` = time from invitation sent to registration submitted (payee set-up time) | 725 |
| `IPPS_Time_Business_Hours` = time from registration submitted to connected (IPPS processing time) | 725 |
| UCSD business hours for cycle time: 8:00am–4:30pm, Mon–Fri (days 5=Sat, 6=Sun excluded) | 725 |

---

## Transcepta (E-Invoicing Portal)

| Fact | Source |
|---|---|
| Transcepta is UCSD's e-invoicing portal through which suppliers submit invoices before they enter Oracle OFC | 758 |
| Transcepta exports contain: Invoice Number, PO Number, Vendor Number, Vendor Name, Date Sent, Status, Validation Error, Document ID | 758 |
| `Validation Error` field is a comma-delimited string; split on `', , '` (double-comma) to get one row per error | 758 |
| ~7% of Transcepta-submitted FY24 invoices had validation errors (~16,799 of ~247,594) | 758 |
| Match Transcepta to OFC on normalized `Invoice Number` + `Vendor Number` (not PO number — a prior version used PO number) | 758 |

---

## Supplier.io (Small Business Certification)

| Fact | Source |
|---|---|
| Supplier.io is UCSD's third-party SB certification data provider; holds certification flags and expiration dates not in Oracle | 458 |
| Supplier.io IDs follow the format `S_XXXXXXX` — internal to Supplier.io, not Oracle `SEGMENT1` numbers | 458 |
| Expiration date columns follow the pattern `<FLAG>_SRC_VALID` (e.g. `MBE_SRC_VALID`, `WOSB_SRC_VALID`) | 458 |
| CalUSource is UCSD's eProcurement marketplace; used to filter OFC suppliers to active trading partners | 458 |

## OFC Business Classification Codes

| Displayed Name | Backend LOOKUP_CODE |
|---|---|
| Small Business Concern (s) | SMALL_BUSINESS_CONCERN |
| Minority Business Enterprise (8) | MINORITY_BUSINESS_ENTERPRISE |
| Small Disadvantaged Business (D) | SMALL_DISADVANTAGED_BUSINESS |
| Veteran-Owned Small Business (V) | VETERAN_OWNED_SMALL_BUSINESS |
| Disabled Veteran Bus Enterprise (DV) | DISABLED_VETERAN_BUS_ENT |
| Women-Owned Small Business (Q) | WOMEN-OWNED_SMALL_BUSINESS |
| Woman Owned | WOMAN_OWNED |
| Small Business | SMALL_BUSINESS |
| Veteran Owned | VETERAN_OWNED |
| Minority Owned | MINORITY_OWNED |
| Service-Disabled Vet-Owned SB (7) | SERVICE_DISABLED_VET_OWNED_SB |
| HUBZone Small Business (H) | HUBZONE_SMALL_BUSINESS |
| Disadvantage Bus Enterprise (DE) | DISADVANTAGE_BUS_ENTERPRISE |
| Veteran Business Enterprise (VE) | VETERAN_BUSINESS_ENTERPRISE |
| Women Business Enterprise (QE) | WOMEN_BUSINESS_ENTERPRISE |
| Historical Black Coll & Univ/MI (B) | HIST_BLACK_COLL_AND_UNIV_MI |
| 8(a) Business Dev. Program | 8A_BUSINESS_DEV_PROGRAM |
| HUB Zone | HUB_ZONE |
| Service-disabled Veteran Owned | DISABLED_VETERAN_OWNED |
| Small Local Business Enterprise (SL) | SMALL_LOCAL_BUSINESS_ENT |
| Lesbian,Gay,Bi,Trans,Queer (LGBTQ) | LESBIAN_GAY_BI_TRANS_QUEER |

---

## Concur (Travel & Expense)

| Fact | Source |
|---|---|
| Concur payment type `*UCSD - Procurement Card` = PCard | 589 |
| Concur payment type `*UCSD - T&E Card` = Travel and Entertainment card | 589 |
| Concur payment type `*UCSD - CTS Air, Hotel Card` = Central Travel System card for air/hotel | 589 |
| `Report_ID` = unique Concur expense report identifier (alphanumeric, ~20 chars) | 589 |
| `Entry_Key` = unique identifier for a single expense line within a report | 589 |
| `Custom 12 - Name` = event type; `Custom 23 - Name` = meal/refreshment subcategory | 589 |
| `Attendee Type Code`: `STUDENT` = student; `SYSEMP` = faculty/staff | 589 |
| `Approval Status` values: `Approved`, `Not Submitted`, `Sent Back to User`, `Pending Central Office Review` | 589 |
| A Concur delegate is authorized to create/submit reports on behalf of another employee; `Created by a Delegate` = Yes/No field | 589 |
| Unreconciled charge aging buckets: `< 30 Days`, `31–60 Days`, `61–90 Days`, `> 90 Days` | 589 |
| Light-refreshments duplicate threshold: `Count1 > 2`; meals: `Count1 > 1` — higher threshold for meals reflects legitimate multi-line claims | 589 |

---

## PPM & TrackVia (Logistics Reconciliation)

| Fact | Source |
|---|---|
| PPM (Project Portfolio Management) = UCSD cost accounting system; records expenditures against project/task budgets | 506 |
| TrackVia = Logistics operational tracking system used by Surplus Sales and Moving Services to log jobs | 506 |
| Composite match key (`link`) = `Original Transaction Reference` + `_` + `Expenditure Type` + `_` + `Expenditure Date` | 506 |
| When PPM's `Expenditure Original Transaction Reference` starts with `ID#`, it's an internal PPM ID — use `Expenditure Comment` as the match key instead | 506 |
| TrackVia `Original Transaction Reference` values may have trailing spaces — apply `.str.rstrip()` before key construction | 506 |
| Date format mismatch: TrackVia uses `%d-%b-%y` (e.g. `15-Nov-23`); PPM uses `%Y-%m-%d` — normalize both before concatenation | 506 |

---

## FBDI (File-Based Data Import)

| Fact | Source |
|---|---|
| FBDI `Import Action` values: `'UPDATE'` for site updates; `'CREATE'` for new classification records | 458 |
| FBDI `Procurement BU` hardcoded to `'UCSD CAMPUS'` for site updates | 458 |
| `Batch ID` is set to today's date as `MMDDYYYY` integer (e.g. `4032025`) | 458 |
| FBDI excludes sites with codes `LIKE 'LEGAL ADDR%'`, `LIKE 'PAYMT PLUS%'`, `LIKE 'PAYMT PSUA%'`, `= 'T_E SUPPLIER'`, `= 'GUEST TRAVELER'` | 458 |

---

## Cross-Project Dependencies

| Dependency | Detail |
|---|---|
| `G-755-Supplier_Details.csv` | Global Oracle OFC supplier/site extract maintained by project 755; reused across multiple projects | 725 |
| `F-458-Supplier_Enrichment.xlsx` | Produced by `S-458-Supplier_Enrichment.ipynb`, consumed by `S-458-FBDI_File_Creation.ipynb` | 458 |
| `Q-758-All_Invoices_Created_FY24` and `Q-758-PO_Invoices_Paid_FY24.sql` | Structurally derived from `667-DM-Procurement_Spend` queries — headers were originally copied from that project | 758 |

---

## File Naming Conventions

| Prefix | Meaning |
|---|---|
| `Q-[ID]-*` | Oracle query (data extraction) |
| `S-[ID]-*` | Script/transformation notebook |
| `P-[ID]-*` | Stored procedure or parameter prompt query |
| `T-[ID]-*` | Temp/test file — candidate for removal |
| `R-[ID]-*` | Raw input report file (e.g. PaymentWorks or Transcepta exports) |
| `F-[ID]-*` | Final output file |
| `G-[ID]-*` | Global/shared data source file (used across projects) |
| `V-[ID]-*` | Intermediate/unclean version of an output file |

---

## Open Flags (Items for Human Review)

| Issue | Project |
|---|---|
| `Travel.ipynb` in 506 folder does not belong to Surplus/Moving Services — appears to be an ad hoc travel reconciliation script accidentally committed here; local desktop paths suggest it was never put into production | 506 |
| Surplus notebook writes output to `Data Sources/` folder while Moving Services notebook writes to `Final Product/` — inconsistent output folder convention | 506 |
| `Q-758-All_Invoices_Created_FY24` is missing its `.sql` file extension — not renamed per review scope rules | 758 |
| `Immediate` payment terms = 2 days in one 758 query, 1 day in the other — verify with business owner | 758 |
| Net 15 payment terms in 458 FBDI may be outdated — SB suppliers appear to have moved to Immediate terms | 458 |
| `S-458-Supplier_Enrichment.ipynb` too large to audit (>25k tokens) — project header cell still needs to be added manually | 458 |
| `S-758-Transcepta_Invoices_Analysis.ipynb` too large to audit — project header cell still needs to be added manually | 758 |
