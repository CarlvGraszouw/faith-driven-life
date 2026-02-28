/**
 * Automated Approve/Reject for Formspree submissions.
 * Deploy as Web App (Execute as me, Anyone can access).
 * Use the /dev or /exec URL as Formspree webhook and for approve/reject links.
 */

// ============ CONFIG — Edit these ============
var CONFIG = {
  SPREADSHEET_ID: 'YOUR_SPREADSHEET_ID',   // From sheet URL: docs.google.com/spreadsheets/d/THIS_PART/edit
  OWNER_EMAIL: 'vongraszouw@gmail.com',    // Where to send Approve/Reject emails
  APPROVED_SHEET_NAME: 'Sheet1',           // Tab name with Type, Name, Date, Message (published as CSV)
  PENDING_SHEET_NAME: 'Pending',          // Tab for pending submissions (create this)
  WEB_APP_URL: 'YOUR_WEB_APP_URL'         // Set after first deploy: Deploy > Web app > copy URL (no /dev)
};
// =============================================

function doPost(e) {
  try {
    var data = e.postData && e.postData.contents ? JSON.parse(e.postData.contents) : {};
    var name = data.name || data['Your name'] || '';
    var email = data.email || data['Your email (not published)'] || '';
    var message = data.message || data.Comment || data['Prayer request'] || data['Your testimony'] || '';
    var subject = data._subject || data.subject || '';

    var type = 'comment';
    if (/prayer/i.test(subject)) type = 'prayer';
    else if (/testimony|testimonies/i.test(subject)) type = 'testimony';

    var id = Utilities.getUuid();
    var dateStr = formatDate(new Date());

    var ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
    var pending = ss.getSheetByName(CONFIG.PENDING_SHEET_NAME);
    if (!pending) {
      pending = ss.insertSheet(CONFIG.PENDING_SHEET_NAME);
      pending.appendRow(['Id', 'Type', 'Name', 'Date', 'Message', 'Email']);
    }
    pending.appendRow([id, type, name, dateStr, message, email]);

    var baseUrl = CONFIG.WEB_APP_URL || getWebAppUrl();
    var approveUrl = baseUrl + '?action=approve&id=' + encodeURIComponent(id);
    var rejectUrl = baseUrl + '?action=reject&id=' + encodeURIComponent(id);

    var htmlBody = '<p>New submission from <strong>' + escapeHtml(name) + '</strong> (' + escapeHtml(email) + ')</p>' +
      '<p><strong>Type:</strong> ' + type + '</p>' +
      '<p><strong>Message:</strong></p><p>' + escapeHtml(message) + '</p>' +
      '<p>Choose:</p>' +
      '<p><a href="' + approveUrl + '" style="display:inline-block;padding:10px 20px;background:#0a0;color:#fff;text-decoration:none;border-radius:6px;margin-right:10px;">Approve – show on site</a> ' +
      '<a href="' + rejectUrl + '" style="display:inline-block;padding:10px 20px;background:#c00;color:#fff;text-decoration:none;border-radius:6px;">Reject</a></p>' +
      '<p><small>If buttons don\'t work, copy these links:<br>Approve: ' + approveUrl + '<br>Reject: ' + rejectUrl + '</small></p>';

    GmailApp.sendEmail(CONFIG.OWNER_EMAIL, '[A Faith Driven Life] New submission – Approve or Reject', 'Please open in an HTML-capable email client.', { htmlBody: htmlBody });

    return ContentService.createTextOutput(JSON.stringify({ ok: true, id: id })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: err.toString() })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  var action = (e && e.parameter && e.parameter.action) || '';
  var id = (e && e.parameter && e.parameter.id) || '';
  var result = '';

  if (action === 'approve' && id) {
    result = handleApprove(id);
  } else if (action === 'reject' && id) {
    result = handleReject(id);
  } else {
    result = '<!DOCTYPE html><html><body><p>Use Approve or Reject links from your email.</p></body></html>';
  }

  return HtmlService.createHtmlOutput(result).setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function handleApprove(id) {
  try {
    var ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
    var pending = ss.getSheetByName(CONFIG.PENDING_SHEET_NAME);
    var approved = ss.getSheetByName(CONFIG.APPROVED_SHEET_NAME);
    if (!pending || !approved) return errorHtml('Sheet not found. Check APPROVED_SHEET_NAME and PENDING_SHEET_NAME.');

    var data = pending.getDataRange().getValues();
    var header = data[0];
    var idCol = header.indexOf('Id');
    if (idCol === -1) idCol = 0;
    var typeCol = header.indexOf('Type'); if (typeCol === -1) typeCol = 1;
    var nameCol = header.indexOf('Name'); if (nameCol === -1) nameCol = 2;
    var dateCol = header.indexOf('Date'); if (dateCol === -1) dateCol = 3;
    var messageCol = header.indexOf('Message'); if (messageCol === -1) messageCol = 4;

    var rowIndex = -1;
    for (var i = 1; i < data.length; i++) {
      if (String(data[i][idCol]) === id) { rowIndex = i; break; }
    }
    if (rowIndex === -1) return errorHtml('Submission not found or already processed.');

    var row = data[rowIndex];
    approved.appendRow([row[typeCol], row[nameCol], row[dateCol], row[messageCol]]);
    pending.deleteRow(rowIndex + 1);

    return '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="font-family:sans-serif;max-width:480px;margin:3rem auto;padding:1.5rem;text-align:center;"><h1 style="color:#0a0;">Approved</h1><p>This submission will appear on your site. Refresh the Comments, Prayer requests, or Testimonies page to see it.</p><p><a href="https://carlvgraszouw.github.io/faith-driven-life/">Back to site</a></p></body></html>';
  } catch (err) {
    return errorHtml(err.toString());
  }
}

function handleReject(id) {
  try {
    var ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
    var pending = ss.getSheetByName(CONFIG.PENDING_SHEET_NAME);
    if (!pending) return errorHtml('Pending sheet not found.');

    var data = pending.getDataRange().getValues();
    var idCol = 0;
    for (var i = 0; i < data[0].length; i++) { if (String(data[0][i]).toLowerCase() === 'id') { idCol = i; break; } }
    for (var j = 1; j < data.length; j++) {
      if (String(data[j][idCol]) === id) {
        pending.deleteRow(j + 1);
        return '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="font-family:sans-serif;max-width:480px;margin:3rem auto;padding:1.5rem;text-align:center;"><h1 style="color:#666;">Rejected</h1><p>This submission will not appear on the site.</p><p><a href="https://carlvgraszouw.github.io/faith-driven-life/">Back to site</a></p></body></html>';
      }
    }
    return errorHtml('Submission not found or already processed.');
  } catch (err) {
    return errorHtml(err.toString());
  }
}

function formatDate(d) {
  var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function errorHtml(msg) {
  return '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="font-family:sans-serif;margin:2rem;"><h1 style="color:#c00;">Error</h1><p>' + escapeHtml(msg) + '</p></body></html>';
}

function getWebAppUrl() {
  try {
    return ScriptApp.getService().getUrl().replace(/\/dev$/, '');
  } catch (e) {
    return '';
  }
}
