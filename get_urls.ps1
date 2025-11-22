# Quick script to get ngrok public URLs
Write-Host "`n Content Gap Analysis - Public URLs`n" -ForegroundColor Cyan

function Get-NgrokUrl {
    param($port, $name)
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/api/tunnels" -ErrorAction Stop
        if ($response.tunnels -and $response.tunnels.Count -gt 0) {
            $url = $response.tunnels[0].public_url
            Write-Host " $name" -ForegroundColor Green
            Write-Host "   $url" -ForegroundColor White
            Write-Host "   Dashboard: http://localhost:$port`n" -ForegroundColor Gray
            return $url
        }
    } catch {
        Write-Host " $name - Not ready" -ForegroundColor Yellow
        Write-Host "   Check: http://localhost:$port`n" -ForegroundColor Gray
        return $null
    }
}

$apiUrl = Get-NgrokUrl -port 4040 -name "API"
$dashUrl = Get-NgrokUrl -port 4041 -name "Dashboard"

if ($apiUrl) {
    Write-Host " API Endpoints:" -ForegroundColor Cyan
    Write-Host "   $apiUrl/docs" -ForegroundColor Gray
    Write-Host "   $apiUrl/health" -ForegroundColor Gray
    Write-Host "   $apiUrl/run`n" -ForegroundColor Gray
}
