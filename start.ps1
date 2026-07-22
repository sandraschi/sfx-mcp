param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
)
$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$BackendPort = 11120

Write-Host "=== SFX-MCP Startup ===" -ForegroundColor Cyan

# Clear zombie processes on backend port
try {
    $zombies = Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue
    foreach ($z in $zombies) {
        Write-Host "  Killing zombie PID $($z.OwningProcess) on port $BackendPort" -ForegroundColor Yellow
        Stop-Process -Id $z.OwningProcess -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "  Port check skipped (no permission)" -ForegroundColor DarkYellow
}

# Start backend
Push-Location $ScriptRoot
$env:MCP_PORT = "$BackendPort"
$env:MCP_HOST = "127.0.0.1"
$job = Start-Job -Name "sfx-backend" -ScriptBlock {
    param($Root, $Port)
    Set-Location $Root
    & "C:\Users\sandr\.local\bin\uv.exe" run python run_server.py
} -ArgumentList $ScriptRoot, $BackendPort

# Health poll (up to 30s)
Write-Host "  Waiting for backend on :$BackendPort..." -ForegroundColor Gray
$healthy = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $healthy = $true; break }
    } catch {}
    Start-Sleep 1
}

if (-not $healthy) {
    Write-Host "  Backend failed to start within 30s" -ForegroundColor Red
    Receive-Job $job -ErrorAction SilentlyContinue
    Stop-Job $job -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "  Backend healthy on :$BackendPort" -ForegroundColor Green
Write-Host "  MCP endpoint: http://127.0.0.1:$BackendPort/mcp" -ForegroundColor Cyan
Write-Host "  Health: http://127.0.0.1:$BackendPort/api/health" -ForegroundColor Cyan

if (-not $Headless -and -not $BackendOnly -and -not $NoBrowser) {
    Start-Process "http://127.0.0.1:$BackendPort/api/health"
}

# Keep-alive
try {
    while ($true) {
        if ($job.State -eq "Completed" -or $job.State -eq "Failed") {
            Write-Host "Backend process exited." -ForegroundColor Red
            Receive-Job $job
            break
        }
        Start-Sleep 5
    }
} finally {
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
}
