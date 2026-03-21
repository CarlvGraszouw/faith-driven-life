# Upload the large Supreme Commission MP3 to Cloudflare R2 (requires Wrangler login).
# Usage:
#   .\scripts\upload-audio-to-r2.ps1 -BucketName "faith-driven-life-audio"
# Optional: -LocalPath to a different file

param(
    [Parameter(Mandatory = $true)]
    [string] $BucketName,
    [string] $ObjectKey = "audio/the-supreme-commission.mp3",
    [string] $LocalPath = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path $PSScriptRoot -Parent
if (-not $LocalPath) {
    $LocalPath = Join-Path (Join-Path $repoRoot "audio") "The Supreme Commission.mp3"
}

if (-not (Test-Path -LiteralPath $LocalPath)) {
    Write-Error "File not found: $LocalPath"
}

$r2Path = "${BucketName}/${ObjectKey}"
Write-Host "Uploading to R2: $r2Path"
Write-Host "Public URL will be: {your Public Bucket URL from R2 bucket settings}/$ObjectKey"

& npx wrangler@4 r2 object put $r2Path --file="$LocalPath" --content-type="audio/mpeg" --remote
