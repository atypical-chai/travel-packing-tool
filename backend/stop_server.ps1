# Stop the FastAPI server running on port 8000.
# Run this when the server was started from Cursor chat (no Ctrl+C).
# Usage: Right-click -> Run with PowerShell, or in terminal: .\stop_server.ps1

$port = 8000
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1

if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Host "Server on port $port stopped."
} else {
    Write-Host "No server found on port $port (already stopped?)."
}

Read-Host "Press Enter to close"
