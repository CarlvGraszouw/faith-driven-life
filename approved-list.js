(function () {
  var url = window.APPROVED_SHEET_CSV_URL;
  var type = document.body && document.body.getAttribute('data-approved-type');
  var listEl = document.querySelector('.approved-list');
  if (!url || !type || !listEl || url.indexOf('YOUR_SHEET_ID') !== -1) return;

  var CORS_PROXY = 'https://corsproxy.io/?';
  var fetchUrl = CORS_PROXY + encodeURIComponent(url);

  fetch(fetchUrl)
    .then(function (r) { return r.text(); })
    .then(function (text) {
      var rows = parseCSV(text);
      if (!rows.length) return;
      var header = rows[0].map(function (c) { return (c || '').toLowerCase().trim(); });
      var typeCol = -1;
      var nameCol = -1;
      var dateCol = -1;
      var messageCol = -1;
      for (var i = 0; i < header.length; i++) {
        var h = header[i];
        if (h === 'type') typeCol = i;
        else if (h === 'name') nameCol = i;
        else if (h === 'date') dateCol = i;
        else if (h === 'message') messageCol = i;
      }
      if (typeCol === -1) typeCol = 0;
      if (nameCol === -1) nameCol = 1;
      if (dateCol === -1) dateCol = 2;
      if (messageCol === -1) messageCol = 3;

      var want = type.replace(/-/g, '').toLowerCase();
      if (want === 'comments') want = 'comment';
      if (want === 'prayerrequests') want = 'prayer';
      if (want === 'testimonies') want = 'testimony';

      var html = '';
      for (var j = 1; j < rows.length; j++) {
        var row = rows[j];
        var rowType = (row[typeCol] || '').toLowerCase().trim();
        if (rowType !== want) continue;
        var name = escapeHtml((row[nameCol] || '').trim());
        var date = escapeHtml((row[dateCol] || '').trim());
        var message = escapeHtml((row[messageCol] || '').trim());
        if (!name && !message) continue;
        html += '<div class="approved-item"><strong>' + name + '</strong>';
        if (date) html += ' <span class="approved-meta">— ' + date + '</span>';
        html += '<p>' + message + '</p></div>';
      }
      if (html) listEl.innerHTML = html;
    })
    .catch(function () {});

  function parseCSV(t) {
    var rows = [];
    var row = [];
    var cell = '';
    var inQuotes = false;
    for (var i = 0; i < t.length; i++) {
      var ch = t[i];
      if (inQuotes) {
        if (ch === '"') inQuotes = false;
        else cell += ch;
      } else {
        if (ch === '"') inQuotes = true;
        else if (ch === ',' || ch === '\t') { row.push(cell); cell = ''; }
        else if (ch === '\n' || ch === '\r') {
          if (ch === '\r' && t[i + 1] === '\n') i++;
          row.push(cell);
          rows.push(row);
          row = [];
          cell = '';
        } else cell += ch;
      }
    }
    if (cell || row.length) { row.push(cell); rows.push(row); }
    return rows;
  }
  function escapeHtml(s) {
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML.replace(/\n/g, '<br>');
  }
})();
