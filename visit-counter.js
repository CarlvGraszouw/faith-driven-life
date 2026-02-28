(function () {
  var el = document.getElementById('visit-counter');
  if (!el) return;
  var key = 'faithdrivenlife';
  var name = 'visits';
  fetch('https://api.countapi.xyz/hit/' + key + '/' + name)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data && typeof data.value === 'number') {
        el.textContent = data.value.toLocaleString();
      }
    })
    .catch(function () { el.textContent = '—'; });
})();
