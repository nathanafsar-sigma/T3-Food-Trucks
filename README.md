# 🚚 T3 Food Trucks Data Pipeline

A data lake solution for Tasty Truck Treats (T3), migrating transaction data from RDS to AWS S3 with Athena querying and Streamlit dashboards.

## Overview

T3 operates a fleet of food trucks in Lichfield and surrounding areas, each offering unique menus and culinary experiences. The trucks operate semi-independently, uploading sales data to a central database every few hours.

### The Problem

The company's existing RDS MySQL infrastructure has become increasingly expensive to maintain. As T3 explores potential acquisition opportunities, demonstrating a robust and cost-effective data architecture is critical for financial stability.

### The Solution

This project implements a complete data migration from RDS to a modern data lake architecture:

- **Cost Reduction**: S3 storage is significantly cheaper than RDS for historical data
- **Scalability**: Parquet format with time-based partitioning enables efficient querying at scale
- **Flexibility**: Athena provides serverless, pay-per-query analytics without managing infrastructure
- **Accessibility**: Streamlit dashboards give stakeholders real-time insights into fleet performance

### Key Features

- 🔄 Automated ETL pipeline for historical and periodic data migration
- 📊 Interactive dashboard for revenue, truck performance, and sales patterns
- 📧 Daily automated reports delivered via Lambda
- 🏗️ Infrastructure as Code with Terraform for reproducible deployments
- 🐳 Dockerized components for consistent environments

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RDS       │────▶│   Extract   │────▶│  Transform  │────▶│   S3 Data   │
│   MySQL     │     │   (Python)  │     │  (Parquet)  │     │    Lake     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                        ┌─────────────┐     ┌─────────────┐
                                        │  Streamlit  │◀────│   Athena    │
                                        │  Dashboard  │     │   Queries   │
                                        └─────────────┘     └─────────────┘
```

## Project Structure

```
T3-Food-Trucks/
├── pipeline/                    # ETL pipeline
│   ├── extract.py              # Extract data from RDS
│   ├── transform.py            # Clean and transform data
│   ├── create_parquet.py       # Convert to Parquet format
│   ├── upload_to_s3.py         # Upload to S3 data lake
│   ├── pipeline.py             # Main orchestration script
│   ├── exploration.ipynb       # Data exploration notebook
│   └── Dockerfile
├── dashboard/                   # Streamlit dashboard
│   ├── dashboard.py            # Main dashboard app
│   ├── queries.py              # Athena query functions
│   └── Dockerfile
├── daily report/               # Lambda report generator
│   ├── generate_report.py      # Daily HTML report
│   └── Dockerfile
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   └── variables.tf
└── case_study.md
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Storage | AWS S3 |
| Query Engine | AWS Athena |
| Database (Source) | AWS RDS MySQL |
| ETL | Python, Pandas |
| Data Format | Parquet (partitioned by date) |
| Dashboard | Streamlit, Plotly |
| Infrastructure | Terraform |
| Containerization | Docker |

## Data Schema

The source data uses a STAR schema:

- **DIM_Truck** - Truck information (name, FSA rating, card reader status)
- **DIM_Payment_Method** - Payment method types
- **FACT_Transaction** - Sales transactions (timestamp, amount, truck, payment method)

## Setup

### Prerequisites

- Python 3.12+
- Docker
- AWS CLI configured
- Terraform

### Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=your-rds-endpoint
DB_PORT=3306
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database

S3_BUCKET_NAME=your-s3-bucket
ATHENA_DATABASE=your-athena-database
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/T3-Food-Trucks.git
   cd T3-Food-Trucks
   ```

2. Install dependencies for each component:
   ```bash
   pip install -r pipeline/pipeline_requirements.txt
   pip install -r dashboard/dashboard_requirements.txt
   ```

## Usage

### Run the ETL Pipeline

```bash
cd pipeline
python pipeline.py
```

Or with Docker:
```bash
docker build -t t3-pipeline ./pipeline
docker run --env-file .env t3-pipeline
```

### Run the Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Or with Docker:
```bash
docker build -t t3-dashboard ./dashboard
docker run -p 8501:8501 --env-file .env t3-dashboard
```

Access at: http://localhost:8501

### Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Pipeline Steps

1. **Extract** - Pull data from RDS MySQL into CSV files
2. **Transform** - Clean, deduplicate, and validate data
3. **Create Parquet** - Convert to time-partitioned Parquet files
4. **Upload** - Push to S3 data lake

## Dashboard Features

- 📊 Daily revenue trends
- 🚚 Truck performance comparison
- 💳 Payment method distribution
- ⏰ Hourly sales patterns
- 📅 Day of week analysis

## Stakeholders

| Name | Role | Priority |
|------|------|----------|
| Hiram Boulie | CFO | Cost reduction, profitability |
| Miranda Courcelle | Head of Culinary Experience | Menu optimization, location insights |
| Alexander D'Torre | Head of Technology | Scalable, cost-effective architecture |

## License

Internal project for Tasty Truck Treats (T3).