(function () {
  var el = document.getElementById('visit-counter');
  if (!el) return;
  var namespace = 'faithdrivenlife';
  var key = 'visits';
  var url = 'https://abacus.jasoncameron.dev/hit/' + namespace + '/' + key;
  fetch(url)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data && typeof data.value === 'number') {
        el.textContent = data.value.toLocaleString();
      }
    })
    .catch(function () { el.textContent = '—'; });
})();
