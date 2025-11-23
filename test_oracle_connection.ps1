# Oracle VM Connection Diagnostic Script
$keyPath = "C:\Users\shami\Downloads\ssh-key-2025-11-22.key"
$vmIP = "80.225.192.78"
$user = "opc"

Write-Host "`n🔬 Oracle VM Connection Diagnostic`n" -ForegroundColor Cyan

# Step 1: Test network connectivity
Write-Host "1️⃣  Testing network connectivity..." -ForegroundColor Yellow
$netTest = Test-NetConnection -ComputerName $vmIP -Port 22 -WarningAction SilentlyContinue
if ($netTest.TcpTestSucceeded) {
    Write-Host "   ✅ Port 22 is reachable`n" -ForegroundColor Green
} else {
    Write-Host "   ❌ Port 22 is NOT reachable - check firewall`n" -ForegroundColor Red
    exit 1
}

# Step 2: Check key file exists
Write-Host "2️⃣  Checking SSH key..." -ForegroundColor Yellow
if (Test-Path $keyPath) {
    Write-Host "   ✅ SSH key found`n" -ForegroundColor Green
} else {
    Write-Host "   ❌ SSH key not found at: $keyPath`n" -ForegroundColor Red
    exit 1
}

# Step 3: Fix key permissions
Write-Host "3️⃣  Setting key permissions..." -ForegroundColor Yellow
icacls $keyPath /inheritance:r 2>$null | Out-Null
icacls $keyPath /grant:r "$($env:USERNAME):(R)" 2>$null | Out-Null
Write-Host "   ✅ Key permissions set`n" -ForegroundColor Green

# Step 4: Attempt connection with timeout
Write-Host "4️⃣  Attempting SSH connection..." -ForegroundColor Yellow
Write-Host "   Command: ssh -o ConnectTimeout=15 -i $keyPath $user@$vmIP`n" -ForegroundColor Gray

# Try connection
ssh -o ConnectTimeout=15 `
    -o StrictHostKeyChecking=no `
    -o UserKnownHostsFile=NUL `
    -i $keyPath `
    $user@$vmIP `
    "echo '✅ Connection successful!' && whoami && cat /etc/os-release | head -n 1"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SSH connection works!`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ SSH connection failed with exit code: $LASTEXITCODE`n" -ForegroundColor Red
    Write-Host "💡 Possible issues:" -ForegroundColor Yellow
    Write-Host "   1. Wrong username (try 'ubuntu' instead of 'opc')" -ForegroundColor Gray
    Write-Host "   2. Wrong SSH key (check if you downloaded the right one)" -ForegroundColor Gray
    Write-Host "   3. Instance firewall blocking (firewall-cmd on Oracle Linux)" -ForegroundColor Gray
    Write-Host "   4. Instance not fully started (wait 2-3 minutes)`n" -ForegroundColor Gray
    Write-Host "🔧 Try Oracle Cloud Shell instead:" -ForegroundColor Cyan
    Write-Host "   1. Go to: https://cloud.oracle.com" -ForegroundColor White
    Write-Host "   2. Click your instance" -ForegroundColor White
    Write-Host "   3. Click 'Console Connection' → 'Launch Cloud Shell Connection'`n" -ForegroundColor White
}
