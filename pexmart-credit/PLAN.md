# Pexmart Credit: end-to-end build plan

**Status: plan, not built.** Written 28 Oct 2026 from a read of `CarlvGraszouw/pexflow-production`
(branch `main`, commit `0fd50b5`). The build happens in that repo. This folder holds the spec and the
build script, and changes nothing in the app.

**Revision 2 (28 Oct 2026), after Carl's second request.** Read `PART2-OWNERSHIP-AND-LETTER.md` with this file.
What changed here:

- **D4 is reversed.** Hein's approval now triggers an **automatic approval letter**, emailed to the applicant
  with a link to a portal download. The letter shows the approved limit, signed with Hein's saved signature.
  Susan no longer has to tell the applicant by hand. The letter is generated after approval, never as an approval.
  Acceptance lines A11–A14 are added to Stage 1 (Part 2 §10).
- **The roles are corrected** against the organogram (4 Sep 2026): Susan Kruger is Accounts Receivable, not
  creditors clerk. Anchelene Pieterse is Accounts Payable. Maroesjke van der Walt is listed as Operations
  Manager. Names need confirming (Part 2 D-P2-1).
- **Part 2 adds the ownership-change service** (Stage 4) and a registry-data question. There is **no free
  API** for director or member changes that I could confirm (Part 2 §1).

**Revision 3 (28 Oct 2026).** Naming resolved: Pexmart, not Bex. Susan is Suzanne, Anchelene is Angeline, and
Maroesjke is Marushka (Carl, 28 Oct 2026). **The data design changed:** the database holds no personal
information, and personal information is kept in a private applicant file that is purged on a schedule.
Consent is captured with a tick box at upload. See `POPIA-DATA-RULES.md`, which governs §4, §6 and §9 here.

**Request (Carl, 28 Oct 2026), the source of this spec:**

> "We need to build a Bex credit section for all our debtors, where people will be able to apply for
> credit with Bexmart. So it will be a customer facing portal that our clients can access via a link
> that is emailed to said customer…"

> "…that submission will be flagged to Susan at Bexmart, and she will be informed that an upload has
> just been done by a client requesting a credit."

> "We want to have that same workflow duplicated between Susan and Hein, but this time Hein is not
> approving purchase requisitions, but he will be approving credit applications that has been applied
> for, and he will be able to reject, edit, lower credit limit, and comment related, and then send that
> back to Susan as an approval or rejection or comment."

**Naming (resolved by Carl, 28 Oct 2026).** The company is **Pexmart**, the app is **PexFlow**
(`pexflow-production`), and Carl's email is `@pexmart.co.za`. The request's "Bex" and "Bexmart" were transcription
errors for "Pex" and "Pexmart". Quoted words stay verbatim, as Carl said them. Everything else uses Pexmart.

---

## 0. What I found

1. **The workflow to duplicate already exists.** Bianca's purchase requisition, decided by Hein, is the
   `PurchaseRequisition` model (`prisma/schema.prisma:2915`) and `decidePurchaseRequisition`
   (`api/functions/[name].ts:5288`). It requires `gm_financial_approval`, reads Hein's saved signature
   from the database, snapshots history before an amendment overwrites anything, audits, and notifies.
   Mirror its shape. Do not copy its functions.
2. **Nothing exists for an outside customer.** Nothing I read lets an outside customer in. The business
   screens and data endpoints all need a PexFlow login. The nearest precedent is the Pipe Inspection ticket (`api/_lib/pipeInspectionTicket.ts`): a
   60-second, single-use JWT signed with its own secret. It hands a staff member into another app. It
   does not let an outsider in. The customer portal's access model is new, and it is the riskiest part.
3. **Susan is already in the code.** `schema.prisma:3472` calls her "the creditors clerk", and `Sidebar.jsx:399`
   gives her the delivery release. The organogram (4 Sep 2026) lists **Susan Kruger as Accounts Receivable**, which
   fits credit control on customers. `SAVE.md:4164` records that she has no PexFlow account as of the last
   handover. I am treating this as the same Susan. Her account is a dependency (ENGINEERING_RULES §10).
4. **There is a file-privacy gap to close first.** `api/file.ts` lets any active staff member open any
   upload except the private areas `hr/`, `training-material/` and `chat/` (`api/_lib/fileAccess.ts:284`).
   As it stands, every staff member could open applicants' bank letters and ID copies. `credit/` must join
   the private areas before any upload goes live.
5. **GitHub gave no reusable credit code.** I searched `pexflow-production` for debtor, credit application and
   credit application. The useful reuse is the requisition workflow, not a library. I did not open the
   other private repos in the account. `pexmart-fms` might hold debtor or credit data. Tell me if it does
   and I will attach it read-only.
6. **The repo's rules are the build's constraints.** `CLAUDE.md`, `ENGINEERING_RULES.md`,
   `BUILD-PROTOCOL.md`, `docs/standards/THREE-STAGE-BUILD-AND-SAFETY-NETS.md` and
   `docs/WINDOWS-WORKSTREAM.md`. Section 12 applies them.

---

## 1. Reuse map

| Requisition (exists) | Credit (new) | How |
|---|---|---|
| `PurchaseRequisition` model | `CreditApplication` + `CreditApplicationLink` + `CreditApplicationDocument` | New models, same conventions: cuid ids, snake_case `@map`, Json house style |
| `prNumber` via `NUMBER_FIELD` (`api/_lib/models.ts:87`) | `CA-0001` via `NUMBER_FIELD` | Mirror |
| Status chain `submitted → quoted → approved_for_payment / rejected`, with `needs_info` and amendment loops | `awaiting_documents → submitted → in_review → with_hein → approved / rejected`, loops through `awaiting_client` and `returned_to_susan` | Mirror the shape |
| `decidePurchaseRequisition`: `gm_financial_approval`, signature snapshot, audit, notify | `decideCreditApplication`: `credit_approval`, signature snapshot, audit, notify | Mirror |
| `amendmentHistory`: snapshot before overwrite | `editHistory`: snapshot before any Hein edit | Mirror |
| `rejectionNote`, required on reject | `decisionNote`, required on reject and on return | Mirror |
| `src/lib/prStatus.js`: one status module | `src/lib/credit/creditStatus.js` | Mirror (one definition, rule 9) |
| `api/_lib/procurementNotifications.ts` | `api/_lib/creditNotifications.ts` | Mirror |
| `api/upload.ts`: private-store credential, refuses to fall back to public | Reuse the credential helper. Never the public store | Reuse |
| `api/file.ts`: `PRIVATE_FILE_AREAS` | Add `credit/` with its own read rule | Extend |
| `api/cron/gm-approval-reminder.ts` | `api/cron/credit-application-watch.ts` with a self-audit | Mirror, then add the self-audit |
| Pipe Inspection ticket (JWT, separate secret) | Not used. The portal uses an opaque hashed token | New, on purpose (§6) |
| `kind` discriminator (`PurchaseRequisition.category`, `TransportTrip.tripType`) | `kind = 'pexmart_credit'` from day one | Carry it (three-stage rule, point 3) |

---

## 2. Locked spec: acceptance statements

Carl's list is the spec. Each line below is checked by a person doing the work on a phone. Tests support
these lines; they do not replace them.

**Stage 1: the spine. All of A1–A18 must be true before Stage 1 is done.** A11–A14 are the approval letter,
specified in `PART2-OWNERSHIP-AND-LETTER.md` §10.

- **A1.** Carl or Susan sends an applicant a link by email. The applicant opens it on a phone with no PexFlow login.
- **A2.** The applicant sees the documents checklist and can download the terms, the credit policy and the POPIA notice. These are Pexmart's PDFs.
- **A3.** The applicant ticks consent, types their name, fills the company details and requested limit, uploads each required document, and presses Submit. An upload that is too large or the wrong type is refused, and the reason shows on the screen.
- **A4.** On submit, Susan gets a push, a bell notice and an email saying a credit application was uploaded, with its number. The email body carries no personal details.
- **A5.** Susan opens the application and each document. She can request more information (the applicant gets a fresh link) or send it to Hein. Send is refused, with the reason on screen, until every required document is present.
- **A6.** Hein sees the application in his queue and can:
  - **approve**, with a limit equal to or lower than the requested limit, terms, and his saved signature;
  - **reject**, with a reason;
  - **edit** the approved limit, terms and conditions, keeping the previous values;
  - **return to Susan** with a comment (the comment is required).
- **A7.** Susan is told each time Hein decides or comments. She tells the applicant the outcome herself (D4).
- **A8.** Nobody without `credit_intake` or `credit_approval` can open a credit document, including by pasting its link. Every document open is audited.
- **A9.** An applicant sees only their own application. The link stops working when it expires or is revoked.
- **A10.** A double tap on Submit, Send or Approve does one thing, not two.
- **A15.** Upload is refused until the consent box is ticked, with the reason on screen. The applicant sees the
  disclaimer beside the box, and the Information Notice opens from it.
- **A16.** A live scan of the credit tables, for a test applicant's email, phone and company name, returns zero rows.
- **A17.** Withdrawal, or a deletion request from Susan, removes the stored applicant file and documents on the next
  run, and the test checks the objects, not a flag.
- **A18.** Each document row points to the consent that covered it.

**Stage 2: instrumentation.** Audit timeline per application. Decision letter (PDF) with the signature.
Reminders and escalation for stuck applications, with a self-audit. An alarm if nobody holds
`credit_intake` or `credit_approval`. An endpoint refusal monitor on the public routes. Search and filters.
A turnaround report.

**Stage 3: extension.** Editing of applicant-supplied details, with a reason and a snapshot. Re-application
linked to the earlier one. A second applicant `kind` configured through `kind`, not a copied module.
Document-expiry reminders.

---

## 3. Workflow

```
Carl or Susan issues link ──► awaiting_documents
Applicant submits ─────────► submitted           (Susan notified)
Susan opens ───────────────► in_review
   ├─ request info ────────► awaiting_client ──(applicant resubmits)──► submitted
   └─ send to Hein ────────► with_hein           (Hein notified)
         Hein:
         ├─ approve (limit ≤ requested, signature) ─► approved            [terminal]
         ├─ reject (reason required) ──────────────► rejected            [terminal]
         └─ return to Susan (comment required) ────► returned_to_susan
                    Susan: send to Hein again │ request info │ …
Hein edits limit, terms or conditions while with_hein: snapshot first, status unchanged.
```

Hein cannot raise the limit above the requested amount (D6). A raised limit is a new application.

---

## 4. Data model

One additive SQL file: `scripts/2026-10-28_credit_applications.sql`. It is safe to run twice. The Prisma
models carry the same comment the on-hold columns carry (`schema.prisma:3147`): created outside Prisma,
declared so that `prisma db push` never drops them. Each model maps to its table with `@@map`, as the existing models do.

- **`CreditApplication`** (Revision 3: **no personal information**, see `POPIA-DATA-RULES.md` §2): `id`,
  `number` (CA-0001), `kind` (`pexmart_credit`), `status`, `requested_limit`, `requested_terms`, `consent_id`
  (a link to the consent record, which holds the notice version and the time, not a name), `submitted_at`,
  `intake_by`, `intake_by_name` (staff), `sent_to_hein_at`, `approved_limit`, `approved_terms`, `conditions`,
  `decision_note` (validated: no ids, emails or phone numbers), `decided_by`, `decided_by_name` (staff),
  `decided_at`, `approver_signature_url` (staff snapshot), `edit_history` (Json, decision values only),
  `revision_count`, `info_request_note` (validated), `info_requested_at`, `withdrawn_at`, `purge_after`,
  `created_at`, `updated_at`.
  **Removed in Revision 3:** `company_name`, `registration_number`, `vat_number`, `trading_address`,
  `contact_name`, `contact_email`, `contact_phone`, `trade_references`, `consent_name`. They live in the
  applicant file in the private store (`POPIA-DATA-RULES.md` §1). The schema guard test enforces this (§9).
- **`CreditApplicationLink`**: `id`, `application_id`, `token_hash` (unique, SHA-256), `created_by`,
  `created_at`, `expires_at`, `revoked_at`, `last_used_at`.
- **`CreditApplicationDocument`**: `id`, `application_id`, `doc_type`, `pathname` (private store),
  `filename`, `content_type`, `size_bytes`, `sha256`, `uploaded_at`, `removed_at`, `removed_by`. Never a
  public URL.
- **`CreditApplicationLetter`** (added in Revision 2, Part 2 §6): `id`, `application_id`, `revision`, `status`
  (`issued`, `superseded`, `revoked`), `issued_at`, `issued_by`, `approved_limit` (snapshot), `sha256`, `pathname`,
  `verification_code_hash`. Unique on `(application_id, revision)`. Rows are never edited.

The document types, statuses and limits live in `src/lib/credit/` (no Prisma import), so the browser and
the API read one definition. `api/upload.ts` already imports from `src/lib` this way.

---

## 5. Permissions

- **`credit_intake`**, "Credit applications: intake (Susan)". Sees the queue, opens documents, requests
  information, sends to Hein.
- **`credit_approval`**, "Credit applications: approval (Hein)". Sees the queue, opens documents, approves,
  rejects, edits, returns.
- Both are added to `api/_lib/permissionLabels.ts` and to the UserManagement tick list.
- **Explicit grants only.** Admin does not get them implicitly (D3). Admin access to applicants' bank
  letters and ID copies is a POPIA decision, not a default.
- Hein already holds `gm_financial_approval`. Do not reuse it. That key approves purchase requisitions,
  and a new capability gets a new permission (ENGINEERING_RULES §6).
- Permissions are read from the stored `AppUser` on every request, never from the request body.

---

## 6. The public portal: security design

This is the part that can hurt. The rest is ordinary code.

**Link token**

- 32 random bytes from `crypto.randomBytes`, base64url. The database stores only the SHA-256 hash. A
  database leak does not yield working links.
- Valid 14 days (D7). Revocable. Issuing a new link revokes the old ones.
- **Multi-use within the expiry, not single-use.** Email scanners open links before the applicant does.
  A single-use token would be burned before the applicant saw it.
- **The token appears in the URL once.** `GET /credit/apply/<token>` calls an exchange endpoint, which sets
  an `HttpOnly; Secure; SameSite=Strict` cookie with a two-hour sliding expiry, then redirects to
  `/credit/apply` with no token. Otherwise the token would sit in browser history, in the request log, and
  in the `Referer` sent to anything the page loads.
- If the cookie is signed, it uses its own secret, never `JWT_SECRET`. Same precedent as the pipe ticket.

**Headers** on the portal route and on `/api/credit-portal/*`: `Referrer-Policy: no-referrer`,
`X-Robots-Tag: noindex, nofollow`, `Cache-Control: no-store`. The portal loads no third-party scripts. The
service worker already sends `/api/` straight to the network (`public/sw.js:201`). The portal shell must
never be cached with a token in it.

**Upload**

- Direct client upload through `@vercel/blob` `handleUpload`, as `api/upload.ts` does. The token-minting
  step checks the portal cookie and the application status (`awaiting_documents` or `awaiting_client`).
  It does not call `getAuthUser`.
- **Private store only.** Refuse if the private credential is missing. Never fall back to the public store.
  `api/upload.ts` explains in detail why.
- The pathname is generated on the server: `credit/<CA-number>/<doc_type>/<uuid>.<ext>`. The applicant never
  chooses it.
- Allowlist: PDF, JPEG, PNG (D8). Size cap 10 MB each (D8). Check magic bytes after upload, not only the
  declared type.
- A document row is written only after the upload callback succeeds. A failed upload leaves no row.

**Consent and personal data**

- **Consent at upload** (Revision 3, Carl's words, 28 Oct 2026: a tick box "when they upload documentation").
  An unticked box is required before any upload. The server refuses an upload without a current consent for the
  current notice version. The wording is drafted, unapproved, and waits for Carl's approval (`POPIA-DATA-RULES.md` §3).
- No personal fields in logs, Sentry, or test fixtures (rule 18). `contact_email`, `contact_phone`,
  `registration_number`, `vat_number`, `trade_references` and any bank-related key are added to
  `SENSITIVE_KEYS` (`api/_lib/sentry.ts:18`) in the same change that introduces them.
- Applicant emails carry the link, or a plain confirmation with the application number and the applicant's
  name, nothing more.

**Read path**

- `api/file.ts`: add `credit/` to `PRIVATE_FILE_AREAS`, with `decideCreditFileRead`. It allows a user who
  holds `credit_intake` or `credit_approval` and whose application exists. Each read is audited, as the
  `hr/` path does.
- **Hard gate:** no upload goes live until `tests/file-privacy-paths-s3.test.ts` is extended and green.

**Rate limits**

- Exchange, upload-token and submit are limited per IP and per token. Refusals are counted for the Stage 2
  monitor.
- Before adding one, check what already exists: `api/_lib/queryGuard.ts` and the `EndpointCallStat` model.

**Endpoint shape**

- The repo folds endpoints into dispatchers: `api/functions/[name].ts`, `api/entities/[name].ts`,
  `api/stale-functions/[name].ts`. Add one public dispatcher, `api/credit-portal/[name].ts`, and new staff
  functions in `AUTHENTICATED_FUNCTIONS`. Do not add a top-level file under `api/` per endpoint. Check the
  deployed function count before the first deploy.

---

## 7. Endpoints

**Public: `/api/credit-portal/<name>`**

| Name | Method | Does |
|---|---|---|
| `session` | GET `?t=` | Exchanges the token for the cookie, then redirects |
| `me` | GET | Application summary, checklist, status words for the applicant |
| `details` | POST | Company fields, requested limit and terms, consent. Only in `awaiting_documents` or `awaiting_client` |
| `upload-token` | POST | Mints the `handleUpload` token into `credit/…`, after the cookie and status checks |
| `documents/remove` | POST | Removes the applicant's own document before submit |
| `submit` | POST | Checks every required document, consent and details. Conditional `updateMany` on status, verifies the count, notifies Susan |

**Staff: `AUTHENTICATED_FUNCTIONS`**

| Function | Who | Does |
|---|---|---|
| `issueCreditApplicationLink` | `credit_intake` | New link, revokes old ones, emails the applicant |
| `requestCreditApplicationInfo` | `credit_intake` | Sets `awaiting_client`, note required, issues a fresh link |
| `sendCreditApplicationToHein` | `credit_intake` | Checklist must pass. Conditional on `in_review` or `returned_to_susan` |
| `decideCreditApplication` | `credit_approval` | Approve or reject. Approved limit ≤ requested. Signature read from the DB. Conditional on `with_hein` |
| `editCreditApplicationTerms` | `credit_approval` | Limit, terms, conditions. Snapshot first. Conditional on `with_hein` |
| `returnCreditApplicationToSusan` | `credit_approval` | Comment required. Sets `returned_to_susan` |

Generic PATCH is blocked for every credit field through `PROTECTED_FIELDS` (`api/_lib/auth.ts:669`). The
credit models are **not** added to `MODELS` (`api/_lib/models.ts`), so there is no generic route at all.

---

## 8. Screens

- **Staff.** A "Credit applications" entry in the nav, visible to either permission. The route sits behind
  `PermissionGate`, and `tests/landing-never-access-denied.test.ts` must stay green.
- **Queue.** Status colours come from `creditStatus.js` only. A count is never shown above an empty area
  (Part 6 of the three-stage doc).
- **Detail (Susan and Hein).** Applicant details, documents (opened through `/api/file`), a checklist that
  flags anything missing, a history timeline, the decision panel.
- **Hein's panel.** Approve (limit defaults to requested; the limit rule is shown in words), Reject (reason),
  Edit terms, Return to Susan (comment). Each disabled button says why, as visible text, and carries
  `data-touch-reason="visible"` (rule 11).
- **After an action**, the result scrolls into view (Part 6, rule 3).
- **Applicant portal.** Phone first, 16px side gutter, no horizontal scroll at 360px. Steps: consent and
  details → documents checklist with the public PDFs → uploads with progress and a reason per file → review
  and submit → confirmation with the application number. No PexFlow navigation, no login UI.

---

## 9. Notifications and safety nets

- **Every sender** checks for the `autotest` prefix as its first line and does nothing for it (rule 6).
- **Rate limits** per recipient per run and per hour (the ntfy precedent is 10 per hour,
  `api/_lib/ntfy.ts:55`). Tag key `credit:<number>` so repeats replace each other. Retries back off
  (500 ms, then 1.5 s) and stop at three. After that, an awaited `captureError` and no more attempts (rule 17).
- **Who is told:** Susan on submit, on Hein's decision, and on a return. Hein when a file is sent to him.
  Push, bell and email. Recipients come from the data: the `AppUser`s holding each permission, never an
  environment variable.
- **Stage 2 safety net:** `credit-application-watch`, wrapped in `withCronErrorReporting`. It reminds Susan
  after one working day in `submitted`, and Hein after two in `with_hein`, then escalates to admins. Its
  self-audit raises an alarm for any application past the grace period with no notification attempt. It
  also alarms when no `AppUser` holds `credit_approval`, the same check `gm-approval-reminder` makes.
- **Idempotency markers** are stamped only inside the branch that actually sent (three-stage doc, Part 2).

---

## 10. Build stages (three-stage rule)

Each stage is accepted by a named person doing real work, not by a green suite.

- **Stage 0: preflight and decisions.** Record the baseline on the build machine: test count, typecheck count,
  lint count. Carl answers D1–D10. Susan and Hein have PexFlow accounts with the right permissions, or Carl
  creates them. Carl creates a Neon dev branch for the builder's `.env`.
- **Stage 1: spine (A1–A18).** Ships complete. No Stage 2 item gates it.
- **Stage 2: instrumentation.** Its own branch and PR.
- **Stage 3: extension.** Its own branch and PR.

---

## 11. Tests

- **Test first, for each acceptance line.** A failing test that names the missing behaviour, then the
  code, then the same test green (ENGINEERING_RULES §1).
- **DB-free (`npm run test:source`)**: state transitions; approved limit ≤ requested; token hash, expiry and
  revocation; upload allowlist and magic bytes; the required-documents gate; the `credit/` read decision; the
  scrubber on the new sensitive keys; notification gating (`autotest`, rate limit, retry maximum); double
  submit against a fake store.
- **DB (CI only, test branch, `autotest` rows):** the full spine, plus reject, the return loop, a double tap,
  cross-applicant access refused, an expired link refused, a revoked link refused.
- **Guards that must stay green:** `landing-never-access-denied`, `touch-reachable-reasons`,
  `control-reachability`, `file-privacy-paths-s3` (extended), `upload-reference-contract` (for the new
  uploader), `whatsapp-off`, `date-only-coercion` (`expires_at` is a moment), `no-cli-prod-deploy`.
- **Fixtures** for tokens and upload pathnames are produced by the production functions, never typed by hand
  (three-stage doc, Part 5).
- **Adversarial pass before go-live:** wrong token, expired, revoked, another applicant's id, oversized file,
  a disguised file (say, an executable renamed to .pdf), a replayed upload callback. Every one must be refused.
- **Live (stage gate):** Susan and Hein each complete A1–A10 on their own phone (A11–A18 as below) against the preview, with a test
  application using the `autotest` prefix or Carl's own address, so no real person is emailed.

---

## 12. Release path

- **Branches:** `feat/2026-10-28-pexmart-credit-spine` for Stage 1, from the current `origin/main`. Later stages get
  their own branches. Nothing is pushed to `main` (Windows workstream §1).
- **Schema first:** the additive SQL file goes to the builder's Neon dev branch only. Carl runs it on production
  by hand before the code deploys (ENGINEERING_RULES §5, rule 7). New code reads the new columns, so the order
  matters.
- **Gates before every push:** `npm run test:source`, `node scripts/typecheck-budget.mjs`, `npm run build`, then
  `git checkout -- api/_lib/buildInfo.ts`, because the build rewrites that file.
- **CI** runs `guards` and `test` on the PR. Release branches run them too (`.github/workflows/test.yml`).
- **Carl merges on green.** The merge is the release. Nobody else merges.
- **After deploy:** `npm run verify:deploy -- --expect "<a string unique to this change>"`. Then a
  `prove-done` receipt against the deployed preview: `scripts/prove-done.mjs`, spec `specs/pexmart-credit-spine.json`,
  with `--expect-bundle` set to the bundle the deploy built. Carl runs it, because it signs as a real admin
  from the production database, which a builder's dev `.env` must not hold.

---

## 13. Refused for this build

- Automatic credit scoring or auto-approval.
- Bank account verification, or any credit bureau.
- An e-signature provider. Hein's saved signature image is used, as purchase requisitions use it.
- Online payments.
- WhatsApp, or SMS of any kind (rule 5; WhatsApp is switched off).
- Public listing or search of applications.
- A separate Vercel project or subdomain in Stage 1. Keeping permissions in one place is the reason; the
  pipe-inspection note makes the same call.
- Virus scanning (D9). It is not part of the spine.
- A decision email whose body states the limit. The limit lives in the approval letter, which the applicant
  downloads through the portal (Part 2 §6). The verification page never shows it.
- Raising a limit above the requested amount (D6).
- OCR of documents.

---

## 14. Risks

1. **The public upload endpoint is the largest new attack surface.** Mitigations are in §6, and the adversarial
   pass in §11 is a go-live condition.
2. **The file-read gap** until `credit/` is private. Hard gate (§6).
3. **POPI.** ID copies, bank letters, contact details and trade references are personal information. The
   disclaimer ("we do not keep your personal information in our database") is true only if the database holds none
   of it. The schema guard, the notification guard and the live scan enforce that. Retention, consent wording and
   the operator agreements need Carl's approval and the attorney's review (`POPIA-DATA-RULES.md` §11, P-1 to P-11).
4. **Susan's account.** The last handover records that she has none. That lead time is Carl's to clear, not the
   build's. Until it clears, Susan cannot accept Stage 1.
5. **A forwarded link.** Anyone holding it can use it for 14 days. Mitigation: short expiry, revoke-on-resend,
   and the portal shows only that application, never staff data.
6. **Races** on Submit, Send and Approve, from a double tap or two staff members. Conditional `updateMany` on the
   status, and the count verified (ENGINEERING_RULES §7).
7. **Production DDL is human-run.** A deploy before the SQL runs breaks the new screens. The order is SQL, then code.
8. **This is a live system.** The portal URL sits on the production domain, and test rows are real rows. Live tests
   use the `autotest` prefix or Carl's address.
9. **The brand name.** Resolved: Pexmart (Carl, 28 Oct 2026). Wording on the public pages still needs Carl's
   approval, because it cannot be unsent once a client has seen it.
10. **The build machine.** Windows clones fail when they sit in OneDrive, when line endings are wrong, when a push
    goes to `main`, or when `ship-item.mjs` is used (it needs `.vercel/project.json`, which is gitignored, and
    its own error message points at a Mac path). The build script follows the Windows workstream doc and never
    uses `ship-item.mjs`.
11. **Gates not yet recorded.** The baseline counts are not in this plan. Stage 0 records them on the build machine.
12. **The letter's legal weight.** The approval letter carries Hein's captured signature image and an approval
    statement with a timestamp and a reference. That is an electronic record. Whether it is enough for Pexmart's
    purposes is for Pexmart's attorney to decide. The build does not claim more than that.

---

## 15. Decisions for Carl

Defaults are what I would pick. Reply "go" to accept them, or change any of them.

- **D1. Brand text. RESOLVED.** "Pexmart Credit", as one constant. The company is Pexmart (Carl, 28 Oct 2026).
- **D2. Susan.** Susan Kruger, creditors clerk, needs a PexFlow account with `credit_intake`. **Default: yes.**
- **D3. Admin access.** Admin does not get either credit permission implicitly. **Default: explicit grants only.**
- **D4. Telling the applicant. SUPERSEDED by Carl, 28 Oct 2026.** An automatic approval letter is emailed to the
  applicant, with a link to a portal download and the limit inside the PDF. The rejection notice is automatic and
  generic. See Part 2 §6–7 and D-P2-5 and D-P2-6.
- **D5. Documents and consent.** Pexmart supplies the consent wording, the checklist, and the three public PDFs
  (terms, credit policy, POPIA notice). **Default: placeholders marked "awaiting Pexmart".**
- **D6. Hein's edit scope.** Stage 1: limit, terms and conditions only. Applicant-supplied fields come in Stage 3.
  Hein cannot raise the limit above the requested amount. **Default: as written.**
- **D7. Link validity.** 14 days. Issuing a new link revokes the old ones. **Default: 14 days.**
- **D8. Uploads.** PDF, JPG and PNG. 10 MB each. No HEIC in Stage 1. **Default: as written.**
- **D9. Virus scanning.** Not in Stage 1. **Default: not in Stage 1.**
- **D10. Retention.** Superseded by **P-3** in `POPIA-DATA-RULES.md` §11: 90 days after the decision, purged by a
  daily job that deletes the stored objects. Pexmart sets the final period.
- **D11. POPI.** Decisions P-1 to P-11 in `POPIA-DATA-RULES.md` §11. Nothing goes live before P-1, P-6 and P-7.

---

## 16. What I could not verify

- **The install and the gates did not run** in the session that wrote this plan. The dependency install was refused
  by the environment's auto-mode classifier, so there are no baseline counts yet. The commands in the build script
  come from `package.json` and `docs/WINDOWS-WORKSTREAM.md`. They are untested on this machine.
- **Current account state** for Susan and Hein. `SAVE.md` is a dated note, not a live check.
- **Whether a generic rate limiter already exists.** `queryGuard.ts` and `EndpointCallStat` are there. Whether either
  fits is not checked.
- **Other private repos** in the account were not opened (see §0, point 5).
