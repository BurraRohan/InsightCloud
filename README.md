# ☁️ InsightCloud
 
**Turn CSV files into conversational, AI-driven insights — no coding required.**
 
InsightCloud is a cloud-native SaaS platform where users upload structured datasets and ask questions in plain English. The AI responds with specific, data-backed answers drawn from the actual uploaded data — not generic responses.
 
Built with Python, Streamlit, Pandas, and AWS (S3, Bedrock, EC2), with a free local development mode using Groq.
 
---
 
## How It Works
 
```
Upload CSV → Pandas analyzes it → You ask a question → AI answers with your real data
```
 
Every AI query uses **context injection** — the system extracts column names, data types, summary statistics, sample rows, and null counts from your dataset, then sends that context alongside your question. The AI never guesses; it works with your actual numbers.
 
---
 
## Tech Stack
 
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Data Processing | Pandas |
| AI (Production) | AWS Bedrock — Mistral 8B |
| AI (Local/Free) | Groq — LLaMA 3.3 70B |
| Storage | AWS S3 + local dual mode |
| Compute | AWS EC2 |
| Auth | JWT + bcrypt |
| Database | SQLite + SQLAlchemy |
| Containers | Docker + docker-compose |
| CI/CD | GitHub Actions |
 
---
 
## Quick Start
 
### Local Development (completely free)
 
```bash
git clone https://github.com/BurraRohan/Cloud-native-GenAI-CSV-Analytics-Platform.git
cd Cloud-native-GenAI-CSV-Analytics-Platform
 
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate          # Windows
 
pip install -r requirements.txt
 
cp .env.example .env
# Get a FREE Groq API key at https://console.groq.com (no credit card needed)
# Set GROQ_API_KEY in .env
 
streamlit run app.py
# Open http://localhost:8501
```
 
Local mode uses `STORAGE_MODE=local` and `AI_MODE=groq`. No AWS account needed — Groq's free tier gives 14,400 requests/day.
 
### Docker
 
```bash
docker-compose up --build
# Access at http://localhost:8501
```
 
---
 
## Features
 
### Context-Injected AI Responses
The AI doesn't just receive your question — it receives your entire dataset's structure. `build_context()` extracts columns, types, `df.describe()` output, first 5 rows, and null counts. A few-shot system prompt teaches the model to respond with specific numbers, percentages, and actionable recommendations.
 
### Role-Based Access Control
Three enforced roles with real feature restrictions — not cosmetic labels:
 
| Feature | Admin | Analyst | Viewer |
|---------|-------|---------|--------|
| Dashboard | ✅ | ✅ | ✅ |
| Upload CSV | ✅ | ✅ | ❌ |
| Ask AI | ✅ | ✅ | ✅ |
| Load Datasets | ✅ | ✅ | ✅ |
| User Management | ✅ | ❌ | ❌ |
| Download PDF Report | ✅ | ✅ | ✅ |
 
### Dual Environment Modes
Switch between local and AWS with zero code changes — just toggle `.env` variables:
 
| Mode | Storage | AI Provider | Cost |
|------|---------|-------------|------|
| Local Dev | `STORAGE_MODE=local` | `AI_MODE=groq` | Free |
| AWS Production | `STORAGE_MODE=s3` | `AI_MODE=bedrock` | AWS pricing |
| Mixed | `STORAGE_MODE=s3` | `AI_MODE=groq` | S3 costs only |
 
### PDF Report Generation
Download AI insights as formatted PDF documents — useful for sharing analysis with non-technical stakeholders.
 
### Security
- JWT authentication with bcrypt password hashing
- Role-based access control enforced server-side
- IAM least-privilege roles (EC2 → S3 + Bedrock only)
- API keys in environment variables, never hardcoded
- CSV input validation (type, size, readability checks)
- AES-256 server-side encryption on all S3 uploads
- HTTPS in production
### Monitoring
AWS CloudWatch dashboard tracking S3 storage metrics, Bedrock invocation latency, and token usage across input/output counts.
 
### Testing
87 tests across 5 modules covering authentication, file upload/validation, data processing, AI integration, and configuration. Run with `pytest`.
 
### CI/CD
GitHub Actions pipeline triggered on every push to `main` — runs module import tests, verifies auth (hash + verify), and builds the Docker image.
 
---
 
## AWS Deployment
 
### 1. Create S3 Bucket
Create a bucket named `insightcloud-uploads` in `us-east-1` with public access blocked and AES-256 encryption enabled.
 
### 2. Create IAM Role
Create an EC2 role with a custom policy (`deploy/iam_policy.json`) granting least-privilege access to S3 and Bedrock only.
 
### 3. Launch EC2 and Deploy
 
```bash
# On a fresh Ubuntu 24.04 EC2 instance (t3.micro)
sudo apt update && sudo apt install -y docker.io docker-compose git
git clone https://github.com/BurraRohan/Cloud-native-GenAI-CSV-Analytics-Platform.git
cd Cloud-native-GenAI-CSV-Analytics-Platform
nano .env  # Configure your environment variables
sudo docker-compose up --build -d
```
 
Access at `http://your-ec2-public-ip:8501`
 
Security group should allow inbound on ports 22 (SSH) and 8501 (Streamlit).
 
---
 
## Project Structure
 
```
├── app.py                 # Streamlit UI — login, dashboard, upload, AI query
├── auth.py                # JWT authentication — signup, login, token management
├── upload.py              # CSV upload & validation — local + S3 dual mode
├── processing.py          # Pandas data analysis & summary statistics
├── genai.py               # AI integration — Groq + Bedrock dual mode
├── database.py            # SQLAlchemy + SQLite setup
├── models.py              # User database model
├── config.py              # Centralized configuration & mode toggles
├── s3_utils.py            # AWS S3 helper functions
├── report.py              # PDF report generator
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example           # Environment variables template
├── tests/                 # 87 test cases across 5 modules
├── .streamlit/
│   └── config.toml        # Streamlit theme (warm gold #B88E23)
├── deploy/
│   ├── ec2_setup.sh       # EC2 bootstrap script
│   └── iam_policy.json    # Least-privilege IAM policy
└── .github/
    └── workflows/
        └── ci.yml         # GitHub Actions CI/CD pipeline
```
 
---
 
## Future Improvements
 
- Migrate frontend to React for a smoother production experience
- Add support for Excel (.xlsx) uploads alongside CSV
- Implement GenAI response caching to reduce latency and cost
- Add auto-scaling with ECS/EKS for handling concurrent users
- Integrate SonarQube for automated code quality checks
---
