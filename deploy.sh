#!/bin/bash
# Deploy waybill-extractor to VPS
set -e

VPS="159.195.37.48"
DIR="/opt/waybill-extractor"
USER="root"

echo "🚀 Deploying to $VPS..."

# Create dir on VPS
ssh $USER@$VPS "mkdir -p $DIR"

# Copy files
scp -r app.py extractor.py schemas.py requirements.txt .env $USER@$VPS:$DIR/

# Install & restart on VPS
ssh $USER@$VPS << 'REMOTE'
cd /opt/waybill-extractor
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt -q
pkill -f "streamlit run app.py" 2>/dev/null || true
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > streamlit.log 2>&1 &
echo "✅ Running on port 8501"
REMOTE

echo "✅ Deployed. URL: http://$VPS:8501"
