# Cloud Service Log Analytics

Mini-project for cloud-based log analytics using **MapReduce** and **Ray** in Python.

This project analyses a synthetic cloud service log dataset and demonstrates:

- MapReduce batch analytics using `mrjob`
- Parallel degraded-service detection using `Ray`
- Cloud-style log processing workflows

---

# Project Overview

The system processes cloud service logs containing:

- service names
- endpoints
- HTTP status codes
- response times
- error types

Two processing approaches are implemented:

## MapReduce Analytics
Implemented using the `mrjob` framework.

Tasks:
- Request count by service
- Server error count by service
- Top 10 slow endpoints

## Ray Extension Analytics
Implemented using `Ray` parallel tasks.

Task:
- Degraded service detection based on:
  - high slow-request rate
  - high server-error rate
  - repeated timeout errors

---

# Project Structure

```text
COMP3041J-cloud-project2/
│
├── data/
│   └── sample_data.csv
│
├── mapreduce/
│   └── mr_job_tasks.py
│
├── ray/
│   ├── ray_extension.py
│   ├── dummy_test.csv
│   └── validation_result.txt
│
├── outputs/
│   ├── output_request.txt
│   ├── output_error.txt
│   ├── output_slow.txt
│   └── output_ray.txt
│
├── screenshot/
│   ├── request.png
│   ├── error_and_slow.png
│   └── ray.png
│
├── data_loader.py
├── .gitignore
├── .env
└── README.md
```

---

# Folder Description

| Folder/File | Description |
|---|---|
| `data/` | Input cloud service log dataset |
| `mapreduce/` | MapReduce analytics implementation using `mrjob` |
| `ray/` | Ray-based degraded-service detection |
| `outputs/` | Generated analytics outputs |
| `screenshot/` | Execution screenshots for validation |
| `data_loader.py` | Shared dataset loading utility |

---

# Environment Requirements

- Python 3.10 – 3.12
- `mrjob`
- `ray`
- `pandas`

Install dependencies:

```bash
pip install mrjob ray pandas
```

---

# Dataset

Input dataset:

```text
data/sample_data.csv
```

Each record contains fields such as:

```text
timestamp
request_id
user_id
service_name
endpoint
http_method
status_code
response_time_ms
region
error_type
```

Example record:

```csv
2026-04-10T09:18:41Z,R00087,U211,payment-service,/payments,POST,500,1340,eu-central,Timeout
```

---

# MapReduce Analytics

Implemented in:

```text
mapreduce/mr_job_tasks.py
```

---

## 1. Request Count by Service

Counts how many requests belong to each service.

Run:

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

Counts records where:

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

Detects endpoints with the highest number of slow requests.

Condition:

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

---

# Ray Extension Analytics

Implemented in:

```text
ray/ray_extension.py
```

The Ray extension performs degraded-service detection using parallel processing.

A service is considered degraded if it satisfies at least one condition:

- slow request rate > 20%
- server error rate > 10%
- at least 5 Timeout errors

Run:

```bash
python ray/ray_extension.py
```

Example output:

```text
payment-service, high server error rate
search-service, high slow request rate
order-service, repeated timeout errors
```

---

# Outputs

Generated output files are stored in:

```text
outputs/
```

Files include:

- `output_request.txt`
- `output_error.txt`
- `output_slow.txt`
- `output_ray.txt`

---

# Validation

Execution screenshots and validation results are included for verification purposes.

Validation artefacts:

- `screenshot/request.png`
- `screenshot/error_and_slow.png`
- `screenshot/ray.png`
- `ray/validation_result.txt`

---

# Technologies Used

- Python
- mrjob
- Ray
- Pandas
- GitHub

---

# Project Workflow

```text
Dataset
   ↓
MapReduce Analytics
   ↓
Ray Parallel Analytics
   ↓
Validation and Comparison
```