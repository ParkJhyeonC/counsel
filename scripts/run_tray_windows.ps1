param(
  [Parameter(Mandatory=$true)][string]$RootDir,
  [Parameter(Mandatory=$true)][string]$PythonExe
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = $PythonExe
$startInfo.Arguments = 'scripts\run_tray_server.py'
$startInfo.WorkingDirectory = $RootDir
$startInfo.CreateNoWindow = $true
$startInfo.UseShellExecute = $false

$logPath = Join-Path $RootDir 'data\run_tray.log'
if (-not (Test-Path (Split-Path $logPath))) {
  New-Item -Path (Split-Path $logPath) -ItemType Directory -Force | Out-Null
}
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

$outputWriter = New-Object System.IO.StreamWriter($logPath, $true, [System.Text.Encoding]::UTF8)
$serverProcess.BeginOutputReadLine()
$serverProcess.BeginErrorReadLine()
$serverProcess.add_OutputDataReceived({
  param($sender, $args)
  if ($args.Data) {
    $outputWriter.WriteLine("[{0}] [OUT] {1}" -f (Get-Date -Format s), $args.Data)
    $outputWriter.Flush()
  }
})
$serverProcess.add_ErrorDataReceived({
  param($sender, $args)
  if ($args.Data) {
    $outputWriter.WriteLine("[{0}] [ERR] {1}" -f (Get-Date -Format s), $args.Data)
    $outputWriter.Flush()
  }
})

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

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 2000
$timer.Add_Tick({
  if ($serverProcess.HasExited) {
    $notifyIcon.BalloonTipTitle = '카운슬로그'
    $notifyIcon.BalloonTipText = '서버가 종료되었습니다. data\\run_tray.log를 확인해 주세요.'
    $notifyIcon.ShowBalloonTip(5000)
    Start-Sleep -Milliseconds 800
    $notifyIcon.Visible = $false
    [System.Windows.Forms.Application]::Exit()
  }
})
$timer.Start()

[System.Windows.Forms.Application]::Run()

if (-not $serverProcess.HasExited) {
  $serverProcess.Kill()
  $serverProcess.WaitForExit(2000) | Out-Null
}
$timer.Stop()
$outputWriter.Dispose()
$notifyIcon.Dispose()
