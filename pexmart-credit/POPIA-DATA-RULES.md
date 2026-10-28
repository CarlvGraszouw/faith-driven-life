# POPIA: what we hold, how we ask, what we say

**Status: draft for Carl and Pexmart's attorney. Not legal advice.** Written 28 Oct 2026. Every consent wording and
notice below is a draft, and none goes live until Carl approves it, the same gate the driver location notice has
(`api/_lib/transportConsent.ts`: "subject to Carl's approval before go-live").

**Carl's words, verbatim** (28 Oct 2026):

> "There is a POPI compliance requirement as well that needs to be complied to. We need to get a client's approval
> through a tick box when they upload documentation to understand that they give us permission to access private
> information. We need to have a disclaimer to tell them that we are not saving any private information on any
> PixMod database, as these documents are downloaded and we're not saving their personal information in databases.
> So that's also part of the build."

*I have read "PixMod" as PexFlow. Confirm.*

---

## 1. The disclaimer has to be true, and the first design made it false

The plan so far stored applicant names, email addresses, phone numbers, trade references, company names and
registration numbers in database columns (`PLAN.md` §4). A disclaimer that says "we do not keep your personal
information in our database" would be untrue under that design. So the design changes first.

**Principle:** the database holds no personal information. Personal information is held in one private
applicant file, plus the uploaded documents and the approval letters, in the private file store, and it is deleted
on a fixed schedule. Guard tests enforce both halves (§9).

**What "private information" means in the notice** (one definition, used everywhere): names, contact details
(email, phone, postal address), identity and registration numbers, bank details, documents, references, and the
name and contact details of any director, member or referee. **Company names and company registration numbers are
treated as personal too.** POPIA's definition of personal information reaches an identifiable juristic person
"where applicable" (secondary sources; the attorney confirms), so the conservative reading costs little.

**Why the file store and not "nothing at all":** an upload has to persist until someone has reviewed it, and the
approval letter has to be downloadable later. Storing nothing is not possible for a working workflow. A file store
is still storage, so the notice must say where the files are, not pretend they are nowhere.

---

## 2. Data map: what, where, who sees it, how long

| Data | Example | Where | Who may see it | Kept for |
|---|---|---|---|---|
| Application reference | CA-0001 | **Database** | Susan, Hein, Pieter | Permanent. No personal information |
| Status, dates, staff ids | "with Hein, 3 Nov", Susan's id | **Database** | Staff with a credit permission | Permanent. Staff are internal |
| Approved limit and terms | R250 000, 30 days | **Database** | Susan, Hein, Pieter. Andre sees a summary. Marina sees status | Permanent. A business decision record. See P-9 |
| Consent record | notice `credit-notice-v1`, time, scope `upload` | **Database** | Susan, Hein, Information Officer | As long as the application record. No name, no IP address |
| Applicant file | name, email, phone, company name, registration and VAT numbers, address, trade references, typed consent name | **Private file store**, encrypted at application level | Susan, Hein, Pieter (backup) | Until the purge date |
| Documents | ID copies, bank letters, proof of address, company documents | **Private file store** | Same as above | Until the purge date |
| Approval letter | PDF: company name, limit, Hein's signature | **Private file store** | The applicant (their own), Susan, Hein, Pieter | Until the purge date. The database keeps the letter number, revision and hash |
| Email log | Template name, status, error | **Database** (`NotificationLog`) | Staff | Per the existing log policy. **No address, no recipient name** (§6) |
| Audit | "Susan viewed applicant file CA-0001" | **Database** (`AuditLog`) | Admins | Per the audit policy. **Ids only, never field values** (§6) |
| Error reports | none of the above | Sentry (EU) | Engineers | Scrubbed (§6) |

---

## 3. The consent tick box, at upload

**Where:** on the upload step, above the file picker. **Unticked by default.** Never pre-ticked.

**Rule:** the upload button is disabled until the box is ticked. The reason is written on the screen, as
visible text, not only in a tooltip (rule 11). The server enforces it too: the upload-token endpoint refuses any
upload without a current consent record for this application and the current notice version. The client check is
a convenience, not the gate.

**Each document row points to the consent record** that covered it, so Pexmart can show which permission applied
to which document.

**Withdrawal:** the applicant can withdraw from the portal at any time. Withdrawal stops the assessment, and the
applicant file and documents are purged on the next daily run (§7).

**Draft tick-box wording** (`credit-consent-v1`, for the attorney):

> ☐ I give Pexmart permission to access and read the personal information in the documents I am uploading, so
> that Pexmart can assess my application for credit. I have read the Information Notice, and I understand how my
> information is used, stored and deleted.

**Optional second tick at submit** (P-10, default yes):

> ☐ I confirm that the information I have given in this application is true and complete.

---

## 4. The disclaimer, beside the tick box

Plain words, no legal jargon, shown on the same screen as the tick box. **Every clause must be true of the built
system.** If a clause cannot be made true, the clause changes, not the system.

> **Pexmart does not keep your personal information in its database.** Your details and documents are kept in a
> private, access-restricted file store. They are used only to assess this application, and they are deleted 90
> days after a decision, or sooner if you ask us to. Our staff look at your documents on our secure system. You can
> read the full Information Notice before you upload anything.

**What makes each clause true:**

- "does not keep ... in its database": the schema guard (§9, test 1) and the live scan (§10).
- "private, access-restricted file store": the file-read rule (`credit/` is a private area, PLAN §6).
- "used only to assess this application": the purpose is written in the notice, and the file is never read for
  anything else. No other use is permitted: the build must not send applicant data to any other party, and a guard test checks it (§9, test 2).
- "deleted 90 days after a decision, or sooner if you ask": the purge job (§7), tested, with an alarm.
- "our staff look at your documents on our secure system": **only true if staff cannot keep copies** (P-4). This
  clause depends on a staff procedure as much as on code. Say so to Carl.

---

## 5. The Information Notice (POPIA section 18)

Given before the documents are collected. Secondary sources (not the Act's text) list these items. The attorney
checks the list against the Act.

1. The responsible party: Pexmart, its registered name and address.
2. The information collected, and where it is collected from (the applicant, and any referee or director they name).
3. The purpose: assessing an application for credit.
4. Whether supplying it is voluntary or mandatory, and what happens if it is not supplied (no credit decision).
5. Any law that requires or allows the collection. **None identified yet.** The attorney confirms.
6. Who receives it: Susan, Hein and Pieter, by role, and the operators in §8.
7. Whether it goes outside South Africa, and what protection applies there (section 72, §8).
8. How long it is kept, and how it is deleted (§7).
9. The applicant's rights: to see it, to correct it, to ask for deletion, to withdraw consent, and to complain to the
   Information Regulator. Contact: the Information Officer (P-5).

**Generated from code, not retyped** (the driver-notice pattern): the wording lives in `src/lib/credit/notice.js`
with a version string. Changing a word means a new version, and applications keep the version they were shown.

---

## 6. Staff rules that the disclaimer depends on

1. **View, do not download.** The credit detail page renders documents inline (`Content-Disposition: inline`, no
   download button). Every view is audited with the staff member's id and the application number, and no content.
   This is not airtight: a screenshot is possible. So P-4 asks Carl whether downloads are allowed under a
   procedure instead.
2. **No personal information in notes.** The decision note and the information-request note are validated by the
   server. A 13-digit number, an email address, or a phone-number pattern is refused, with the reason in words.
3. **No personal information in emails, pushes or subjects.** Email subjects are generic, for example "Pexmart
   credit application update". `sendEmail` writes its subject into `NotificationLog.templateName`, so a company
   name in a subject would be stored in the database. The ntfy push uses only the generic line in
   `api/_lib/ntfy.ts`, because ntfy is a public third-party service.
4. **Applicant recipients are not stored.** A credit notification writes `recipientId` and `recipientName` as null,
   and the entity id is the application id only.
5. **No personal information in an error report.** Captured errors carry ids. The applicant file is never passed
   to `captureError`, and the new keys are added to `SENSITIVE_KEYS` in the same change (rule 18).

---

## 7. Retention, withdrawal and deletion

- **Default retention:** 90 days after the decision, for the applicant file, the documents and the letters (P-3).
- **Purge job:** a daily job, wrapped in `withCronErrorReporting`. It deletes the **stored objects**, not only a
  database flag. The pattern is the one `purgeOldChat` already uses (`api/_lib/chat.ts`, 365-day purge), and the
  photo archive's 30-day rule (`api/_lib/photoArchiveNet.ts`).
- **Failure:** a purge that fails is retried with the usual backoff, then reported with an awaited `captureError`
  and an alarm. A self-audit counts applications past their purge date that still have stored files. Any such row
  raises an alarm. A silent purge failure is the failure the three-stage doc warns about (Part 2).
- **Withdrawal:** the applicant's withdrawal sets `withdrawn_at`. The next daily run purges, and staff are told the
  application is closed.
- **Deletion on request:** Susan or the Information Officer can delete an applicant's file early. The action is
  audited with the reason, and the database keeps the decision record.
- **Access and correction:** the applicant can see and download their own documents and letters from the portal.
  They can correct their details until the decision. After that, correction goes through the Information Officer.

---

## 8. Operators, transfers and breaches

**Operators** (POPIA section 21 needs a written agreement with each; confirm each one):

| Operator | Used for | Where data may sit | Check |
|---|---|---|---|
| Vercel | Hosting, Blob (private store) | Not stated in the repo (`vercel.json` has no region) | Region and DPA |
| Neon | Database | Not stated in the repo | Region and DPA |
| Resend | Email (`api/_lib/email.ts`) | Resend is a US company. Check where mail data is processed | DPA, and section 72 |
| Sentry | Error reports | EU (rule 4) | DPA |
| ntfy.sh | Push wake-ups | Third-party public service | Generic text only (§6) |
| WinSMS | SMS, not used for applicants | South Africa, to confirm | Not used for credit |

**Transfers abroad (section 72, secondary sources):** sending personal information outside South Africa is barred
unless a listed ground applies. The usual ground for a cloud provider is a contract that binds it to protection
substantially similar to POPIA's. If Resend, Vercel or Neon store data outside South Africa, Pexmart needs that
contract, and the notice must say so.

**Breaches (section 22):** a runbook, owned by the Information Officer. Detect (Sentry and staff reports),
contain (revoke the links, lock the file area), assess (what was exposed, to whom), notify the Information
Regulator and the people affected as soon as reasonably possible. The attorney drafts the notice wording. The
build's own test is that a leaked link cannot read another applicant (`PLAN.md` §11).

---

## 9. Build rules, as guard tests (red first, per the repo's rule)

1. **Schema guard.** Reads `prisma/schema.prisma`. For each credit model, every column must be on an allowlist
   (references, dates, statuses, business limits and terms, staff ids, consent id, letter fields). A column named
   like `email`, `phone`, `cell`, `address`, `name`, `id_number`, `passport`, `reg`, `vat`, `bank`, `account`,
   `reference`, `trade`, `director` or `iban` fails the build unless it is on the allowlist with a reason. The
   staff name fields are allowlisted as staff.
2. **Notification guard.** Credit senders write null recipient fields, a generic subject, and no address in error
   text. A test sends to a fixture applicant and asserts the `NotificationLog` row contains none of the address,
   the company name or the typed name.
3. **Push guard.** Credit pushes use only the generic constant.
4. **Audit guard.** Credit audit calls pass ids and actions, never field values.
5. **Consent guard.** Upload is refused without a current consent for the current notice version. A test with a
   stale version must be refused.
6. **Notice guard.** The tick-box and disclaimer text on the page equal the constants in `notice.js`.
7. **Purge guard.** Autotest rows past their purge date have their stored objects deleted. The test checks the
   objects, not the flag. An alarm test checks that a failed purge is reported.
8. **Decision-note guard.** A 13-digit number, an email address and a phone-number pattern are each refused.
9. **Sentry guard.** The new personal keys are in `SENSITIVE_KEYS`, and the scrubber is tested on them.

---

## 10. Live check, before go-live and after every release

A read-only scan (ENGINEERING_RULES §4) of the credit tables in production, for the test applicant's email address,
phone number and company name. **Expected: zero rows, in every table.** The scan is run by Carl or by the DB agent,
with the output pasted into the PR. A non-zero result blocks the release.

---

## 11. Decisions for Carl (POPI)

- **P-1. Approve the wording** of the tick box, the disclaimer and the notice, after the attorney has read them. Nothing
  goes live before this. **Default: drafts as written.**
- **P-2. Design.** No personal information in the database, personal information in the private file store with a
  purge. **Default: this design.** The alternative, database columns with a longer retention, would require the
  disclaimer to say so, and this document does not recommend it.
- **P-3. Retention.** 90 days after the decision, for the file store. **Default: 90 days.** Bexmart sets the real
  period. Shorter is safer under section 14 (no keeping records longer than necessary). Longer needs a stated reason.
- **P-4. Staff downloads.** View-only in the portal (default), or downloads allowed under a written procedure that
  requires local copies to be deleted at the decision. The disclaimer's last clause depends on this.
- **P-5. Information Officer.** Name the person, and confirm their registration with the Information Regulator.
  **Default: Carl until named.**
- **P-6. The attorney.** Engage to review the consent wording, the disclaimer, the notice (including the list in §5), the
  company-data question, the section 72 position, and the operator agreements.
- **P-7. Operators and data location.** Confirm the region and the DPA for Vercel, Neon and Resend, and whether
  Resend processes mail data outside South Africa. **Default: none signed yet. Nothing goes live until this is done.**
- **P-8. Company details.** Treated as personal, held only in the applicant file. **Default: yes.**
- **P-9. Approved limit and terms in the database.** Kept as a business decision record, with no personal
  information in the same row. **Default: yes.** Stricter alternative: move them into the file store too.
- **P-10. Second tick at submit.** **Default: yes.**
- **P-11. The verification page.** Shows the letter number, the issue date and the status. It shows neither the
  company name nor the limit. **Default: as written.** This changes `PART2-OWNERSHIP-AND-LETTER.md` §6.

---

## 12. Where this changes the earlier plan

- **`PLAN.md` §4 (data model):** `company_name`, `registration_number`, `vat_number`, `contact_name`,
  `contact_email`, `contact_phone`, `trade_references` leave the database. They go into the applicant file. The
  `CreditApplicationDocument` row keeps a pathname and a consent id, with no names.
- **`PLAN.md` §6 (portal):** the consent tick moves to the upload step. The disclaimer sits beside it.
- **`PLAN.md` §9 (notifications):** recipient fields are null for applicants, and subjects are generic.
- **`PART2-OWNERSHIP-AND-LETTER.md` §6:** the verification page drops the company name (P-11).
- **`PART2-OWNERSHIP-AND-LETTER.md` §8, Stage 5:** the officer snapshot stores salted hashes of names for the diff,
  and names live in the file store. Identity numbers appear only in the filing document.

---

## 13. What I could not verify

- Sections 18 and 72 come from secondary summaries. Sections 14, 21 and 22 are cited from memory. The official text
  was not retrieved. The attorney checks every section number against the Act.
- Whether POPIA's definition reaches juristic persons. The sources say "where applicable". The attorney decides.
- Where Vercel, Neon and Resend store data. The repo does not say. `vercel.json` has no region.
- Whether Vercel Blob encrypts at rest. The application-level encryption of the applicant file is a recommendation
  until that is confirmed.
- Whether the PexFlow admin roles can already read credit files through another route. Check in Stage 0.

## Sources (search results, secondary)

- [POPIA section 18 notification summary (Lightstone)](https://www.lightstoneproperty.co.za/narrative/Section18-Notification.aspx)
- [POPIA section 18 summary (Schindlers)](https://www.schindlers.co.za/the-conditions-of-lawful-processing-of-personal-information/)
- [POPIA definitions, including juristic persons (MJK)](https://mjkinc.co.za/popia/definitions)
- [POPIA companies and B2B (MJK)](https://mjkinc.co.za/popia/companies-and-b2b)
- [Trans-border data transfers (CMS)](https://cms.law/en/zaf/legal-updates/Managing-cross-border-data-transfers)
- [PER article on section 72 and the cloud (PER/PELJ)](https://www.saflii.org/za/journals/PER/2024/39.html)

Repo references: `api/_lib/transportConsent.ts` (versioned notice gated on Carl's approval), `PersonSignature` in
`prisma/schema.prisma` (consent precedent, which also stores the typed name in the database and is therefore not
copied for applicants), `api/_lib/chat.ts` (`purgeOldChat`), `api/_lib/photoArchiveNet.ts` (`BLOB_RETENTION_DAYS`),
`api/_lib/email.ts` (`logAttempt` writes `templateName` and `recipientName`), `api/_lib/ntfy.ts` (generic line).
