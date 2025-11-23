# Oracle Cloud SSH Connection Fix

## ⚠️ Connection Timeout Issues

If `ssh oracle-vm` times out, follow these steps:

---

## Step 1: Check Oracle Cloud Firewall

SSH might be blocked. Add it to Security List:

1. Go to **Oracle Cloud Console**: https://cloud.oracle.com
2. Navigate to: **Networking** → **Virtual Cloud Networks**
3. Click your VCN → **Security Lists** → **Default Security List**
4. Click **Add Ingress Rules**
5. Add this rule:

| Field | Value |
|-------|-------|
| Source Type | CIDR |
| Source CIDR | 0.0.0.0/0 |
| IP Protocol | TCP |
| Source Port Range | All |
| Destination Port Range | 22 |
| Description | SSH Access |

6. Click **Add Ingress Rules**

---

## Step 2: Check Instance Firewall (if Oracle Linux)

If your VM runs Oracle Linux, you need to open the firewall:

```bash
# After connecting via SSH:
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=8050/tcp
sudo firewall-cmd --permanent --add-port=4040/tcp
sudo firewall-cmd --permanent --add-port=4041/tcp
sudo firewall-cmd --reload
```

---

## Step 3: Try Verbose SSH

Run this to see detailed connection info:

```powershell
ssh -vv -i C:\Users\shami\Downloads\ssh-key-2025-11-22.key -o ConnectTimeout=30 opc@80.225.192.78
```

Look for these in the output:
- ✅ "Connection established" - Good
- ❌ "Connection timed out" - Firewall issue
- ❌ "Permission denied" - Wrong key or username

---

## Step 4: Alternative - Use Oracle Cloud Shell

If SSH still doesn't work, use Oracle's built-in terminal:

1. Go to Oracle Cloud Console
2. Click your instance name
3. Click **Console Connection** → **Launch Cloud Shell Connection**
4. This gives you terminal access without SSH

---

## Step 5: Verify Instance is Running

```powershell
# Check if port 22 is open
Test-NetConnection -ComputerName 80.225.192.78 -Port 22
```

Should show `TcpTestSucceeded : True`

---

## Step 6: Update SSH Config

If the above works, update your SSH config:

```powershell
# Edit: C:\Users\shami\.ssh\config
# Change ConnectTimeout to 30 seconds:

Host oracle-vm
    HostName 80.225.192.78
    User opc
    IdentityFile C:/Users/shami/Downloads/ssh-key-2025-11-22.key
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
    Compression yes
    ConnectTimeout 30
```

---

## Quick Fix Script

```powershell
# Run this in PowerShell
$sshConfig = @"
Host oracle-vm
    HostName 80.225.192.78
    User opc
    IdentityFile C:/Users/shami/Downloads/ssh-key-2025-11-22.key
    StrictHostKeyChecking no
    ConnectTimeout 30
    ServerAliveInterval 30
"@

Set-Content -Path "$env:USERPROFILE\.ssh\config" -Value $sshConfig
ssh oracle-vm
```

---

## Still Not Working?

### Check Instance State
- Go to Oracle Cloud Console
- Verify instance shows "RUNNING" (green)
- Check the Public IP matches: `80.225.192.78`

### Try Different Network
- Mobile hotspot instead of Wi-Fi
- VPN might be blocking Oracle Cloud IPs

### Restart Instance
- In Oracle Console: Actions → Reboot
- Wait 2-3 minutes
- Try connecting again

---

## Once Connected

After successful SSH connection, run:

```bash
# Test you're in
whoami  # Should show: opc

# Check OS
cat /etc/os-release

# Then proceed with deployment
chmod +x deploy_oracle.sh
./deploy_oracle.sh
```
