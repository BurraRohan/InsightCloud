# ☁️ InsightCloud

**Cloud-native GenAI CSV Analytics Platform on AWS**

Upload CSV files and get AI-driven, explainable insights using natural language — powered by AWS Bedrock (Mistral 8B) for production and Groq LLaMA 3.3 70B (free) for local development.

---

## Tech Stack

| Component       | Technology                              |
| --------------- | --------------------------------------- |
| UI              | Streamlit                               |
| Data Processing | Pandas                                  |
| AI (Production) | AWS Bedrock — Mistral Ministral 3 8B    |
| AI (Local/Free) | Groq — LLaMA 3.3 70B Versatile         |
| Storage         | AWS S3 (+ local dual mode)              |
| Compute         | AWS EC2                                 |
| Auth            | JWT + bcrypt                            |
| Database        | SQLite + SQLAlchemy                     |
| Container       | Docker + docker-compose                 |
| CI/CD           | GitHub Actions                          |
| Theme           | Warm Gold (#B88E23)                     |

---

## Quick Start (Local Development — Completely FREE)

```bash
# 1. Clone the repository
git clone https://github.com/BurraRohan/Cloud-native-GenAI-CSV-Analytics-Platform.git
cd Cloud-native-GenAI-CSV-Analytics-Platform

# 2. Set up virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create and configure .env
cp .env.example .env
# Get your FREE Groq API key at https://console.groq.com (no credit card needed)
# Set GROQ_API_KEY in .env

# 5. Run the app
streamlit run app.py

# 6. Open in browser → http://localhost:8501
```

> **Note:** Local mode uses `STORAGE_MODE=local` + `AI_MODE=groq`. No AWS account needed. Groq free tier gives 14,400 requests/day.

---

## Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8501
```

---

## Environment Modes

| Mode          | Storage              | AI                | Cost        | Use Case                |
| ------------- | -------------------- | ----------------- | ----------- | ----------------------- |
| **Local Dev** | `STORAGE_MODE=local` | `AI_MODE=groq`    | FREE        | Development & testing   |
| **AWS Prod**  | `STORAGE_MODE=s3`    | `AI_MODE=bedrock` | AWS pricing | Production deployment   |
| **Mixed**     | `STORAGE_MODE=s3`    | `AI_MODE=groq`    | S3 only     | Testing S3 with free AI |

No code changes needed — `upload.py` and `genai.py` handle mode switching automatically via `.env` toggles.

---

## How the AI Works

InsightCloud uses **context injection** to ensure the AI only answers based on your actual uploaded data:

1. User uploads a CSV → Pandas reads it
2. `build_context()` extracts: column names, data types, `df.describe()`, first 5 rows, null counts
3. This real data context + user's question gets sent to the AI
4. AI responds with specific numbers, percentages, and recommendations from your dataset

The system prompt includes a **few-shot example** to teach the AI the desired answer format — specific, data-driven, with actionable recommendations.

---

## Role-Based Access Control

Three enforced roles with real feature restrictions:

| Feature              | Admin | Analyst | Viewer |
| -------------------- | ----- | ------- | ------ |
| Dashboard            | ✅    | ✅      | ✅     |
| Upload CSV           | ✅    | ✅      | ❌     |
| Ask AI               | ✅    | ✅      | ✅     |
| Load Datasets        | ✅    | ✅      | ✅     |
| User Management      | ✅    | ❌      | ❌     |
| Download PDF Report  | ✅    | ✅      | ✅     |

---

## AWS Deployment Guide

### Step 1: Create S3 Bucket
1. Go to **AWS S3 Console**
2. Create bucket: `insightcloud-uploads`
3. Region: `us-east-1`
4. Block all public access: **YES**
5. Enable encryption: **AES-256**

### Step 2: Create IAM Role for EC2
1. Go to **AWS IAM Console**
2. Create Role → AWS Service → EC2
3. Create custom policy using [`deploy/iam_policy.json`](deploy/iam_policy.json)
4. Name: `InsightCloud-EC2-Role`

### Step 3: Launch EC2 & Deploy
1. AMI: **Ubuntu 24.04 LTS** | Type: **t3.micro** (free tier)
2. Security group: allow **port 8501** + **port 22**
3. IAM profile: **InsightCloud-EC2-Role**
4. SSH in and run:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose git
git clone https://github.com/BurraRohan/Cloud-native-GenAI-CSV-Analytics-Platform.git
cd Cloud-native-GenAI-CSV-Analytics-Platform
nano .env  # Add your environment variables
sudo docker-compose up --build -d
```

5. Access: `http://your-ec2-public-ip:8501`

---

## Testing

87 test cases across 5 modules — all passing:

```
tests/test_auth.py        — 17 tests (password hashing, JWT, signup, login)
tests/test_upload.py      — 16 tests (CSV validation, file save, list, load)
tests/test_processing.py  — 20 tests (summary stats, groupby, column analysis)
tests/test_genai.py       — 19 tests (context building, prompts, messages)
tests/test_config.py      — 15 tests (mode toggles, env vars, settings)
```

Run tests: `pytest`

---

## Monitoring

AWS CloudWatch dashboard (`InsightCloud-Monitoring`) tracking:
- **S3 Storage** — BucketSizeBytes, NumberOfObjects
- **AI Performance** — Invocations, InvocationLatency
- **Token Usage** — InputTokenCount, OutputTokenCount, EstimatedTPMQuotaUsage

---

## Project Structure

```
insightcloud/
├── app.py                → Streamlit UI (login, signup, dashboard, upload, AI query)
├── auth.py               → JWT authentication (signup, login, token management)
├── upload.py             → CSV upload & validation — dual mode (local + S3)
├── processing.py         → Pandas data analysis & summary statistics
├── genai.py              → AI integration — dual mode (Groq + Bedrock Mistral)
├── database.py           → SQLAlchemy + SQLite setup
├── models.py             → User database model
├── config.py             → Centralized configuration & mode toggles
├── s3_utils.py           → AWS S3 helper functions
├── report.py             → PDF report generator
├── requirements.txt      → Python dependencies
├── pytest.ini            → Test configuration
├── Dockerfile            → Container definition
├── docker-compose.yml    → Container orchestration
├── .env.example          → Environment variables template
├── tests/                → 87 test cases
├── .streamlit/
│   └── config.toml       → Streamlit theme configuration
├── deploy/
│   ├── ec2_setup.sh      → EC2 bootstrap script
│   └── iam_policy.json   → Least-privilege IAM policy (S3 + Bedrock)
└── .github/
    └── workflows/
        └── ci.yml        → GitHub Actions CI/CD pipeline
```

---

## Key Features

- 🔐 **JWT Authentication** — Secure signup/login with bcrypt password hashing
- 👥 **Role-Based Access** — Admin, Analyst, Viewer with enforced restrictions
- 📁 **Dual-Mode Storage** — Seamless local ↔ S3 switching via `STORAGE_MODE`
- 🧠 **Dual AI Mode** — Groq (free, fast) for local, Bedrock Mistral for AWS production
- 📊 **Pandas Processing** — Auto summary statistics, column analysis, null detection
- 💬 **Context-Injected AI** — Real dataset info sent with every query for accurate answers
- 📄 **PDF Reports** — Download AI insights as professional PDF documents
- 📈 **Performance Metrics** — Response time tracking, query count, average latency
- 🎨 **Polished UI** — Warm gold theme (#B88E23), Playfair Display + DM Sans typography
- 🐳 **Docker Ready** — One-command deployment with docker-compose
- ⚙️ **CI/CD Pipeline** — GitHub Actions for automated testing and Docker builds
- 🔒 **Security** — IAM least-privilege, env variables, input validation, S3 encryption
- 🧪 **87 Test Cases** — Comprehensive pytest coverage across all modules
- 📊 **CloudWatch Monitoring** — S3 storage, Bedrock latency, token usage dashboards

---

## Security Practices

- JWT tokens with bcrypt password hashing
- Role-based access control (Admin, Analyst, Viewer)
- IAM roles for EC2 → S3 and Bedrock access (least privilege)
- API keys stored in environment variables — never hardcoded
- CSV input validation (file type, size, readability)
- AES-256 server-side encryption for S3 uploads
- HTTPS for all communication in production

---
