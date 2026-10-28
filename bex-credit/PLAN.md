# Bex Credit: end-to-end build plan

**Status: plan, not built.** Written 28 Oct 2026 from a read of `CarlvGraszouw/pexflow-production`
(branch `main`, commit `0fd50b5`). The build happens in that repo. This folder holds the spec and the
build script, and changes nothing in the app.

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

**Naming.** The request says "Bexflow" and "Bexmart". The repo is `pexflow-production`, the company is
Pexmart, and Carl's email is `@pexmart.co.za`. This plan assumes Bex = Pex. If Bex is a separate brand,
say so before Stage 0.

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
3. **Susan is already in the code.** `schema.prisma:3472` says "Susan is the creditors clerk", and
   `Sidebar.jsx:399` gives her the delivery release. `SAVE.md:4164` records "Susan Kruger and Pieter Marais
   have no PexFlow account" as of the last handover. I am treating this as the same Susan. Her account
   is a dependency (ENGINEERING_RULES §10).
4. **There is a file-privacy gap to close first.** `api/file.ts` lets any active staff member open any
   upload except the private areas `hr/`, `training-material/` and `chat/` (`api/_lib/fileAccess.ts:284`).
   As it stands, every staff member could open applicants' bank letters and ID copies. `credit/` must join
   the private areas before any upload goes live.
5. **GitHub gave no reusable credit code.** I searched `pexflow-production` for Bex, Bexmart, debtor and
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
| `kind` discriminator (`PurchaseRequisition.category`, `TransportTrip.tripType`) | `kind = 'bex_credit'` from day one | Carry it (three-stage rule, point 3) |

---

## 2. Locked spec: acceptance statements

Carl's list is the spec. Each line below is checked by a person doing the work on a phone. Tests support
these lines; they do not replace them.

**Stage 1: the spine. All of A1–A10 must be true before Stage 1 is done.**

- **A1.** Carl or Susan sends an applicant a link by email. The applicant opens it on a phone with no PexFlow login.
- **A2.** The applicant sees the documents checklist and can download the terms, the credit policy and the POPIA notice. These are Bexmart's PDFs.
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

- **`CreditApplication`**: `id`, `number` (CA-0001), `kind` (`bex_credit`), `status`, `company_name`,
  `registration_number`*, `vat_number`*, `trading_address`, `contact_name`, `contact_email`*,
  `contact_phone`*, `requested_limit`, `requested_terms`, `trade_references`* (Json), `consent_at`,
  `consent_version`, `consent_name`, `submitted_at`, `intake_by`, `intake_by_name`, `sent_to_hein_at`,
  `approved_limit`, `approved_terms`, `conditions`, `decision_note`, `decided_by`, `decided_by_name`,
  `decided_at`, `approver_signature_url` (snapshot), `edit_history` (Json), `revision_count`,
  `info_request_note`, `info_requested_at`, `created_at`, `updated_at`.
  *\* Sensitive: added to `SENSITIVE_KEYS` in the same change (rule 18).*
- **`CreditApplicationLink`**: `id`, `application_id`, `token_hash` (unique, SHA-256), `created_by`,
  `created_at`, `expires_at`, `revoked_at`, `last_used_at`.
- **`CreditApplicationDocument`**: `id`, `application_id`, `doc_type`, `pathname` (private store),
  `filename`, `content_type`, `size_bytes`, `sha256`, `uploaded_at`, `removed_at`, `removed_by`. Never a
  public URL.

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

- Consent (version-stamped), the typed name and the tick come before any upload is allowed. The wording is
  Bexmart's (D5).
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
- **Stage 1: spine (A1–A10).** Ships complete. No Stage 2 item gates it.
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
- **Live (stage gate):** Susan and Hein each complete A1–A10 on their own phone against the preview, with a test
  application using the `autotest` prefix or Carl's own address, so no real person is emailed.

---

## 12. Release path

- **Branches:** `feat/2026-10-28-bex-credit-spine` for Stage 1, from the current `origin/main`. Later stages get
  their own branches. Nothing is pushed to `main` (Windows workstream §1).
- **Schema first:** the additive SQL file goes to the builder's Neon dev branch only. Carl runs it on production
  by hand before the code deploys (ENGINEERING_RULES §5, rule 7). New code reads the new columns, so the order
  matters.
- **Gates before every push:** `npm run test:source`, `node scripts/typecheck-budget.mjs`, `npm run build`, then
  `git checkout -- api/_lib/buildInfo.ts`, because the build rewrites that file.
- **CI** runs `guards` and `test` on the PR. Release branches run them too (`.github/workflows/test.yml`).
- **Carl merges on green.** The merge is the release. Nobody else merges.
- **After deploy:** `npm run verify:deploy -- --expect "<a string unique to this change>"`. Then a
  `prove-done` receipt against the deployed preview: `scripts/prove-done.mjs`, spec `specs/bex-credit-spine.json`,
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
- A decision email to the applicant that states the limit (D4).
- Raising a limit above the requested amount (D6).
- OCR of documents.

---

## 14. Risks

1. **The public upload endpoint is the largest new attack surface.** Mitigations are in §6, and the adversarial
   pass in §11 is a go-live condition.
2. **The file-read gap** until `credit/` is private. Hard gate (§6).
3. **POPIA.** ID copies, bank letters and trade references are personal information. Retention and deletion are
   not decided (D10), so nothing is auto-deleted yet. The build stores them privately and never logs them.
   Bexmart needs its own sign-off on the consent wording, the retention period, and who the operator is.
4. **Susan's account.** The last handover records that she has none. That lead time is Carl's to clear, not the
   build's. Until it clears, Susan cannot accept Stage 1.
5. **A forwarded link.** Anyone holding it can use it for 14 days. Mitigation: short expiry, revoke-on-resend,
   and the portal shows only that application, never staff data.
6. **Races** on Submit, Send and Approve, from a double tap or two staff members. Conditional `updateMany` on the
   status, and the count verified (ENGINEERING_RULES §7).
7. **Production DDL is human-run.** A deploy before the SQL runs breaks the new screens. The order is SQL, then code.
8. **This is a live system.** The portal URL sits on the production domain, and test rows are real rows. Live tests
   use the `autotest` prefix or Carl's address.
9. **The brand name.** "Bex" in the request, "Pex" in the repo. Wrong brand text on a public page is embarrassing
   and cannot be unsent. Carl confirms it (D1).
10. **The build machine.** Windows clones fail when they sit in OneDrive, when line endings are wrong, when a push
    goes to `main`, or when `ship-item.mjs` is used (it needs `.vercel/project.json`, which is gitignored, and
    its own error message points at a Mac path). The build script follows the Windows workstream doc and never
    uses `ship-item.mjs`.
11. **Gates not yet recorded.** The baseline counts are not in this plan. Stage 0 records them on the build machine.

---

## 15. Decisions for Carl

Defaults are what I would pick. Reply "go" to accept them, or change any of them.

- **D1. Brand text.** "Bex Credit" (your words), as one constant. Or "Pexmart Credit". **Default: Bex Credit.**
- **D2. Susan.** Susan Kruger, creditors clerk, needs a PexFlow account with `credit_intake`. **Default: yes.**
- **D3. Admin access.** Admin does not get either credit permission implicitly. **Default: explicit grants only.**
- **D4. Telling the applicant.** Susan tells the applicant the outcome by hand. Or the system sends an automatic
  email with no limit in it. **Default: Susan, by hand.**
- **D5. Documents and consent.** Bexmart supplies the consent wording, the checklist, and the three public PDFs
  (terms, credit policy, POPIA notice). **Default: placeholders marked "awaiting Bexmart".**
- **D6. Hein's edit scope.** Stage 1: limit, terms and conditions only. Applicant-supplied fields come in Stage 3.
  Hein cannot raise the limit above the requested amount. **Default: as written.**
- **D7. Link validity.** 14 days. Issuing a new link revokes the old ones. **Default: 14 days.**
- **D8. Uploads.** PDF, JPG and PNG. 10 MB each. No HEIC in Stage 1. **Default: as written.**
- **D9. Virus scanning.** Not in Stage 1. **Default: not in Stage 1.**
- **D10. Retention.** How long applicant documents are kept, and how they are deleted. Bexmart sets it. **Default:
  nothing is deleted automatically until it is set.**

---

## 16. What I could not verify

- **The install and the gates did not run** in the session that wrote this plan. The dependency install was refused
  by the environment's auto-mode classifier, so there are no baseline counts yet. The commands in the build script
  come from `package.json` and `docs/WINDOWS-WORKSTREAM.md`. They are untested on this machine.
- **Current account state** for Susan and Hein. `SAVE.md` is a dated note, not a live check.
- **Whether a generic rate limiter already exists.** `queryGuard.ts` and `EndpointCallStat` are there. Whether either
  fits is not checked.
- **Other private repos** in the account were not opened (see §0, point 5).
