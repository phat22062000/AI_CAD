# Tu dong day tai lieu/quy tac/skill len GitHub (chay boi Task Scheduler luc 16:45, T2-T7)
# Chi day file khong bi .gitignore chan (khong DXF/PDF/DWG/don hang). Log: tools\auto_push\auto_push.log
param([switch]$DryRun)
$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$log  = Join-Path $PSScriptRoot 'auto_push.log'
function Log($m){ $l = '{0:yyyy-MM-dd HH:mm:ss}  {1}' -f (Get-Date),$m; Add-Content -LiteralPath $log -Value $l -Encoding UTF8; Write-Host $l }
Set-Location -LiteralPath $repo
Log "Bat dau ($repo)"
git add -A 2>&1 | Out-Null
$staged = @(git diff --cached --name-only)
if($staged.Count -eq 0){ Log 'Khong co thay doi, bo qua.'; exit 0 }
# Chot an toan: khong cho day file du lieu khach
$bad = @($staged | Where-Object { $_ -match '\.(pdf|dwg|nc)$' -or ($_ -match '\.dxf$' -and $_ -ne 'templates/Template.dxf') -or $_ -match '(^|/)(Thang-\d+|AI_Work)/' })
if($bad.Count -gt 0){ git reset -q; Log ('DUNG: co file bi chan: ' + ($bad -join ', ')); exit 1 }
Log ('File thay doi: ' + ($staged -join '; '))
if($DryRun){ git reset -q; Log 'DryRun: khong commit.'; exit 0 }
git commit -q -m ('Cap nhat tu dong {0:yyyy-MM-dd HH:mm}' -f (Get-Date)) 2>&1 | ForEach-Object { Log $_ }
$out = git push origin main 2>&1
$out | ForEach-Object { Log "$_" }
if($LASTEXITCODE -ne 0){ Log 'LOI push (xem log).'; exit 1 }
Log 'Day len GitHub thanh cong.'
