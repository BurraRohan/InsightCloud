#!/bin/bash
# ═══════════════════════════════════════════════════════════
# InsightCloud — EC2 Instance Setup Script
# Run this on a fresh Ubuntu EC2 instance to set up InsightCloud
# Usage: bash deploy/ec2_setup.sh
# ═══════════════════════════════════════════════════════════

set -e  # Exit on any error

echo "=== InsightCloud EC2 Setup ==="
echo ""

# ─── Update System ─────────────────────────────────────────
echo "[1/5] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# ─── Install Docker ────────────────────────────────────────
echo "[2/5] Installing Docker..."
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# ─── Install Git ───────────────────────────────────────────
echo "[3/5] Installing Git..."
sudo apt-get install -y git

# ─── Clone Repository ─────────────────────────────────────
echo "[4/5] Cloning InsightCloud repository..."
# Replace with your actual GitHub repo URL
git clone https://github.com/YOUR_USERNAME/insightcloud.git
cd insightcloud

# ─── Create .env File ─────────────────────────────────────
echo "[5/5] Creating .env configuration file..."
cat > .env << 'EOF'
# InsightCloud Environment Configuration

# App
SECRET_KEY=generate-a-strong-random-key-here
DATABASE_URL=sqlite:///./insightcloud.db

# Storage mode: "s3" for AWS, "local" for development
STORAGE_MODE=s3
UPLOAD_DIR=./uploads

# AI mode: "bedrock" for AWS production
AI_MODE=bedrock

# AWS Settings
AWS_REGION=us-east-1
AWS_S3_BUCKET=insightcloud-uploads

# Bedrock Model (Claude 3 Haiku)
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# No AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY needed
# EC2 IAM role handles authentication automatically (more secure)
EOF

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  InsightCloud setup complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  NEXT STEPS:"
echo "  1. Edit .env with your actual SECRET_KEY"
echo "  2. Run: docker compose up --build -d"
echo "  3. Access: http://YOUR_EC2_PUBLIC_IP:8501"
echo ""
echo "  NOTE: Ensure your EC2 instance has the"
echo "  InsightCloud-EC2-Role IAM role attached"
echo "  for S3 and Bedrock access."
echo ""
