# gui_fill.ps1 - điền file Excel mẫu "CAD作業納品書" (Gui) cho một đơn hàng bằng Excel (COM, chạy ẩn).
# Dùng: powershell -NoProfile -ExecutionPolicy Bypass -File gui_fill.ps1 -Job <job.json>
# job.json: {"template": "...xls", "out": "...xls", "order": "521106-24", "rows": [{"code": "26-066371", "x": 90.22, "y": 38, "pending": false}, {"code": "26-066372", "x": null, "y": null, "pending": true}, ...]}
# Làm: đổi tên sheet và ô B3 (注番) thành số đơn; ghi từng mã vào hàng 6 trở xuống (B = số thứ tự, C = mã, D = X, E = Y);
#      mã chưa xong ("pending": true): chỉ ghi B và C, trống X/Y và người làm, tô nền xanh lá TOÀN BỘ dòng (cột A đến cột cuối 備考, gồm ô trống);
#      thêm hoặc bớt hàng cho vừa số mã (dòng 合計 và vùng in tự co giãn theo); lưu thành .xls.
param([Parameter(Mandatory = $true)][string]$Job)
$ErrorActionPreference = 'Stop'
$j = Get-Content -Raw -Encoding UTF8 $Job | ConvertFrom-Json
$rows = @($j.rows)
$n = $rows.Count
if ($n -lt 1) { throw 'Không có mã nào để ghi.' }
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$xl.AutomationSecurity = 3     # msoAutomationSecurityForceDisable: không chạy macro nào
try {
    $wb = $xl.Workbooks.Open($j.template, 0, $false)
    $ws = $wb.Worksheets.Item(1)
    # số hàng dữ liệu hiện có trong mẫu: từ hàng 6 đến hàng ngay trên dòng 合計 (cột B)
    $r = 6
    while ($ws.Cells.Item($r, 2).Text -ne '合計' -and $r -lt 400) { $r++ }
    if ($r -ge 400) { throw 'Không thấy dòng 合計 trong file mẫu.' }
    $cur = $r - 6
    $pName = $ws.Cells.Item(6, 16).Text       # 作成担当者 (giữ nguyên người ghi trong mẫu)
    $qName = $ws.Cells.Item(6, 17).Text       # チェック担当者
    # cột cuối của bảng = ô cuối cùng có chữ ở dòng tiêu đề (hàng 4: 備考 chiếm 2 cột R:S); mặc định 19 (S)
    $lastCol = 19
    try { $lc = $ws.Cells.Item(4, $ws.Columns.Count).End(-4159).Column; if ($lc -ge 18 -and $lc -le 30) { $lastCol = $lc } } catch { }
    if ($n -gt $cur) {
        for ($k = 0; $k -lt ($n - $cur); $k++) { [void]$ws.Rows.Item(5 + $cur).Insert() }   # chèn vào trong vùng để công thức 合計 giãn theo
    } elseif ($n -lt $cur) {
        [void]$ws.Range("A$(6 + $n):A$(5 + $cur)").EntireRow.Delete()
    }
    # xoá dữ liệu cũ rồi ghi mới
    [void]$ws.Range("B6:E$(5 + $n)").ClearContents()
    for ($i = 0; $i -lt $n; $i++) {
        $row = 6 + $i
        $pending = [bool]$rows[$i].pending
        $ws.Cells.Item($row, 2).Value2 = [double]($i + 1)
        $ws.Cells.Item($row, 3).Value2 = [string]$rows[$i].code
        if ($pending) {
            # mã chưa xong: chỉ số thứ tự + mã, để trống kích thước và tên người làm, tô xanh lá toàn bộ dòng (cột A đến cột cuối 備考)
            [void]$ws.Range($ws.Cells.Item($row, 16), $ws.Cells.Item($row, 17)).ClearContents()      # mẫu có thể đã ghi sẵn tên người làm
            $ws.Range($ws.Cells.Item($row, 1), $ws.Cells.Item($row, $lastCol)).Interior.Color = 5296274    # RGB(146,208,80), cột A (送信No.) đến cột cuối 備考 (kể cả ô trống)
        } else {
            if ($null -ne $rows[$i].x) { $ws.Cells.Item($row, 4).Value2 = [double]$rows[$i].x }
            if ($null -ne $rows[$i].y) { $ws.Cells.Item($row, 5).Value2 = [double]$rows[$i].y }
            $ws.Cells.Item($row, 16).Value2 = $pName
            $ws.Cells.Item($row, 17).Value2 = $qName
        }
    }
    $ws.Cells.Item(3, 2).Value2 = [string]$j.order        # 注番
    $ws.Name = [string]$j.order
    $out = [string]$j.out
    if (Test-Path $out) { Remove-Item -Force $out }
    $wb.SaveAs($out, 56)                                   # 56 = xlExcel8 (.xls)
    $wb.Close($false)
    Write-Output ("OK rows=$n total_row=" + (6 + $n))
} finally {
    $xl.Quit()
    [void][System.Runtime.Interopservices.Marshal]::ReleaseComObject($xl)
}
