# Fast SSH Connection to Oracle Cloud VM
# This script optimizes SSH connection speed

$keyPath = "C:\Users\shami\Downloads\ssh-key-2025-11-22.key"
$vmIP = "80.225.192.78"
$user = "opc"

Write-Host "`n🚀 Connecting to Oracle Cloud VM..." -ForegroundColor Cyan
Write-Host "IP: $vmIP" -ForegroundColor Gray
Write-Host "User: $user`n" -ForegroundColor Gray

# Fix key permissions (suppress output)
icacls $keyPath /inheritance:r 2>$null | Out-Null
icacls $keyPath /grant:r "$($env:USERNAME):(R)" 2>$null | Out-Null

# Connect with optimized SSH options
# -o StrictHostKeyChecking=no - Skip host key verification prompt
# -o ConnectTimeout=10 - Fail fast if can't connect
# -o ServerAliveInterval=60 - Keep connection alive
ssh -i $keyPath `
    -o StrictHostKeyChecking=no `
    -o ConnectTimeout=10 `
    -o ServerAliveInterval=60 `
    -o ServerAliveCountMax=3 `
    -o TCPKeepAlive=yes `
    -o Compression=yes `
    $user@$vmIP
