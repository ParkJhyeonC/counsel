param(
  [Parameter(Mandatory=$true)][string]$RootDir,
  [Parameter(Mandatory=$true)][string]$PythonExe
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = $PythonExe
$startInfo.Arguments = '-c "from app import app, init_db; init_db(); app.run(host=\"0.0.0.0\", port=5000, debug=False, use_reloader=False)"'
$startInfo.WorkingDirectory = $RootDir
$startInfo.CreateNoWindow = $true
$startInfo.UseShellExecute = $false
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true

$serverProcess = New-Object System.Diagnostics.Process
$serverProcess.StartInfo = $startInfo
$null = $serverProcess.Start()

$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$notifyIcon.Visible = $true
$notifyIcon.Text = '카운슬로그 서버 실행 중'
$notifyIcon.BalloonTipTitle = '카운슬로그'
$notifyIcon.BalloonTipText = '트레이에서 실행 중입니다. 우클릭으로 열기/종료가 가능합니다.'
$notifyIcon.ShowBalloonTip(4000)

$contextMenu = New-Object System.Windows.Forms.ContextMenuStrip
$openItem = $contextMenu.Items.Add('브라우저 열기')
$openItem.Add_Click({ Start-Process 'http://localhost:5000' }) | Out-Null
$exitItem = $contextMenu.Items.Add('종료')
$exitItem.Add_Click({
    if (-not $serverProcess.HasExited) {
      $serverProcess.Kill()
      $serverProcess.WaitForExit(2000) | Out-Null
    }
    $notifyIcon.Visible = $false
    [System.Windows.Forms.Application]::Exit()
}) | Out-Null

$notifyIcon.ContextMenuStrip = $contextMenu
$notifyIcon.Add_DoubleClick({ Start-Process 'http://localhost:5000' })

[System.Windows.Forms.Application]::Run()

if (-not $serverProcess.HasExited) {
  $serverProcess.Kill()
  $serverProcess.WaitForExit(2000) | Out-Null
}
$notifyIcon.Dispose()
