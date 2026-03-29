$root = Join-Path $PSScriptRoot '..'
Get-ChildItem -Path $root -Recurse -Filter *.html | Where-Object {
  $_.FullName -notmatch 'mockups' -and $_.Name -notlike 'google*.html'
} | ForEach-Object {
  $c = [System.IO.File]::ReadAllText($_.FullName)
  $o = $c
  $c = $c.Replace('href="favicon.svg"', 'href="/favicon.svg?v=4"')
  $c = $c.Replace('href="../favicon.svg"', 'href="/favicon.svg?v=4"')
  $c = $c.Replace('<link rel="icon" href="logo-official.png"', '<link rel="icon" href="/logo-official.png?v=4"')
  $c = $c.Replace('<link rel="icon" href="../logo-official.png"', '<link rel="icon" href="/logo-official.png?v=4"')
  $c = $c.Replace('<link rel="apple-touch-icon" href="logo-official.png"', '<link rel="apple-touch-icon" href="/logo-official.png?v=4"')
  $c = $c.Replace('<link rel="apple-touch-icon" href="../logo-official.png"', '<link rel="apple-touch-icon" href="/logo-official.png?v=4"')
  if ($c -ne $o) {
    [System.IO.File]::WriteAllText($_.FullName, $c)
    Write-Host "patched: $($_.FullName)"
  }
}
