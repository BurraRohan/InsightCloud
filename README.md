# ☁️ InsightCloud

**Cloud-native GenAI CSV Analytics Platform on AWS**

Upload CSV files and get AI-driven, explainable insights using natural language — powered by AWS Bedrock (Claude 3 Haiku) for production and Groq LLaMA 3.3 70B (free) for local development.

---

## Tech Stack

| Component       | Technology                     |
| --------------- | ------------------------------ |
| UI              | Streamlit                      |
| Data Processing | Pandas                         |
| AI (Production) | AWS Bedrock (Claude 3 Haiku)   |
| AI (Local/Free) | Groq — LLaMA 3.3 70B Versatile |
| Storage         | AWS S3 (+ local mode)          |
| Compute         | AWS EC2                        |
| Auth            | JWT + bcrypt                   |
| Database        | SQLite + SQLAlchemy            |
| Container       | Docker + docker-compose        |
| CI/CD           | GitHub Actions                 |
| Theme           | Warm Gold (#B88E23)            |

---

## Quick Start (Local Development — Completely FREE)

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/insightcloud.git
cd insightcloud

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

## AWS Deployment Guide

### Step 1: Enable Claude Haiku in Bedrock

1. Go to **AWS Bedrock Console** (us-east-1 region)
2. Click **"Model access"** → **"Manage model access"**
3. Check **"Claude 3 Haiku"** by Anthropic
4. Click **"Save changes"** and wait for **"Access granted"**

### Step 2: Create S3 Bucket

1. Go to **AWS S3 Console**
2. Create bucket: `insightcloud-uploads`
3. Region: `us-east-1`
4. Block all public access: **YES**
5. Enable encryption: **AES-256**

### Step 3: Create IAM Role for EC2

1. Go to **AWS IAM Console**
2. Create Role → AWS Service → EC2
3. Create custom policy using [`deploy/iam_policy.json`](deploy/iam_policy.json)
4. Name: `InsightCloud-EC2-Role`

> The IAM policy follows **least-privilege** — only allows S3 bucket access and Bedrock Claude Haiku invocation.

### Step 4: Launch EC2 & Deploy

1. AMI: **Ubuntu 24.04 LTS** | Type: **t2.micro** (free tier)
2. Security group: allow **port 8501** + **port 22**
3. IAM profile: **InsightCloud-EC2-Role**
4. SSH in and run:

```bash
bash deploy/ec2_setup.sh
docker compose up --build -d
```

5. Access: `http://your-ec2-public-ip:8501`

---

## Project Structure

```
insightcloud/
├── app.py                → Streamlit UI (login, signup, dashboard, upload, AI query)
├── auth.py               → JWT authentication (signup, login, token management)
├── upload.py             → CSV upload & validation — dual mode (local + S3)
├── processing.py         → Pandas data analysis & summary statistics
├── genai.py              → AI integration — triple mode (Groq + Gemini + Bedrock)
├── database.py           → SQLAlchemy + SQLite setup
├── models.py             → User database model
├── config.py             → Centralized configuration & mode toggles
├── s3_utils.py           → AWS S3 helper functions
├── requirements.txt      → Python dependencies
├── Dockerfile            → Container definition
├── docker-compose.yml    → Container orchestration
├── .env.example          → Environment variables template
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

- 🔐 **JWT Authentication** — Secure signup/login with bcrypt password hashing and role-based access
- 📁 **Dual-Mode Storage** — Seamless local ↔ S3 switching via `STORAGE_MODE` in `.env`
- 🧠 **Triple AI Mode** — Groq (free, fast), Gemini (free), Bedrock (AWS production)
- 📊 **Pandas Processing** — Auto summary statistics, column analysis, null detection, data preview
- 💬 **Context-Injected AI** — Real dataset info (columns, types, stats, sample rows) sent with every query
- 📝 **Few-Shot Prompting** — AI taught to give specific numbers, percentages, and recommendations
- 🎨 **Polished UI** — Warm gold theme (#B88E23), Playfair Display + DM Sans typography
- 🐳 **Docker Ready** — One-command deployment with docker-compose
- ⚙️ **CI/CD Pipeline** — GitHub Actions for automated testing and Docker builds
- 🔒 **Security** — IAM least-privilege policies, environment variables for secrets, input validation, HTTPS

---

## Security Practices

- JWT tokens with bcrypt password hashing
- IAM roles for EC2 → S3 and Bedrock access (least privilege)
- API keys stored in environment variables — never hardcoded
- CSV input validation (file type, size, readability)
- HTTPS for all communication in production

---

## Course

**Cloud Product & Platform Engineering (21IPE315P)** — Review 2

**Team:** Jan Saida (RA2311003010093), B. Rohan (RA2311003010113)

**Faculty:** Mrs. Agalya A
