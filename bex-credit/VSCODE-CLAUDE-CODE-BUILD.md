# Bex Credit: VS Code and Claude Code build script

**For:** one builder, on one Windows PC, in one clone. That is the rule in `docs/WINDOWS-WORKSTREAM.md` §1:
one session, one clone, never `main`, and Carl merges.

**Before you start:** read `PLAN.md` in this folder. Copy it into the clone as `SPEC-bex-credit.md`.
That copy is the locked spec. Changing it stops the build and restarts the item (ORCHESTRATION-RULES §4).

**How to read this script**

- **Run** blocks are PowerShell, typed in the VS Code terminal.
- **PASTE** blocks go into the Claude Code panel, word for word.
- **STOP** means do not continue until the condition is true.
- **Receipt** means paste that output into the PR. A step with no receipt is not done (ORCHESTRATION-RULES §7).

---

## Part A. The machine (once)

**A1. Not OneDrive.** Your clone must not sit under OneDrive.

```powershell
New-Item -ItemType Directory -Force C:\dev | Out-Null
cd C:\dev
```

**A2. Git settings, before cloning.**

```powershell
git config --global core.autocrlf false
git config --global core.longpaths true
git config --global user.name  "<your name>"
git config --global user.email "<your email>"
```

**A3. VS Code.** Settings → `files.eol` → `\n`. Install the Claude Code extension. Sign in.

**A4. Clone and Node 24.**

```powershell
gh repo clone CarlvGraszouw/pexflow-production pexflow
cd C:\dev\pexflow
git ls-files --eol | Select-String 'w/crlf'     # only .ps1 files should print
fnm install
fnm use
node -v                                          # STOP unless it prints v24.x
npm ci
```

**A5. `.env`.** Create `C:\dev\pexflow\.env` (gitignored). Copy values from the password manager only.

- `DATABASE_URL` and `DATABASE_URL_UNPOOLED`: **your own Neon dev branch**, which Carl creates for this PC.
  Never production. Never the shared `testing` branch.
- `TEST_DATABASE_URL`: **leave it out.**
- `JWT_SECRET`, `CRON_SECRET`: your own dev values.
  `node -e "console.log(require('crypto').randomBytes(48).toString('base64url'))"`
- `BLOB_PRIVATE_RW_TOKEN`: leave empty unless Carl gives a dev value. Uploads then refuse on your PC. That is
  correct. Upload is proven on the preview, not on your PC.

**Do not run** `vercel env pull`, `npx vercel`, or `scripts/ship-item.mjs` on Windows.

**STOP** until `node -v` prints `v24.x` and `npm ci` exits 0.

---

## Part B. Baseline (before any code)

```powershell
git fetch origin
git switch -c feat/2026-10-28-bex-credit-spine origin/main
git log -1 --oneline                            # this is the base commit; paste it
npm run test:source        *> receipts\2026-10-28-baseline-test.txt
node scripts/typecheck-budget.mjs *> receipts\2026-10-28-baseline-typecheck.txt
npm run lint *> receipts\2026-10-28-baseline-lint.txt
npm run build
git checkout -- api/_lib/buildInfo.ts
```

Create `receipts\` first if it is missing. It is gitignored.

**STOP** if any command fails. Fix it, or tell Carl what is failing. Do not start Part D with a red baseline.

**Receipt:** the three baseline files, plus the base commit line.

---

## Part C. Carl's decisions (STOP until answered)

Send Carl `PLAN.md` §15, D1–D10, with the defaults. Carl's answers go into `SPEC-bex-credit.md` §15, and
**you write them there**. The agent does not. Once they are written, the spec is locked.

**STOP** until Carl has answered D1–D10 in writing.

---

## Part D. Claude Code session

Open the `C:\dev\pexflow` folder in VS Code. Open a new Claude Code session in it.

### D-1. Standing brief. PASTE first, every session

```
You are Watchdog for this session. Read .claude/agents/watchdog.md and .claude/ownership.md first.
Then read CLAUDE.md, ENGINEERING_RULES.md, BUILD-PROTOCOL.md,
docs/standards/THREE-STAGE-BUILD-AND-SAFETY-NETS.md and docs/WINDOWS-WORKSTREAM.md.

The spec is SPEC-bex-credit.md. It is LOCKED. Do not change it. If it seems wrong, stop and tell me.

Branch: feat/2026-10-28-bex-credit-spine, from origin/main. Never push to main. Never merge.

Hard rules for this session:
- Never run `npm test`, `npx vitest run`, or the DB suite. Use `npm run test:source` only.
- Never run `prisma db push`, `npx vercel`, `vercel --prod`, or `git stash`.
- Never run a SQL file against production. Apply to the builder's dev branch only.
- Write the failing test first for every behaviour (ENGINEERING_RULES §1).
- Credit models are NOT added to api/_lib/models.ts. There is no generic route for them.
- Every sender checks for the `autotest` prefix first (rule 6).
- Personal fields go into SENSITIVE_KEYS in the same change (rule 18).
- Private store only for credit files. Never the public store.
- Report the base commit in your first message.

Carl's words, for every commit message, verbatim, dated:
Carl, 28 Oct 2026: "We need to build a Bex credit section for all our debtors, where people will be able
to apply for credit with Bexmart."
Carl, 28 Oct 2026: "…Hein is not approving purchase requisitions, but he will be approving credit
applications that has been applied for…"

Stop at every STOP line in the build script and wait for me.
```

### D-2. Register the area. PASTE

```
Before you appoint any agent, write the ownership row for area `credit` in .claude/ownership.md,
following the existing rows exactly. Shared files are one owner each at a time:
prisma/schema.prisma, api/functions/[name].ts, api/_lib/auth.ts, api/_lib/permissionLabels.ts,
api/file.ts, api/_lib/fileAccess.ts, api/_lib/sentry.ts, src/App.jsx, src/components/layout/Sidebar.jsx,
vercel.json, public/sw.js. Show me the row. Do not appoint yet.
```

---

## Part E. Stage 1: the spine (A1–A10)

Each step ends at a STOP. Each STOP is a gate, not a suggestion.

### S1-1. Schema (DB agent). PASTE

```
You are the DB agent for this step only. Write scripts/2026-10-28_credit_applications.sql:
- three tables from PLAN.md §4: CreditApplication, CreditApplicationLink, CreditApplicationDocument;
- additive only: CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS, nothing dropped or renamed;
- safe to run twice;
- a sequence for CA-#### numbers, matching the NUMBER_FIELD pattern used for CC- client collections.
Add the matching Prisma models to prisma/schema.prisma with the same comment the on-hold columns carry:
created outside Prisma, declared so `prisma db push` never drops them.
Apply to MY dev branch only:
  node --env-file=.env scripts/apply-sql-file.mjs scripts/2026-10-28_credit_applications.sql
Then run it again, to prove it is safe twice. Then run `npm run test:source`.
Do not touch production. Carl runs production SQL himself.
```

**STOP** until the SQL applies twice on the dev branch and `npm run test:source` is still green.
**Receipt:** the two apply outputs.

### S1-2. Red tests first. PASTE

```
Write the failing tests before any implementation. One file per concern, under tests/, named for the
behaviour. At minimum:
- credit-state-machine: every transition in PLAN.md §3, and every refused one.
- credit-limit: approved limit must be > 0 and <= requested limit; a raise is refused with the reason in words.
- credit-link-token: a token is 32 random bytes; only its SHA-256 is stored; an expired, revoked or
  unknown token is refused; issuing a new link revokes the old ones.
- credit-upload-rules: PDF/JPEG/PNG only; 10 MB cap; magic bytes must match; pathname is server-made
  as credit/<number>/<doc_type>/<uuid>.<ext>; refused if the private credential is missing (no fallback).
- credit-required-docs: send-to-Hein refused until every required document is present, naming the missing ones.
- credit-file-read: credit/ opens only for credit_intake or credit_approval holders with an existing application.
- credit-notify-gating: autotest prefix is a no-op; per-recipient rate limit; retries stop at 3; no infinite retry.
- credit-double-submit: a second submit or decide on the same status does nothing and says so.
- credit-scrubber: the new sensitive keys are redacted at any depth.
Run `npm run test:source`. Paste the output.
Each failing test must fail for the NAMED reason, not a typo or a missing import.
If a test fails for the wrong reason, fix the test first.
```

**STOP** until every new test is red for the stated reason.
**Receipt:** the red output, with the failure reason for each test.

### S1-3. Server. PASTE

```
Make the red tests green, one file at a time, in this order:
1. src/lib/credit/: statuses, required document types, limits, upload allowlist. No Prisma import here.
2. Token module: generate, hash, verify, expire, revoke.
3. State machine and the functions in PLAN.md §7. Each conditional on status, using updateMany
   with the condition in `where`, and the affected count verified (ENGINEERING_RULES §7).
   Each write hard-codes its field set. No spreading of request bodies.
4. api/credit-portal/[name].ts: one public dispatcher. Cookie exchange, the portal endpoints.
5. api/file.ts and api/_lib/fileAccess.ts: add credit/ to PRIVATE_FILE_AREAS and decideCreditFileRead.
   Extend tests/file-privacy-paths-s3.test.ts.
6. api/_lib/sentry.ts: SENSITIVE_KEYS gains the new personal keys, in this same change.
7. api/_lib/creditNotifications.ts: the sender rules from PLAN.md §9.
8. AUTHENTICATED_FUNCTIONS: the staff functions from PLAN.md §7.
After each file, run `npm run test:source` and show me the count.
Do not add the credit models to api/_lib/models.ts.
Do not add a new top-level file under api/ for any single endpoint.
```

**STOP** until `npm run test:source` is green on every new test and the count has only gone up.

### S1-4. Applicant portal (phone first). PASTE

```
Build the applicant portal, phone first, per PLAN.md §8.
- Route under /credit/apply, outside ProtectedRoute and AuthLayout. No PexFlow navigation. No login UI.
- Steps: consent and details → documents checklist with the public PDFs → uploads → review and submit →
  confirmation with the application number.
- Every disabled control shows its reason as visible text, with data-touch-reason="visible".
- No horizontal scroll at 360px. 16px side gutter.
- No third-party scripts. Referrer-Policy no-referrer, X-Robots-Tag noindex, Cache-Control no-store
  on the portal route and on /api/credit-portal/*.
- Public PDFs go under public/credit/, as placeholders marked "awaiting Bexmart" (D5).
Run `npm run test:source`, then `npm run typecheck:budget` (or node scripts/typecheck-budget.mjs).
Show me the touch-reachable-reasons result.
```

**STOP** until the touch and reachability guards are green. The phone check happens in S1-12.

### S1-5. Staff screens. PASTE

```
Build the staff screens, per PLAN.md §8.
- Nav entry "Credit applications", visible to either credit permission. Add it to Sidebar.jsx.
- Route behind PermissionGate in App.jsx.
- Queue: status colours from src/lib/credit/creditStatus.js only. Never a second copy.
- Detail: applicant details, documents via /api/file, missing-items checklist, history, decision panel.
- Hein's panel (credit_approval only): Approve, Reject, Edit terms, Return to Susan. The limit rule
  shown in words. Every disabled button says why, as visible text.
- After any action, scroll the result into view (scrollIntoView, bound to the panel's own ref).
Then show me: tests/landing-never-access-denied.test.ts, tests/control-reachability.test.ts and
tests/touch-reachable-reasons.test.ts, all green.
```

**STOP** until all three guards are green.

### S1-6. Adversarial pass. PASTE

```
Write one test per attack and make each one refused, with a reason, and no data leaked:
- wrong, expired, revoked and unknown tokens
- a valid token for application A used to read application B
- an oversized file, a file with a PDF name and an executable's bytes, a file with no extension
- an upload callback replayed after the application was submitted
- submit twice in the same instant (double tap)
- Hein approving a limit above requested
- Susan trying decideCreditApplication (she lacks credit_approval)
- a staff member without credit_intake opening a credit/ document by pasting its path
- a PATCH to a credit field through the generic route
- a notification to an autotest recipient
Run `npm run test:source`. Paste the list of attacks and each one's result.
```

**STOP** until every attack is refused by a test.

### S1-7. Gates. PASTE, then run

```
Run the full local gate set and paste the output of each:
1. npm run test:source
2. node scripts/typecheck-budget.mjs
3. npm run lint
4. npm run build
Then: git checkout -- api/_lib/buildInfo.ts
Compare typecheck and lint counts with the baseline in receipts/. An increase is a failure.
Any new error in a file you touched is a failure, fixed here and not waived.
```

**STOP** until all four gates pass and the counts have not increased.
**Receipt:** the four outputs, and the before and after counts.

### S1-8. Push and open the PR

```
git add the files for this step only, then commit with a message that quotes Carl's words, verbatim and dated,
the way the existing commits do. Do not add any model name to the commit message.
git push -u origin feat/2026-10-28-bex-credit-spine
Open the PR with gh pr create. If .github/pull_request_template.md exists, fill its headings from this change.
Check `gh run list --limit 10` first. Do not push while a run is queued.
```

**STOP** until the PR exists and CI has started.

### S1-9. CI

Wait for the checks on the PR. Do not push to make CI run again (rule 15). If a check is red, the fix is
a new commit on the same branch, with a test that fails first.

**STOP** until the `guards` and `test` checks are green on the PR head.
**Receipt:** the PR link and the green check list.

### S1-10. Carl's steps (you cannot do these)

1. Review and merge the PR to a `release/2026-10-28` branch on Carl's schedule. Only Carl merges.
2. Run `scripts/2026-10-28_credit_applications.sql` on production by hand, **before** the code deploys.
3. Grant `credit_intake` to Susan and `credit_approval` to Hein in User Management.
4. Confirm the brand text (D1), then approve the release.
5. After the deploy, run:
   `npm run verify:deploy -- --expect "<a string unique to this change, such as the consent version>"`

**STOP** until Carl has done 1–4.

### S1-11. Live check, as the real people

Susan and Hein, each on their own phone, against the preview, with a test application that uses the `autotest`
prefix or Carl's own address. Each acceptance line A1–A10 is ticked by the person who did it, with a date.
Susan does A1–A5 and A7. Hein does A6, A8 and A9. Either of them may do A10.

The spec file `specs/bex-credit-spine.json` is written in this step. It asserts the things in A1–A10 that can
be read from the served bundle and the API.

**Carl runs the receipt, not you.** `prove-done` signs a token for a real admin, looked up in the database the
preview uses. Your dev `.env` must not hold that. Carl runs this from his own machine, against the bundle the
deploy built (the name `verify:deploy` printed):

```
node --env-file=.env scripts/prove-done.mjs <preview-url> specs/bex-credit-spine.json --expect-bundle <assets/index-XXXX.js>
```

**STOP.** Stage 1 is **not done** until all of A1–A10 are ticked and the prove-done receipt is GREEN.
Rule 14: done means Carl can use it, with the receipt pasted beneath the word.

---

## Part F. Stage 2: instrumentation

Its own branch: `feat/2026-10-28-bex-credit-instrumentation`, from the merged `main`. Same rules, same gates.
Build in this order, a red test before each item:

1. The audit timeline per application.
2. The decision letter (PDF) with Hein's signature from the saved image.
3. `credit-application-watch` cron, wrapped in `withCronErrorReporting`, with the self-audit from PLAN.md §9.
4. The alarm when nobody holds `credit_approval` or `credit_intake`.
5. The endpoint refusal monitor for `/api/credit-portal/*`.
6. Search and filters on the queue.
7. The turnaround report.

**STOP** after each item for its gates, and at the end for a human acceptance pass by Susan and Hein.

---

## Part G. Stage 3: extension

Its own branch: `feat/2026-10-28-bex-credit-extension`. Same rules.

1. Applicant-supplied fields editable by Hein, with a reason and a snapshot.
2. Re-application linked to the earlier application.
3. A second applicant `kind`, set through configuration. Not a copied module. Add the registry test first
   (three-stage doc, Part 5).
4. Document-expiry reminders.

**STOP** at the end for a human acceptance pass.

---

## Part H. If something breaks on Windows

| Symptom | Cause and fix |
|---|---|
| `npm ci` fails at `postinstall` (`prisma generate`) | Network or proxy. Retry. Do not delete the lockfile. |
| `test:source` cannot find the generated client | Run `npm ci` again. Check that `src\generated` exists. |
| Git shows every line changed | CRLF. Run `git ls-files --eol` and fix the file. Never commit CRLF into LF files. |
| The clone is slow or files are locked | You are in OneDrive. Move the clone to `C:\dev`. |
| `git push` rejected | Never force-push to `main`. On your own branch: `git fetch origin`, then `git rebase origin/main`, then `git push --force-with-lease`. |
| `buildInfo.ts` shows as modified after a build | The build rewrites it. `git checkout -- api/_lib/buildInfo.ts`. |
| Anything asks for `.vercel/project.json` | You ran a Vercel or ship-item command. Do not. The PR's Vercel check is the preview. |
| A check is red and the cause is not your change | Say so on the PR, with the failing check named. Do not skip, disable or quarantine a test. |

---

## Part I. Commit message template

```
feat(credit): <what this commit does>

Carl, 28 Oct 2026: "We need to build a Bex credit section for all our debtors, where people will be able
to apply for credit with Bexmart."

Acceptance: <A-numbers this commit moves>
```

---

## Part J. Receipts to paste into the PR, at the end

- Baseline: test count, typecheck count, lint count, base commit
- The four local gates after the change, with counts before and after
- The CI check list, green, on the PR head
- The red-test output from S1-2
- The adversarial pass results from S1-6
- The acceptance tick list, A1–A10, with each person's name and date
- The prove-done receipt, GREEN
