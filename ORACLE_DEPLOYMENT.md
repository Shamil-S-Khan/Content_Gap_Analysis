# Oracle Cloud Deployment Guide

Complete guide to deploy Content Gap Analysis on Oracle Cloud's free tier.

---

## Prerequisites

- Oracle Cloud account (sign up at https://www.oracle.com/cloud/free/)
- SSH client (PuTTY on Windows or ssh on Linux/Mac)
- Your ngrok authtokens

---

## Step 1: Create Oracle Cloud VM

### 1.1 Sign In
- Go to https://cloud.oracle.com
- Sign in to your Oracle Cloud account

### 1.2 Create Instance
1. Navigate to: **Compute** → **Instances** → **Create Instance**
2. Configure:
   - **Name:** `content-gap-analysis`
   - **Compartment:** (root) or your compartment
   - **Image:** Ubuntu 22.04 Minimal
   - **Shape:** VM.Standard.A1.Flex (ARM - Always Free)
     - OCPUs: 2
     - Memory: 12 GB
   - **Networking:** Use default VCN
   - **Add SSH Keys:** Generate or upload your key
   - **Boot Volume:** 50 GB

3. Click **Create**

### 1.3 Save Information
- Save the **Public IP address** (e.g., 132.145.XXX.XXX)
- Save the **SSH private key** (download if auto-generated)

---

## Step 2: Configure Firewall

### 2.1 Open Ports in Oracle Cloud
1. Go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN → **Security Lists** → **Default Security List**
3. Click **Add Ingress Rules** and add:

| Source CIDR | Protocol | Port Range | Description |
|-------------|----------|------------|-------------|
| 0.0.0.0/0 | TCP | 8000 | Content Gap API |
| 0.0.0.0/0 | TCP | 8050 | Dashboard |
| 0.0.0.0/0 | TCP | 4040 | ngrok API Monitor |
| 0.0.0.0/0 | TCP | 4041 | ngrok Dashboard Monitor |

### 2.2 Open Ports in Ubuntu Firewall
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8050 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 4040 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 4041 -j ACCEPT
sudo netfilter-persistent save
```

---

## Step 3: Connect to VM

### Windows (PowerShell)
```powershell
# Set correct permissions on private key
icacls "path\to\your-key.key" /inheritance:r
icacls "path\to\your-key.key" /grant:r "$($env:USERNAME):(R)"

# Connect
ssh -i path\to\your-key.key ubuntu@YOUR_PUBLIC_IP
```

### Linux/Mac
```bash
# Set correct permissions
chmod 400 ~/your-key.key

# Connect
ssh -i ~/your-key.key ubuntu@YOUR_PUBLIC_IP
```

---

## Step 4: Deploy Application

### 4.1 Copy deployment script to VM
From your local machine:
```powershell
scp -i path\to\your-key.key deploy_oracle.sh ubuntu@YOUR_PUBLIC_IP:~/
```

### 4.2 Run deployment script on VM
```bash
chmod +x deploy_oracle.sh
./deploy_oracle.sh
```

### 4.3 Add your ngrok authtokens
```bash
nano ngrok.yml
# Replace YOUR_FIRST_AUTHTOKEN_HERE with your actual token

nano ngrok-dashboard.yml
# Replace YOUR_SECOND_AUTHTOKEN_HERE with your actual token
```

### 4.4 Start services
```bash
# Re-login to apply docker group changes
exit
ssh -i path\to\your-key.key ubuntu@YOUR_PUBLIC_IP

# Navigate to project
cd ~/Content_Gap_Analysis

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

---

## Step 5: Access Your Services

### Public URLs (via ngrok)
Wait about 10 seconds for ngrok to connect, then:

```bash
# Get API URL
curl http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*'

# Get Dashboard URL
curl http://localhost:4041/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*'
```

### Direct Access (via Public IP)
- API: `http://YOUR_PUBLIC_IP:8000`
- Dashboard: `http://YOUR_PUBLIC_IP:8050`
- API Monitor: `http://YOUR_PUBLIC_IP:4040`
- Dashboard Monitor: `http://YOUR_PUBLIC_IP:4041`

---

## Step 6: Verify Deployment

```bash
# Check all containers are running
docker-compose ps

# View logs
docker-compose logs -f

# Test API health
curl http://localhost:8000/health

# Test via ngrok (get URL from step 5)
curl https://your-ngrok-url.ngrok-free.app/health
```

---

## Useful Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f ngrok-api
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services
```bash
docker-compose down
```

### Update Code
```bash
cd ~/Content_Gap_Analysis
git pull origin master
docker-compose up -d --build
```

### Monitor Resources
```bash
# Check disk space
df -h

# Check memory
free -h

# Check Docker stats
docker stats
```

---

## Auto-Start on Boot

To make services start automatically when VM reboots:

```bash
# Create systemd service
sudo nano /etc/systemd/system/content-gap-analysis.service
```

Add this content:
```ini
[Unit]
Description=Content Gap Analysis Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/Content_Gap_Analysis
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable content-gap-analysis
sudo systemctl start content-gap-analysis
```

---

## Troubleshooting

### Containers not starting?
```bash
docker-compose logs
docker system df  # Check disk space
```

### Can't access via public IP?
```bash
# Check firewall rules
sudo iptables -L -n

# Check ports are open
sudo netstat -tlnp | grep -E '8000|8050|4040|4041'
```

### ngrok authentication failed?
```bash
# Check authtoken in config
cat ngrok.yml
cat ngrok-dashboard.yml

# Restart ngrok containers
docker-compose restart ngrok-api ngrok-dashboard
```

### Out of disk space?
```bash
# Clean Docker
docker system prune -a

# Check usage
df -h
```

---

## Cost Information

**Oracle Cloud Free Tier:**
- ✅ 2 ARM VMs - Always Free
- ✅ 24 GB total RAM - Always Free
- ✅ 200 GB block storage - Always Free
- ✅ 10 TB outbound data transfer/month - Always Free
- ✅ Public IP addresses - Always Free

**Your Setup Uses:**
- 1 ARM VM (2 OCPUs, 12 GB RAM)
- 50 GB storage
- Minimal bandwidth

**Total Cost: $0/month** (within free tier limits)

---

## Security Best Practices

1. **Change SSH port** (optional):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change Port 22 to something else
   sudo systemctl restart sshd
   ```

2. **Setup firewall** (ufw):
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 8000/tcp
   sudo ufw allow 8050/tcp
   sudo ufw allow 4040/tcp
   sudo ufw allow 4041/tcp
   sudo ufw enable
   ```

3. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Use environment variables** for sensitive data instead of hardcoding

---

## Summary

✅ **24/7 availability** - VM runs continuously
✅ **Free forever** - Oracle Cloud free tier
✅ **Public access** - Both ngrok and direct IP
✅ **Auto-restart** - Systemd service ensures uptime
✅ **Scalable** - Can upgrade if needed

Your Content Gap Analysis will be accessible worldwide at:
- ngrok URLs (permanent with same authtoken)
- Direct IP: `http://YOUR_PUBLIC_IP:8000` and `http://YOUR_PUBLIC_IP:8050`

Need help? Check logs with `docker-compose logs -f`
