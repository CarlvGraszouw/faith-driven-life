$root = Join-Path $PSScriptRoot '..'
$old = @'
  <link rel="icon" href="/logo-official.png?v=4" type="image/png" sizes="48x48">
  <link rel="icon" href="/favicon.svg?v=4" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/logo-official.png?v=4" sizes="180x180">
'@
$new = @'
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg?v=4" type="image/svg+xml" sizes="any">
  <link rel="icon" href="/logo-official.png?v=4" type="image/png" sizes="48x48">
  <link rel="apple-touch-icon" href="/logo-official.png?v=4" sizes="180x180">
'@
Get-ChildItem -Path $root -Recurse -Filter *.html | Where-Object {
  $_.FullName -notmatch 'mockups' -and $_.Name -notlike 'google*.html'
} | ForEach-Object {
  $c = [System.IO.File]::ReadAllText($_.FullName)
  if ($c -notmatch 'favicon\.ico') {
    if ($c.Contains($old)) {
      $c2 = $c.Replace($old, $new)
      [System.IO.File]::WriteAllText($_.FullName, $c2)
      Write-Host "inserted ico: $($_.FullName)"
    }
  }
}
