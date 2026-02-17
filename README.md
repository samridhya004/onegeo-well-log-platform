# OneGeo Well Log Platform

A full-stack well log analysis platform built with FastAPI, PostgreSQL, React, and Plotly.

This project demonstrates scalable ingestion of LAS well log data, efficient querying, visualization, and rule-based AI interpretation.

---

## Features

- Upload LAS files
- Raw LAS stored securely in AWS S3
- Structured data stored in PostgreSQL
- Efficient bulk ingestion (1M+ rows supported)
- Indexed depth-based querying
- Interactive Plotly visualization
- Statistical analysis of curve data
- Rule-based AI interpretation engine
- Single-page professional dashboard UI

---

## Architecture Overview

### Backend
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- AWS S3 (raw file storage)

### Frontend
- React (Vite)
- Axios
- Plotly.js

### Data Flow

1. User uploads LAS file
2. Raw file stored in S3
3. LAS parsed using `lasio`
4. Structured data inserted into PostgreSQL
5. Indexed queries enable efficient depth-range filtering
6. Frontend visualizes curve
7. AI interpretation engine generates structured insights

---

## Database Schema

### wells
- id
- name
- original_filename
- created_at

### curves
- id
- well_id (FK)
- mnemonic
- unit

### measurements
- id
- curve_id (FK)
- depth (indexed)
- value

Indexes:
- Depth index for fast interval queries
- Foreign key relationships for structured retrieval

---

## AI Interpretation Engine

The interpretation pipeline is structured into three layers:

1. Data Extraction
2. Statistical Analysis
   - Min, Max, Mean, Std Dev
   - Variability classification
   - Trend detection
   - Spread analysis
3. Domain-Aware Rule Layer (Optional Enhancements)
   - Gamma Ray heuristics
   - Resistivity heuristics
   - Density & Sonic hints

The system remains deterministic, explainable, and extensible.

---

# Design Decisions

- **PostgreSQL** chosen for structured relational storage and indexed depth queries.
- **AWS S3** used for raw LAS archival storage.
- **Bulk insertion** implemented for scalable ingestion.
- **Layered interpretation pipeline** to separate statistical logic from domain rules.
- **Single-page dashboard** for usability and clarity.

---

# Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- AWS S3 bucket (Optional)

---

# AWS Setup (Production Mode Only)

1. Create S3 bucket
2. Create IAM user with S3 access
3. Generate access keys
4. Add credentials to .env

---

# Quick Start (No AWS Required)

The application can be run locally without configuring AWS S3.

In this mode:

1. Ensure PostgreSQL database `onegeo` exists.
2. Configure only the `DATABASE_URL` in the `.env` file.
3. Leave AWS environment variables empty if S3 upload is not required.
4. Run the backend and frontend normally.
5. Upload LAS files and work with structured data stored in PostgreSQL.

Note: AWS S3 integration is included for production-grade raw file storage, but the core ingestion, querying, visualization, and interpretation features work independently of S3.

---

# Full Setup Instructions

---

# 1. Clone Repository

## Mac / Linux

```bash
git clone https://github.com/samridhya004/onegeo-well-log-platform.git
cd onegeo-well-log-platform
```

## Windows (PowerShell)

```bash
git clone https://github.com/samridhya004/onegeo-well-log-platform.git
cd onegeo-well-log-platform
```
# 2. PostgreSQL Setup

Create a database named:

```bash
onegeo
```

Example (psql):

```bash
CREATE DATABASE onegeo;
```

# 3. Backend Setup

Navigate to backend:

```bash
cd backend
```

## Create Virtual Environment

### Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Create .env File

Inside backend/, create:

```bash
.env
```

Add:

```bash
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/onegeo
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-bucket-name
```
Replace placeholders with your local configuration.

## Run Backend Server

```bash
uvicorn app.main:app --reload
```

Backend will run at:

```bash
http://127.0.0.1:8000
```

Swagger Docs:

```bash
http://127.0.0.1:8000/docs
```

# 4. Frontend Setup

Navigate to frontend:

```bash
cd ../frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

Frontend runs at:

```bash
http://localhost:5173
```

## How To Use

1. Upload LAS file
2. Select well
3. Select curve
4. Enter depth range
5. Click "Plot Curve"
6. View:
    - Interactive plot
    - Statistical summary
    - AI interpretation

## Performance Notes

- Bulk insertion used for efficient ingestion
- Depth indexed for fast interval queries
- Designed to scale for millions of rows
- Structured schema avoids redundancy

## Future Improvements

- Multi-curve track visualization
- Advanced AI / ML-based interpretation
- Deployment using Docker + AWS ECS
- Authentication layer
- Exportable reports

## Author

Samridhya Khajuria

Focus: Software engineering fundamentals, scalability, architecture, and clarity.