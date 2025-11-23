#!/bin/bash
# Oracle Cloud Deployment Script for Content Gap Analysis
# Run this script on your Oracle Cloud VM

set -e

echo "🚀 Setting up Content Gap Analysis on Oracle Cloud..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
echo "📥 Cloning repository..."
cd ~
git clone https://github.com/Shamil-S-Khan/Content_Gap_Analysis.git
cd Content_Gap_Analysis

# Create ngrok config files (you'll need to add your authtokens)
echo "⚙️  Creating ngrok config files..."
cat > ngrok.yml << 'EOF'
version: "2"
authtoken: YOUR_FIRST_AUTHTOKEN_HERE
web_addr: 0.0.0.0:4040
tunnels:
  api:
    proto: http
    addr: api:8000
    inspect: true
EOF

cat > ngrok-dashboard.yml << 'EOF'
version: "2"
authtoken: YOUR_SECOND_AUTHTOKEN_HERE
web_addr: 0.0.0.0:4040
tunnels:
  dashboard:
    proto: http
    addr: dashboard:8050
    inspect: true
EOF

echo ""
echo "⚠️  IMPORTANT: Edit ngrok config files with your authtokens:"
echo "   nano ngrok.yml"
echo "   nano ngrok-dashboard.yml"
echo ""
echo "Then run: docker-compose up -d"
echo ""
echo "✅ Setup complete!"
