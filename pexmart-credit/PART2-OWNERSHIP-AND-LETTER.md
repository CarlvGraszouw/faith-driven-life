# Pexmart Credit, Part 2: ownership-change service, registry data, approval letter

**Status: plan, not built.** Written 28 Oct 2026. Read with `PLAN.md`. Where this file changes a Part 1 decision,
`PLAN.md`'s revision note says so.

**Request (Carl, 28 Oct 2026), verbatim:**

> "Surely we should be able to get some form of a free API, I think, related to integrate into this process as
> well. Even if it's paid, we would really like to incorporate that as a service as well."

> "You're planning for the customer facing portal, the downloads of documents, the uploads of documents, the
> notification of those uploads and approvals, and customer communication related to an approval letter, an
> automated generated auto approval letter with the signature of the value of the credit limit signed by Hein.
> That's also something that you need to allow for."

> "Suzanne is already in the workflow. She approves credit reviews before deliveries take place in the logistics
> section. Do proper homework."

---

## 1. Answer first: is there a free API?

**No free official API for director or member changes, as far as I could find.** Paid options exist, and
none has a published per-call price I could confirm.

| Option | What it is | Director or member changes? | Price, as found | Status |
|---|---|---|---|---|
| CIPC's own developer portal (**APIVerse**) | Official, OAuth, read-only | Unconfirmed | Not published. Application and approval | A reseller's claim, not verified. CIPC's site was unreachable from this session |
| CIPC's own eServices lookup | Per-record search on the CIPC site | Yes, one company at a time | Unclear. A reseller says the free search ended in 2021 | Unverified |
| **SearchWorks** (Standard Bank) | Paid CIPC API | Claims a change history for directors and members | Pay-per-use, per the MD. No rate published | Standard Bank page not fetched |
| **Datanamix** | Paid CIPC search with API | Claims director changes and change history | Not published | Vendor claims |
| **CompanyData** | REST API, paid | Director data | Not published | Vendor claims |
| **WinDeed** | Paid alerts service | Yes, alerts on directorships at CIPC | "From R5.01 excl. VAT", unit not stated | The only vendor I found selling alerts as a product. Not fetched |
| **Lexis SACompany** | Paid database | Change history mentioned | Not published | No API or alert confirmed |
| **Lightstone** | Paid CIPC and VAT base data | No alert product confirmed | Not published | Not a fit as far as found |
| **GovChain** | Done-for-you filing service, not a data feed | Filing only | R590 and about 15 working days, per its page as summarised by search | No API found. Not fetched |
| **OpenCorporates** | Paid global register | Not confirmed for South Africa | Official page: Essentials £2,250 a year for 500 calls a month. Free only for public-benefit, non-commercial users | Not a fit for SA change alerts |
| **data.gov.za** | Government open data | No CIPC director dataset found | Free, but no director data | Dead end |

**Recommendation:**

1. Do not promise a free feed. The honest position is "free for changes we file or you tell us about, paid for
   changes filed by anyone else".
2. Build the notification service on the sources we own first. That costs nothing per call and it is the
   service people actually buy (Part 2 §3, sources A and B).
3. Run a short written evaluation of two or three paid feeds (§9), and check CIPC APIVerse directly. Buy only
   after a written answer on resale rights. That answer decides whether the "on-sell" model is legal at all.

**The restriction that matters most:** CIPC's beneficial ownership register is open to law enforcement,
competent authorities and banks, not to the public. A parliamentary reply and a commercial guide both say so
(sources in §13). No feed can therefore report beneficial-owner changes. Shareholding is covered in §2.

---

## 2. What "ownership change" can and cannot see

Our promise has to match what is visible. "Every change in the ownership structure" is not achievable from any
public source.

| Change | Where it is recorded | Can a feed see it? | Our source |
|---|---|---|---|
| Director appointed or resigned (company) | CIPC, on a CoR39 notice | Yes, via a paid feed or CIPC | Pexmart files it, the client declares it, or a feed reports it |
| CC member change | CIPC, under the Close Corporations Act (ss 34–37 per a secondary source). The form is not verified | Probably, via a feed | Same as above |
| Shareholding change, Pty Ltd | The company's own securities register. Not filed at CIPC (general Companies Act structure, not re-verified this session) | **No** | Client declaration in the portal only |
| Beneficial owner (5% thresholds) | CIPC BO register, restricted to authorities and banks | **No** | Client declaration only |
| Company name, status, business rescue | CIPC | Yes, via a feed | Feed, or Pexmart's own filing |

**The service statement, as it should appear to clients:** "We tell you about every change we file for you, every
change you tell us about, and, if you take the monitoring option, every director or member change CIPC shows
for your company. Shareholding and beneficial-owner changes are visible to us only when you declare them."

Selling this as "every change to your ownership" would be a misrepresentation. That is the most likely on-sell
risk, and it needs to be stopped in the sales wording before the first quote goes out.

---

## 3. Three sources of truth, one event stream

- **A. Pexmart-filed.** A request from the portal is worked through Susan and Hein, filed, and confirmed. The
  confirmation creates the event. Free per event, apart from the filing cost.
- **B. Client-declared.** The client tells us about any change through the portal form, including shareholding
  and beneficial-owner changes. Free.
- **C. Feed-reported.** A paid feed reports changes filed by anyone else. Optional, and only after a contract.

**De-duplication.** An event key is built from the company registration number, the change type, the person's
identity hash (not the ID number), and the effective date. A change we filed (source A) must not come back
through source C as news. The vendor match step suppresses it.

**Client notifications.** The notification goes to the client company's named contact, by email. Each event is
logged. Notifications are sent once per status, not once per poll (rule 17).

---

## 4. The clock

Two readings of the deadline conflict, from what I could find:

- **CIPC Notice 25 of 2026** (May 2026, per a law-firm blog summary): notify within 10 business days from the date
  the change occurred. Filing route: the "Director Amendments" platform.
- **Regulation 39** of the Companies Regulations (2011), per acts.co.za: 10 business days from when the company
  becomes aware of the change.

**Design choice (conservative):** the deadline runs from the effective date, and the system also stores
`aware_at`. A legal opinion from Pexmart's attorney confirms which reading applies (D-P2-11).

**Filing clock defaults:** a reminder to Susan and Hein at business day 3 and day 7, and escalation to Hein at day
8. These are my defaults, and Carl sets them (D-P2-12).

**Processing lag:** CIPC's own page (per search, possibly dated) says automated changes take effect after the
directors' OTPs, and manual ones take about three days. Treat "filed" and "registered" as different events.

---

## 5. Roles, verified against the organogram

**Source:** `scripts/data/org-chart-2026-09-04.json`, the organogram export of 4 Sep 2026 (163 people). Titles and
reporting lines below come from that file. Older docs in the repo sometimes disagree, and the table notes where.

**Spelling and title checks.** **Names, confirmed by Carl on 28 Oct 2026:** "Suzanne is Susan", "Anchelene" (for Angeline), and "Maroesjke" (for
Marushka). Titles still come from the org chart. Permissions go on these exact accounts. The repo has a history of a fuzzy match confusing two
people: `SAVE.md` line 804 records that "a fuzzy match confused exactly" Marina and Maroesjke. Match by exact account
only.

| Name in request | Name in repo | Title (org chart) | Reports to | Role in this build |
|---|---|---|---|---|
| Hein | Hein Momberg | General Manager | Andre Janse van Rensburg | **Final approver** for credit and ownership requests. Signs letters. Escalation point |
| Suzanne (Carl: "Suzanne is Susan") | Susan Kruger | Accounts Receivable | Pieter Marais | **Intake** for both request types. Sends to Hein. Releases deliveries today (`delivery_release`). Code calls her the "creditors clerk" in a comment; the org chart says AR, and AR fits credit control on customers |
| Pieter | Pieter Marais | Accountant and Financial Manager | Hein Momberg | **Backup intake** (like `delivery_release_backup`). Susan's manager. Sees all credit decisions |
| Angeline (confirmed: Anchelene) | Anchelene Pieterse | Accounts Payable | Pieter Marais | **Pays** filing fees and vendor invoices. Sees fee tasks only. No applicant documents |
| Andre | Andre Janse van Rensburg | Board Member | (none) | **Visibility only** by default: decided limits and ownership summaries. No documents. No approval unless D-P2-8 says otherwise |
| Marushka (confirmed: Maroesjke) | Maroesjke van der Walt | **Operations Manager** (org chart, 4 Sep). Older docs say Production Manager | Hein Momberg | **Escalation** when a delivery is held for credit or ownership beyond N days. Read-only holds. No documents |
| (not named) | Marina van der Walt | Sales Manager | Hein Momberg | Sees credit **status** and limit for her accounts, so she knows before she quotes. No documents |
| (not named) | Werner Posthumus-Meyjes | Logistics Manager | Maroesjke van der Walt | Sees "held for credit" on the planner, the label that already exists for Susan's release. No data |
| (not named) | Pinky Baloyi | HR and Payroll Officer | Pieter Marais | **No access.** No business reason |

**Visibility matrix (proposed).** Full = read and act within the role. Summary = read the outcome, not the file.
Status = the words only. None = not shown.

| Data | Susan | Pieter | Hein | Anchelene | Andre | Maroesjke | Marina | Werner |
|---|---|---|---|---|---|---|---|---|
| Applicant documents (ID copies, bank letters, trade references) | Full | Full (backup only) | Full | None | None | None | None | None |
| Credit decision and approved limit | Full | Full | Full | None | Summary | Status | Status | None |
| Approval letter (PDF) | Full | Full | Full | None | None | None | None | None |
| Ownership-change events, client company | Full | Full | Full | None | Summary | None | Status | None |
| Filing fees and vendor invoices | Status | Full | Full (approves) | Full | None | None | None | None |
| Delivery held for credit or ownership | Full (releases) | Full | Full | None | None | Status and escalation | Status | Status |

**Permissions to create** (ENGINEERING_RULES §6: a new capability gets a new permission, and no existing key is
overloaded):

- `credit_intake`, `credit_intake_backup`, `credit_approval`, `credit_status_view`, `credit_board_view`
- `ownership_intake`, `ownership_intake_backup`, `ownership_approval`, `ownership_fees`

`gm_financial_approval` (Hein, purchase requisitions) is not reused. Admin gets none of them implicitly (PLAN
D3).

---

## 6. The approval letter: automatic, after Hein approves

**"Automatic" does not mean "auto-approval".** The letter is generated automatically *after* Hein approves. Nothing
approves itself. Auto-approval stays refused (PLAN §13).

### What it contains

- Pexmart letterhead (brand text, D1 in PLAN).
- Letter number, for example `CAL-CA-0001-R1` (R1 = first revision).
- Date of issue.
- The applicant: company name and registration number.
- **The approved credit limit**, in figures and in words (ZAR). No reusable number-to-words helper exists in
  `api/`. Write one, tested.
- Payment terms, review date (default 12 months, D-P2-7), and the conditions text Hein entered.
- Approver line: "Hein Momberg, General Manager", with **his saved signature image**. It is read from the database
  at approval time, as `decidePurchaseRequisition` does, and never taken from the request body. If he has no
  image, approval is refused with the same message the PR flow uses.
- "Approved electronically by Hein Momberg on <timestamp>. Approval reference <CA-0001-A1>."
- A verification code and a verification address.

### How it is produced

- **PDF library:** jsPDF, already used server-side in `api/_lib` (`projectReportPdf.ts`, `trainingPdf.ts`,
  `productionSheetPdf.ts`). Reuse it.
- **Storage:** the private store, under `credit/<CA-number>/letters/<letter-id>.pdf`. Never the public store. The
  SHA-256 of the file is stored with the row.
- **Table:** `CreditApplicationLetter`: `id`, `application_id`, `revision`, `status` (`issued`, `superseded`,
  `revoked`), `issued_at`, `issued_by`, `approved_limit` (snapshot), `sha256`, `pathname`,
  `verification_code_hash`. The unique key is `(application_id, revision)`. A row is never edited.
- **Revisions:** a new decision, or an edit to the limit, issues revision 2 and marks revision 1 `superseded`.
- **Idempotency:** the approval transaction commits first. The letter job runs after commit, keyed on
  `(application_id, revision)`, so a retry cannot make a second letter.
- **Failure:** retry with backoff, at most three times (rule 17). After that, awaited `captureError`, and the
  queue shows "letter not issued, retry". A silent failure is the blind spot the three-stage doc warns about
  (Part 3).

### How it reaches the customer

- **Default: an email with a link** to the portal download. The PDF is not attached, because a credit limit in an
  email attachment outlives the portal. Attachment is a choice (D-P2-5).
- **In the portal:** the applicant downloads their own letters, newest first, with the superseded ones marked.
- **Verification page:** `/credit/verify/<code>`, public, rate limited, and it shows **only** the letter number,
  issue date and status (valid, superseded, revoked). It shows **no company name and no limit** (`POPIA-DATA-RULES.md`
  P-11). A code guessed by a stranger reveals nothing about the business or the person.

### Rejection letter

Default: an automatic rejection notice with no reason text and no limit. "Pexmart has reviewed your application
and is unable to approve it at this stage. Your account manager will contact you." Hein's note stays internal.
Susan may send a reasoned letter by hand (D-P2-6).

---

## 7. Customer communications, all automatic, all logged

Every row is a row in a comms log (`CreditApplicationEvent` or its ownership twin), with the template version, the
recipient, the time, and the send result. A message that cannot be sent is visible in the queue.

| Event | To | Channel | Shows | Limit |
|---|---|---|---|---|
| Application submitted | Applicant | Email | Application number, what happens next | Once per submit |
| Application received | Susan, and Pieter as backup | Push, bell, email | Number and company name | Per recipient per hour (10, ntfy precedent) |
| Missing documents | Applicant | Email | Missing list and a fresh link | Two reminders: day 3 and day 7 |
| Information requested | Applicant | Email | Susan's note and a link | Per request |
| Sent to Hein | Hein | Push, bell, email | Number | Per send |
| **Approved** | Applicant | Email with link | Letter is ready, link | Once per revision |
| **Approved, limit edited** | Applicant and Susan | Email with link | New revision, old one superseded | Once per revision |
| Rejected | Applicant and Susan | Email | Generic notice | Once |
| Returned to Susan | Susan | Push, bell, email | Hein's comment | Once per return |
| Ownership request received, filed, confirmed | Client contact | Email | Status words and the filing reference | Once per status |
| Registry change detected (source C) | Client contact and Susan | Email | What changed, the effective date, "not filed by Pexmart" | Once per event key |
| Filing clock | Susan and Hein | Push, email | Days left | Days 3, 7 and 8 |

All senders check the `autotest` prefix first and do nothing for it. Recipients come from the data (the users who
hold each permission), not from an environment variable. Tag keys: `credit:<number>`, `ownership:<number>`.

---

## 8. The ownership-change service (Stage 4)

**The same engine, not a copy.** `kind = 'ownership_change'` is the second discriminator, as the three-stage
doc requires. The state machine, the portal shell, the comms log and the letter code are shared modules. The
rows live in their own table, `OwnershipChangeRequest`. A single table with conditional columns would be harder
to audit, so it is not used.

**States:**

```
submitted ─► in_review (Susan) ─► with_hein (Hein)
                 │  ▲                 │
                 ▼  │                 ├─► approved_for_filing ─► filed ─► confirmed   [confirmed is terminal]
           info_requested            ├─► returned_to_susan
                                     └─► rejected                                   [terminal]
```

- **`filed` needs a filing reference** and the CoR39 acknowledgment in the private store. Without both, the
  request cannot move on.
- **`confirmed`** needs the CIPC record shown (a screenshot or a document, uploaded by Susan) or a matching feed
  event (source C, later).
- **Filing route:** in-house, through CIPC's own platform, or through a partner such as GovChain. The route is
  chosen per request. Cost and access are unverified (D-P2-3).
- **Fee:** Anchelene pays the filing fee or partner invoice, with Hein approving the payment. Filing is **not**
  blocked by an unpaid fee, because a block on a filing would stop people (rule 1). The fee status is shown.

**Source C (vendor watch), Stage 5 only, after a signed contract:**

- A `RegistryProvider` interface with three calls: `lookupCompany(regNo)`, `listOfficers(regNo)`,
  `changesSince(regNo, date)`.
- A `NullProvider` that makes no external call. It is the default, so Stage 4 ships without any vendor.
- The vendor is chosen by configuration. Its key is an environment secret, never in the code.
- A daily job per watched company compares the new officer list with the last stored snapshot, and creates events
  for the differences. Snapshots store **salted hashes** of names, so the diff works, plus roles and dates. Plain names live in the
  applicant file in the private store. **No ID numbers and no plain names in the database** (`POPIA-DATA-RULES.md` §12).
- A monthly call budget with a hard cap. At 80% of the budget, Susan and Hein are alerted. The job stops at 100%
  and says so. A silent stop is the failure the self-audit pattern exists to catch.

---

## 9. What to ask the vendors, in writing

1. **Coverage:** which entity types (Pty Ltd, CC, NPC) and which fields (directors, CC members, appointment and
   resignation dates, change history).
2. **Alerts:** is there a webhook or a daily change feed? Latency? A stable change ID for de-duplication?
3. **Price:** per call, monthly minimum, per watched company, setup, overage, and what happens at the cap.
4. **Resale and white-label rights:** can Pexmart pass the data, or the monitoring result, to its own clients as
   part of a paid service? Is sub-licensing allowed? **This is the "on-sell" question. Without a written yes, the
   on-sell model is not built.**
5. **CIPC terms:** does the vendor's licence from CIPC allow the resale in (4)? CIPC's eServices terms have an
   "Intellectual Property and restrictions on use" section (bizportal.gov.za/terms.aspx). Its text was not
   retrieved, so a lawyer reads it.
6. **POPIA:** an operator agreement, data location, retention and deletion, breach notice, and the list of
   sub-processors.
7. **Service:** uptime, support hours, exit terms and data return.

**Shortlist to send the RFQ to:** SearchWorks (Standard Bank), Datanamix, CompanyData, WinDeed (alerts). Lightstone
and Lexis only if the first four decline. GovChain as a **filing partner**, not a data feed. Apply to CIPC APIVerse
directly, in parallel. Sending the RFQ is an external action, so Carl sends it, or approves the text first.

**Cost model, to fill in when quotes arrive:** monthly cost ≈ watched companies × calls per company per day × 30 ×
price per call, plus any minimum. The charge to the client must cover that per client, with margin. A filing fee
pass-through (GovChain's R590, if confirmed) is a separate line.

---

## 10. Stages and acceptance (additions to PLAN §10)

- **Stage 1 (spine) now includes the approval letter.** Acceptance lines **A11–A14**:
  - **A11.** When Hein approves, the applicant gets an email with a link to the letter within a few minutes. The
    PDF shows the limit in figures and in words, Hein's signature, and the approval reference.
  - **A12.** The applicant downloads the same file from the portal.
  - **A13.** When Hein edits the limit, a new revision is issued, and the old one shows "superseded" on the
    verification page.
  - **A14.** Only the applicant, Susan, Pieter and Hein can open the letter. The verification page shows no limit.
- **Stage 2:** the comms log view, letter reissue by Susan, and the filing-clock reminders (for ownership, from
  Stage 4).
- **Stage 4: ownership-change service, in-house filing** (its own branch: `feat/…-ownership-change`). Sources A and
  B only. No vendor. Acceptance: Susan and Hein complete a real request on their phones, file it, and the client
  gets the confirmation.
- **Stage 5: vendor watch (source C).** Only after a signed contract and the written resale answer. Its own
  branch and its own acceptance.

**Stage 1 addition: credit information on Susan's delivery-release screen.** Susan already releases deliveries
(`delivery_release`, `src/components/layout/Sidebar.jsx:399`; `api/_lib/deliveryRelease.ts`). Add the client's
credit status there as **information only**: "CA-0001 approved, limit R…" or "no credit review on file". It must
not release or hold a delivery by itself. Carl decides any hold (D-P2-14).

---

## 11. Risks, refusals and what I did not verify

**Risks**

1. **Overpromising** "every ownership change". Mitigation: the wording in §2 goes in every quote.
2. **On-selling registry data** without a licence. Mitigation: no resale build until written permission (§9).
3. **Shareholding and beneficial owners** are not public, so they cannot be notified from a registry. Mitigation:
   client declarations only, said plainly.
4. **Late filing.** The clock, the reminders and the escalation (§4). The penalty amount was not verified. The
   liability sits with the company and its directors, so the service needs a legal review before it is sold.
5. **POPIA** on directors' personal information. Minimise: no ID numbers in snapshots, a legitimate-interest basis
   in the privacy notice, and an operator agreement with each vendor.
6. **Stopping people.** A delivery auto-held on an ownership notice would stop a driver or a clerk (rule 1). Flags
   only. Carl decides any hold.
7. **Name errors.** Wrong person, wrong permission. Mitigation: names confirmed (D-P2-1), and match by exact
   account.

**Refused**

- Auto-filing with CIPC without a signed resolution from the client.
- ID numbers in plain database columns.
- Ownership details by WhatsApp (switched off, rule 5) or by unauthenticated email. Requests come through the
  portal.
- Automatic approval of any letter.
- Reselling vendor data before a written licence.

**Not verified this session**

- The CIPC, GovChain, Standard Bank and acts.co.za pages were not fetched. Their host names do not resolve from
  this session, so the facts above come from search results and are marked as such. **To verify them, allow
  `www.cipc.co.za`, `www.govchain.co.za`, `acts.co.za` and `corporateandinvestment.standardbank.com` in the
  session's network settings.** Until then, treat every price and every claim in §1 as unconfirmed.
- The CC member form. The search did not confirm it. The CK2 name in the note is from memory.
- Whether Hein has a saved signature image today (the PR flow needs one, so it probably does). Check in Stage 0.
- Whether Hein's and Susan's permissions match the matrix in §5. Check in User Management.

---

## 12. Decisions for Carl (Part 2)

Defaults are what I would pick. Reply "go" to accept them, or change any of them.

- **D-P2-1. Names and titles. RESOLVED (Carl, 28 Oct 2026):** "Suzanne is Susan", Anchelene and Maroesjke. Titles
  still come from the org chart.
- **D-P2-2. The free-API answer.** Accept "no free feed; buy one after a written evaluation". Approve the RFQ
  shortlist in §9. **Default: yes.**
- **D-P2-3. Filing route.** In-house through CIPC's platform, or a partner such as GovChain. **Default: in-house,
  with GovChain as the fallback, after cost is confirmed.**
- **D-P2-4. Client promise wording** (§2). **Default: as written.**
- **D-P2-5. Approval letter delivery.** Link to the portal, or attachment. **Default: link.**
- **D-P2-6. Rejection letter.** Automatic and generic, or sent by hand by Susan. **Default: automatic, generic.**
- **D-P2-7. Letter validity** (review date) and numbering. **Default: 12 months, `CAL-CA-####-R#`.**
- **D-P2-8. Andre.** Visibility only, or sign-off above an amount you set. **Default: visibility only.**
- **D-P2-9. Pieter as backup intake.** **Default: yes, as with `delivery_release_backup`.**
- **D-P2-10. Maroesjke's escalation.** Escalate a delivery held for credit or ownership after how many days?
  **Default: 3 working days.**
- **D-P2-11. Deadline reading.** Conservative (from the effective date), pending the attorney's view. **Default:
  conservative.**
- **D-P2-12. Filing-clock reminders.** Business days 3 and 7, escalation on day 8. **Default: as written.**
- **D-P2-13. Who pays the filing fee.** Client pass-through, or absorbed by Pexmart. **Default: pass-through.**
- **D-P2-14. Credit on Susan's release screen.** Information only. **Default: information only, no automatic
  release or hold.**

---

## 13. Sources

Search results were used because the primary sites were not reachable. Each source is marked as the search found it.

- GovChain director change service: https://www.govchain.co.za/services/company-directors-change (search summary; not fetched)
- GovChain services: https://www.govchain.co.za/services (search result)
- CIPC director changes electronic: https://www.cipc.co.za/?p=9706 (search result; the page looks old)
- CIPC Notice 25 of 2026, director information: https://acts.co.za/news/blog/2026/05/cipc-notice-25-2026-director-information (search result; not fetched)
- Companies Regulation 39: https://www.acts.co.za/companies-act-2008/r351_39__directors_and_register_of_persons_disqualified_from_serving_as_director (search result)
- SearchWorks CIPC API (Standard Bank): https://corporateandinvestment.standardbank.com/cib/global/products-and-services/onehub/api-marketplace/cipc-information (search result; not fetched)
- SearchWorks news, pricing model: https://www.searchworks.co.za/Media/News/2024-04-03.pdf (search result)
- Datanamix CIPC Company Search Plus: https://www.datanamix.com/cipc-company-search-plus/ (search result)
- CompanyData CIPC API, including the APIVerse claims: https://companydata.com/cipc-api/ (search result; a vendor's own description)
- WinDeed alerts: https://www.windeed.co.za/?p=4309 (search result)
- Lexis SACompany: https://www.lexisnexis.com/en-za/lexissacompany (search result)
- Lightstone market analysis (no alert API found): https://www.lightstoneproperty.co.za/MarketAnalysis.aspx (search result)
- OpenCorporates pricing: https://opencorporates.com/pricing/ (search result, official page)
- OpenCorporates plug-in data: https://opencorporates.com/plug-in-our-data/ (search result)
- Beneficial ownership register access: https://cms.law/en/zaf/publication/access-to-the-beneficial-ownership-register (search result)
- Beneficial ownership, CIPC head on transparency (March 2026): https://www.businessday.co.za/news/2026-03-05-cipc-head-calls-for-more-beneficial-ownership-transparency/ (search result)
- Parliamentary reply on BO register access: https://pmg.org.za/committee-question/33890/ (search result)
- CIPC eServices terms: https://bizportal.gov.za/terms.aspx (search result; the restriction section was not retrieved)
- CC member change (secondary): https://accountingacademy.co.za/news/read/cipc-cc-transfer-of-member-s-interest (search result)
- Open-register monitoring model, Germany (for the webhook pattern only): https://openregister.de/en/changelog/monitor-api (search result)

Repo references (verified in this session):
`scripts/data/org-chart-2026-09-04.json`, `HANDOVER-HR-2026-09-25.md` (people table and grants),
`src/components/layout/Sidebar.jsx:399–402` (delivery release and backup),
`api/_lib/deliveryRelease.ts:227` and `:589` (Pieter as backup),
`api/_lib/permissionLabels.ts:67` (`delivery_release_backup`),
`api/_lib/email.ts` (`sendEmail` takes attachments),
`api/_lib/projectReportPdf.ts`, `api/_lib/trainingPdf.ts`, `api/_lib/productionSheetPdf.ts` (jsPDF on the server),
`prisma/schema.prisma:3472` (Susan's comment, "creditors clerk").
