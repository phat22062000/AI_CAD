# Tu dong day TOAN BO folder AI_CAD len https://github.com/phat22062000/AI_CAD (Task Scheduler 16:55, T2-T7)
# Dang nhap git qua Git Credential Manager (khong luu token trong script). Log: tools\auto_push\day_ai_cad.log
param([switch]$DryRun)
$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$log  = Join-Path $PSScriptRoot 'day_ai_cad.log'
function Log($m){ $l = '{0:yyyy-MM-dd HH:mm:ss}  {1}' -f (Get-Date),$m; Add-Content -LiteralPath $log -Value $l -Encoding UTF8; Write-Host $l }
$env:GIT_TERMINAL_PROMPT = '0'
Set-Location -LiteralPath $repo
Log "Bat dau ($repo)"
$remote = (git remote get-url origin 2>&1)
if($remote -notmatch 'phat22062000/AI_CAD'){ Log "DUNG: remote origin khong dung repo AI_CAD: $remote"; exit 1 }
git add -A 2>&1 | ForEach-Object { Log "$_" }
# Chot an toan: GitHub tu choi file >100MB
$big = @(git -c core.quotepath=false diff --cached --name-only | Where-Object { $_ -and (Test-Path -LiteralPath $_) -and ((Get-Item -LiteralPath $_).Length -gt 95MB) })
if($big.Count -gt 0){ git reset -q; Log ('DUNG: file >95MB: ' + ($big -join ', ')); exit 1 }
$staged = @(git diff --cached --name-only)
if($staged.Count -eq 0){ Log 'Khong co thay doi, bo qua commit.' }
else{
  Log ("So file thay doi: {0}" -f $staged.Count)
  if($DryRun){ git reset -q; Log 'DryRun: khong commit.'; exit 0 }
  git -c user.name=ADMIN -c user.email=phat22062000@gmail.com commit -q -m ('Cap nhat tu dong {0:yyyy-MM-dd HH:mm}' -f (Get-Date)) 2>&1 | ForEach-Object { Log "$_" }
}
# Push ke ca khi khong co thay doi moi (day not commit con ton)
$out = git push origin main 2>&1
$code = $LASTEXITCODE
$out | ForEach-Object { Log "$_" }
if($code -ne 0){ Log 'LOI push (xem log).'; exit 1 }
Log 'Day len GitHub thanh cong.'
