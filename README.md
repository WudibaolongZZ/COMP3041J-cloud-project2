# COMP3041J-cloud-project2
Mini-project for cloud log analytics with MapReduce and Ray
# Cloud Service Log Analytics

This project implements MapReduce-based cloud log analytics using the `mrjob` framework in Python.

The system processes a synthetic cloud service log dataset and generates analytics results for:

- Request count by service
- Server error count by service
- Top 10 slow endpoints

---

# Project Structure

```text
COMP3041J-cloud-project2/
│
├── sample.csv
├── mr_job_tasks.py
└── README.md
```

---

# Requirements

Install the required Python package:

```bash
pip install mrjob
```

---

# Dataset

The input dataset is a CSV log file:

```text
sample.csv
```

Each log record contains fields such as:

- service_name
- endpoint
- status_code
- response_time_ms

Example:

```csv
2026-04-10T09:18:41Z,R00087,U211,payment-service,/payments,POST,500,1340,eu-central,Timeout
```

---

# Run Instructions

## 1. Request Count by Service

This command counts how many requests belong to each service.

```bash
python mapreduce/mr_job_tasks.py --job request data/sample_data.csv
```

Example output:

```text
auth-service 12121
payment-service 7914
search-service 10616
```

---

## 2. Server Error Count by Service

This command counts the number of server errors where:

```text
status_code >= 500
```

Run:

```bash
python mapreduce/mr_job_tasks.py --job error data/sample_data.csv
```

Example output:

```text
payment-service 814
search-service 690
```

---

## 3. Top 10 Slow Endpoints

This command identifies the endpoints with the highest number of slow requests.

A request is considered slow when:

```text
response_time_ms > 800
```

Run:

```bash
python mapreduce/mr_job_tasks.py --job slow data/sample_data.csv
```

Example output:

```text
payment-service,/payments 512
search-service,/search 438
```

# Ray Extension for Service Degradation Detection

## Environment
- Python 3.10 - 3.12
- Ray 2.55.1+
- Pandas

## Install dependencies
```bash
pip install ray pandas

