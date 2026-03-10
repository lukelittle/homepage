---
title: "Building a Batch Processing System for SEC Rule 606(a) Order Routing Disclosure"
slug: "sec-606a-order-routing-disclosure"
date: 2026-02-20T09:00:00-05:00
draft: true
tags: ["batch-processing", "aws", "serverless", "regulatory-tech", "sec", "finra", "compliance", "data-engineering", "reporting", "broker-dealer"]
categories: ["engineering"]
description: "How to design deterministic batch processing systems for regulatory compliance reporting, with a focus on SEC Rule 606(a) order routing disclosure requirements"
cover:
    image: "sec-606a-order-routing-disclosure.png"
    alt: "Architecture diagram showing batch processing system for SEC Rule 606(a) reporting"
---

## Introduction

Financial regulatory reporting presents unique challenges for distributed systems engineers: strict compliance requirements, deterministic processing, complete auditability, and the need for reproducibility. This article explores these challenges through the lens of SEC Rule 606(a), which requires broker-dealers to disclose their order routing practices quarterly.

We'll examine why batch processing is the appropriate architecture for this use case, how to implement deterministic data pipelines, and the key differences between disclosure reporting and real-time trading controls.

## What is SEC Rule 606(a)?

SEC Rule 606(a), part of Regulation NMS, requires broker-dealers to publicly disclose quarterly reports describing how they route non-directed customer orders. The rule aims to provide transparency into potential conflicts of interest, particularly around payment for order flow (PFOF).

### Regulatory Requirements

The rule requires disclosure of:

1. **Venue routing percentages**: Where orders were sent
2. **Order type breakdown**: Market vs limit order distribution
3. **Monthly granularity**: Reports broken down by month within the quarter
4. **Security type separation**: NMS stocks and options reported separately
5. **Material relationships**: Disclosure of PFOF and routing incentives

### Legal Citations

- **17 CFR § 242.606**: [Order routing disclosure requirements](https://www.law.cornell.edu/cfr/text/17/242.606)
- **SEC Release No. 34-43590**: [Adopting release](https://www.sec.gov/rules/final/34-43590.htm)
- **FINRA Rule 5310**: [Best execution obligations](https://www.finra.org/rules-guidance/rulebooks/finra-rules/5310)

## Routing Disclosure vs Best Execution

A critical distinction exists between routing disclosure (606a) and best execution (FINRA 5310):

### Rule 606(a): Transparency
- **Question**: Where were orders routed?
- **Metric**: Routing percentages
- **Frequency**: Quarterly disclosure
- **Architecture**: Batch processing

### FINRA Rule 5310: Performance
- **Question**: Were orders executed well?
- **Metric**: Execution quality (price improvement, fill rates)
- **Frequency**: Continuous obligation
- **Architecture**: Real-time streaming

These are complementary but distinct obligations. Disclosure shows **where** orders went; best execution measures **how well** they were executed. This distinction drives fundamentally different architectural approaches.

## Why Batch Processing?

Rule 606(a) is an ideal candidate for batch processing architecture:

### 1. Regulatory Timing
Reports are due **quarterly**, not real-time. There's no need for streaming infrastructure when the business requirement is "once per quarter."

### 2. Complete Datasets
We process all orders for a complete quarter. Batch processing naturally handles bounded datasets with clear start and end points.

### 3. Deterministic Results
Regulatory reports must be reproducible. Batch processing makes it easier to ensure that re-running the same quarter produces identical results.

### 4. Aggregated Statistics
We're computing percentages over millions of orders. Batch aggregation is more efficient than maintaining running totals in a streaming system.

### 5. Cost Efficiency
No need for expensive, always-on streaming infrastructure. Compute resources are used only when reports are generated.

## Architecture Overview

Our implementation uses AWS serverless services:

```
EventBridge (Quarterly Cron)
    ↓
Step Functions (Orchestration)
    ↓
AWS Batch (Fargate Container)
    ↓
S3 (Reports) + DynamoDB (Metadata)
```

### Component Selection

**AWS Batch on Fargate** (not Lambda):
- Processing may exceed Lambda's 15-minute limit
- Pandas operations need more memory than Lambda provides
- Container approach allows flexible dependencies

**Step Functions** (not Airflow):
- Simple quarterly schedule doesn't justify Airflow overhead
- Native AWS integration
- Built-in error handling and retry logic

**DynamoDB** (not RDS):
- Serverless, pay-per-request pricing
- Perfect for infrequent metadata writes
- Fast queries by run_id or year_quarter

**S3** (obvious choice):
- Durable, versioned storage
- Lifecycle policies for automatic archival
- Native integration with all AWS services

## Determinism and Reproducibility

Regulatory systems must be reproducible. If an auditor asks "show me Q1 2024 again," we must produce identical results.

### Input Versioning

```
s3://bucket/data/
  v1/orders.csv
  v2/orders.csv
```

Each run records which input version was used.

### Output Versioning

```
s3://bucket/reports/
  year=2024/
    quarter=Q1/
      20240401_120000/  # First run
      20240401_150000/  # Re-run
```

Each execution writes to a timestamped directory, preserving history.

### Code Versioning

```python
metadata = {
    'code_version': os.getenv('GIT_COMMIT', 'unknown')
}
```

Container builds inject git commit hash, enabling exact code reproduction.

### Metadata Tracking

```python
{
  "run_id": "20240401_120000",
  "run_timestamp": "2024-04-01T12:00:00Z",
  "year": 2024,
  "quarter": 1,
  "input_dataset_version": "v1",
  "total_rows_processed": 1234567,
  "code_version": "abc123def456"
}
```

Every execution is fully traceable.

## The Aggregation Logic

The core of 606(a) reporting is computing routing percentages:

```python
# Filter non-directed orders only
filtered = df[
    (df['directed_flag'] == False) &
    (df['security_type'].isin(['NMS_STOCK', 'OPTION']))
]

# Group by month, security type, and venue
for (month, sec_type), month_df in filtered.groupby(['month', 'security_type']):
    total_orders = len(month_df)
    total_market = len(month_df[month_df['order_type'] == 'MARKET'])
    total_limit = len(month_df[month_df['order_type'] == 'LIMIT'])
    
    for venue, venue_df in month_df.groupby('route_venue'):
        venue_count = len(venue_df)
        venue_market = len(venue_df[venue_df['order_type'] == 'MARKET'])
        venue_limit = len(venue_df[venue_df['order_type'] == 'LIMIT'])
        
        # Calculate percentages
        pct_total = (venue_count / total_orders) * 100
        pct_market = (venue_market / total_market) * 100
        pct_limit = (venue_limit / total_limit) * 100
```

### Detecting PFOF Bias

Disproportionate routing of market orders can indicate PFOF influence:

```
Venue: BATS
  % of Total Orders: 45.0%
  % of Market Orders: 60.0%  ← Disproportionately high
  % of Limit Orders: 30.0%   ← Disproportionately low
```

This pattern suggests market orders are preferentially routed to BATS, possibly due to payment for order flow.

## Data Governance

### Audit Trail

Every execution creates:
1. Step Functions execution record
2. CloudWatch log streams
3. DynamoDB metadata entry
4. S3 output artifacts

### Retention Policy

```hcl
lifecycle_rule {
  transition {
    days = 90
    storage_class = "GLACIER"
  }
  
  expiration {
    days = 2555  # 7 years for regulatory compliance
  }
}
```

### Encryption

- S3: Server-side encryption (AES-256)
- DynamoDB: Encryption at rest
- CloudWatch: Encrypted logs

## Idempotency

Re-running the same quarter is safe:

1. **New output directory**: Each run writes to timestamped path
2. **No destructive operations**: Previous runs preserved
3. **Metadata tracking**: All runs recorded in DynamoDB
4. **Deterministic logic**: Same input → same output

## Observability

### CloudWatch Logs
- Step Functions: Execution history
- Batch Jobs: Container stdout/stderr
- Structured logging for easy querying

### CloudWatch Metrics
- Batch job duration
- Step Functions execution count
- S3 object count
- DynamoDB read/write units

### Alerting
- Job failures trigger SNS notifications
- Execution time anomalies
- Data quality issues

## Cost Optimization

Running this system costs approximately $1-2/month:

- **S3 storage**: ~$0.50/month
- **AWS Batch (quarterly)**: ~$0.10/run
- **DynamoDB (on-demand)**: ~$0.25/month
- **Step Functions**: ~$0.025/run

### Optimization Strategies

1. **Fargate Spot**: 70% cost savings for batch jobs
2. **S3 Lifecycle**: Automatic archival to Glacier
3. **DynamoDB On-Demand**: Pay only for actual usage
4. **Right-sized compute**: 0.25 vCPU sufficient for most quarters

## Lessons for Regulatory Systems

### 1. Batch vs Streaming
Not everything needs real-time processing. Match architecture to business requirements.

### 2. Determinism is Critical
Reproducibility isn't optional in regulatory systems. Design for it from day one.

### 3. Audit Everything
Every execution must be fully traceable. Metadata is as important as the report itself.

### 4. Version Everything
Input data, code, and outputs must all be versioned for reproducibility.

### 5. Simplicity Wins
Serverless batch processing is simpler and cheaper than complex streaming infrastructure for quarterly reports.

## Contrast with Real-Time Systems

For comparison, a best execution monitoring system (FINRA 5310) would require:

```
Order Flow (Real-Time)
    ↓
Kafka/Kinesis (Streaming)
    ↓
Flink/Spark Streaming (Processing)
    ↓
Time-Series DB (Metrics)
    ↓
Real-Time Dashboard
```

This is fundamentally different because:
- **Latency**: Microseconds vs hours
- **Data volume**: Continuous stream vs bounded batch
- **Complexity**: Event-driven vs scheduled
- **Cost**: Always-on vs on-demand

Choose the right architecture for the right problem.

## Educational Value

This project teaches:

1. **Regulatory context**: Understanding compliance requirements
2. **Batch processing**: Deterministic data pipelines
3. **Infrastructure as Code**: Terraform for reproducible infrastructure
4. **Data governance**: Versioning, lineage, and audit trails
5. **Cloud architecture**: Serverless patterns and cost optimization
6. **System design**: Matching architecture to requirements

## Conclusion

SEC Rule 606(a) order routing disclosure demonstrates that not every data processing problem requires real-time streaming. Batch processing, when matched to appropriate use cases, provides simplicity, cost efficiency, and determinism.

Key takeaways:

- **Match architecture to requirements**: Quarterly reports don't need streaming
- **Determinism enables compliance**: Reproducibility is critical for regulatory systems
- **Serverless reduces complexity**: No infrastructure to manage
- **Audit trails are essential**: Every execution must be traceable
- **Simplicity is valuable**: The simplest architecture that meets requirements is often the best

For graduate students studying distributed systems, this project provides hands-on experience with real-world regulatory requirements, cloud architecture patterns, and the engineering discipline required for compliance systems.

## References

1. **SEC Rule 606**: [17 CFR 242.606](https://www.law.cornell.edu/cfr/text/17/242.606)
2. **SEC Adopting Release**: [Release No. 34-43590](https://www.sec.gov/rules/final/34-43590.htm)
3. **FINRA Best Execution**: [Rule 5310](https://www.finra.org/rules-guidance/rulebooks/finra-rules/5310)
4. **Regulation NMS**: [SEC Overview](https://www.sec.gov/rules/final/34-51808.htm)

## Disclaimer

This article describes a simplified educational implementation using synthetic data. This is not legal advice and is not intended for production regulatory filing. Real-world 606(a) systems require additional complexity, legal review, and compliance oversight.

---

**About the Author**: This educational project was designed for graduate-level computer science students studying distributed systems and cloud architecture.

**Repository**: [sec-606a-order-routing-disclosure-example](https://github.com/lukelittle/sec-606a-order-routing-disclosure-example)

**License**: MIT