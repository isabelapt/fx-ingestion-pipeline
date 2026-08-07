# 💱 FX Rate Ingestion Pipeline & Data Lake

[![CI/CD Pipeline](https://github.com/isabelapt/fx-ingestion-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/isabelapt/fx-ingestion-pipeline/actions)
![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple.svg)
![AWS](https://img.shields.io/badge/AWS-Serverless-orange.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)

An enterprise-grade, event-driven **Serverless Data Pipeline** designed to ingest daily Foreign Exchange (FX) rates from external financial APIs, validate data contracts, enforce domain rules, and persist partitioned raw payloads into an AWS S3 Data Lake exposed via **Amazon Athena**.

---

## 📐 Architecture Overview

![AWS Serverless Architecture](docs/diagrams/fx_ingestion_architecture.png)

*For a detailed resource-by-resource explanation of the cloud components and Event-Driven flows, refer to the **[AWS Architecture Diagram Guide](docs/architecture_diagram.md)**.*

### Key Technical Features:

* **Clean Architecture & DDD:** Domain entities (`FXRateEntity`), value validation (`FXRateData` Pydantic schemas), and use-case orchestration decoupled from AWS SDKs (`boto3`).
* **Infrastructure as Code (IaC):** 100% provisioned via **Terraform** using `config.yaml` as a single source of truth.
* **Partitioned Data Lake:** Hive-style partition layout (`raw/year=YYYY/month=MM/day=DD/`) for query optimization and cost minimization on Amazon Athena.
* **Automated CI/CD:** GitHub Actions workflow with OpenID Connect (OIDC) authentication for passwordless AWS deployment and strict 100% test coverage enforcement (`pytest` + `uv`).

---

## 📊 Analytics Layer (Amazon Athena)

Data stored in S3 is cataloged in **AWS Glue** and made instantly queryable via standard SQL in **Amazon Athena**.

### Sample SQL Query (`queries/athena_queries.sql`):

```sql
SELECT 
    observation_date,
    base_currency,
    rates['eur'] AS eur_rate,
    rates['brl'] AS brl_rate
FROM fx_rates_db_dev.raw_fx_rates
ORDER BY observation_date DESC;
```

### Query Results Preview:

![Athena Query Results](docs/images/athena_query_results.png)

---

## 🛠️ Project Structure

```text
fx-ingestion-pipeline/
├── .github/workflows/    # CI/CD Workflows (CI + Terraform Deploy/Destroy)
├── config.yaml           # Centralized configuration (IaC & App)
├── docs/                 # Project documentation & guides
│   ├── diagrams/         # Generated architecture diagrams (PNG)
│   │   └── fx_ingestion_architecture.png
│   ├── images/           # Documentation images and screenshots
│   │   └── athena_query_results.png
│   ├── architecture_diagram.md # Detailed guide mapping AWS components & flows
│   ├── architecture_guide.md # Clean Architecture & domain design overview
│   └── iam_roles_guide.md # Detailed AWS IAM Roles & Permissions Guide
├── infra/
│   └── terraform/        # Terraform modules (Lambda, S3, Glue, IAM, EventBridge)
├── queries/
│   └── athena_queries.sql # Athena DDL & analytical queries
├── src/
│   ├── adapters/         # API Client & Lambda Handler
│   ├── domain/           # Entities, Pydantic Schemas, and Business Rules
│   ├── infra/            # S3 Repository (Boto3 persistence)
│   └── use_cases/        # Orchestrator Use Cases
└── tests/                # Unit & Integration Tests (100% Coverage)
```

---

## 📚 Detailed Documentation

For deeper dives into specific aspects of the platform, refer to the guides below:

* ☁️ **[AWS Architecture Diagram Guide](docs/architecture_diagram.md):** In-depth functional description of each AWS component, event flows, Lambda configuration, CloudWatch alarms, and SNS topics.
* 📐 **[Software Architecture Guide](docs/architecture_guide.md):** In-depth explanation of Clean Architecture layers, Domain-Driven Design (DDD) principles, Pydantic schemas, Python dataclass validation, and testing mock strategy.
* 🛡️ **[AWS IAM Roles & Permissions Guide](docs/iam_roles_guide.md):** Detailed security configuration, resource-restricted IAM policy JSONs (both for Terraform execution and Lambda runtime), EventBridge CRON rules, and alerting flows.

---

## 🚀 Getting Started Locally

### Prerequisites

* **Python 3.12+** and **uv** package manager
* **Terraform >= 1.5.0**
* **AWS CLI** configured

### 1. Installation & Environment Setup

```bash
# Clone repository
git clone https://github.com/isabelapt/fx-ingestion-pipeline.git
cd fx-ingestion-pipeline

# Install dependencies with uv
uv sync
```

### 2. Run Test Suite

```bash
# Run unit and integration tests with coverage
uv run pytest --cov=src --cov-report=term-missing
```

### 3. Provision AWS Infrastructure

```bash
cd infra/terraform
terraform init
terraform apply -auto-approve
```

### 4. Destroy AWS Resources

```bash
cd infra/terraform
terraform destroy -auto-approve
```

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
