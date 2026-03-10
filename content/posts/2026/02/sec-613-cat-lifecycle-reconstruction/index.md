---
title: "Event-Sourced Order Lifecycle Reconstruction (SEC Rule 613 / CAT)"
slug: "sec-613-cat-lifecycle-reconstruction"
date: 2026-02-19T09:00:00-05:00
draft: true
tags: ["streaming", "event-sourcing", "kafka", "spark", "regulatory-tech", "distributed-systems", "aws", "finra", "sec", "broker-dealer", "compliance"]
categories: ["engineering"]
description: "Learn how to reconstruct complete order lifecycles across distributed trading systems using event sourcing, Apache Kafka, and Spark Structured Streaming - inspired by SEC Rule 613 and the Consolidated Audit Trail."
aliases:
  - /posts/2026/02/consolidated-audit-trail-event-sourcing/
cover:
    image: "consolidated-audit-trail-event-sourcing.png"
    alt: "Architecture diagram showing order lifecycle reconstruction with event sourcing"
---

## Introduction

Imagine you're a regulator investigating suspicious trading activity. An order was placed at 9:30 AM, routed to three different exchanges, partially filled, modified twice, and finally canceled at 9:35 AM. How do you reconstruct what actually happened when the data is scattered across dozens of systems?

This is the challenge that the **Consolidated Audit Trail (CAT)** solves for U.S. securities markets. In this post, we'll explore how CAT works, why it matters, and how you can build a simplified version using modern streaming architecture.

## What is the Consolidated Audit Trail?

### The Regulatory Context

In 2012, the Securities and Exchange Commission (SEC) adopted [Rule 613](https://www.sec.gov/about/divisions-offices/division-trading-markets/rule-613-consolidated-audit-trail) under Regulation NMS (National Market System). This rule requires self-regulatory organizations (SROs) to create and maintain a consolidated audit trail that captures the lifecycle of orders across U.S. securities markets.

**Legal citation**: [17 CFR § 242.613](https://www.law.cornell.edu/cfr/text/17/242.613)

### Why Was CAT Needed?

Before CAT, market data was fragmented:
- **Multiple venues**: NYSE, NASDAQ, BATS, IEX, and dozens of other exchanges
- **Hundreds of broker-dealers**: Each with their own systems and formats
- **No unified view**: Regulators couldn't easily track an order across the market

This fragmentation made it difficult to:
- Investigate market events (like the 2010 Flash Crash)
- Detect manipulation or insider trading
- Ensure fair and orderly markets
- Reconstruct what happened during anomalies

### What CAT Captures

CAT requires reporting of:
1. **Customer and order information** for all NMS securities
2. **Order lifecycle events** from inception through execution
3. **Routing information** across venues
4. **Modifications, cancellations, and executions**
5. **Timestamps** with millisecond (or better) precision
6. **Linkage identifiers** to connect related events

## The CAT NMS Plan

The industry's implementation is operated by [CAT NMS, LLC](https://www.catnmsplan.com/), which:
- Receives billions of events daily from market participants
- Maintains [technical specifications](https://www.catnmsplan.com/specifications) for data reporting
- Provides regulatory access to consolidated data
- Enforces data quality standards

[FINRA](https://www.finra.org/rules-guidance/notices/20-31) provides oversight and expects firms to perform comparative reviews and maintain data quality controls.

### Recent Developments

The CAT program continues to evolve. In 2025, the SEC issued an [order to reduce operating costs](https://www.sec.gov/newsroom/press-releases/2025-127-sec-issues-order-reduce-operating-costs-consolidated-audit-trail) while maintaining regulatory effectiveness ([fact sheet](https://www.sec.gov/files/34-104144-fact-sheet.pdf)).

## Understanding Order Lifecycles

### What is an Order Lifecycle?

An order lifecycle is the complete journey of an order from inception to final disposition:

```
sequenceDiagram
    participant Customer
    participant Broker
    participant Exchange1
    participant Exchange2
    
    Customer->>Broker: NEW order<br/>(Buy 100 AAPL @ $185)
    Note over Broker: Assigns order ID
    
    Broker->>Exchange1: ROUTE 60 shares
    Exchange1->>Broker: ACK (accepted)
    Exchange1->>Broker: FILL 60 @ $184.99
    
    Broker->>Exchange2: ROUTE 40 shares
    Exchange2->>Broker: ACK (accepted)
    Exchange2->>Broker: FILL 40 @ $185.01
    
    Note over Broker: Order complete
    Broker->>Customer: Confirmation
```

Each step generates an **event**. These events must be:
- **Linked**: Connected through identifiers
- **Ordered**: Sequenced by event time
- **Complete**: No missing steps
- **Accurate**: Correct prices, quantities, timestamps

### The Distributed Systems Challenge

In real markets:
- Events come from **multiple independent systems**
- **No global clock** (timestamps are approximate)
- **Network delays** cause reordering
- **Systems fail** and retry (creating duplicates)
- **Late events** arrive after initial processing

This is a classic distributed systems problem: how do you reconstruct a coherent story from fragmented, out-of-order, potentially duplicate data?

## Event Sourcing: The Foundation

### What is Event Sourcing?

Event sourcing is a pattern where:
- **State changes are stored as events** (not just current state)
- **Current state is derived** by replaying events
- **Events are immutable** (never modified, only appended)
- **Complete history is preserved** for audit and debugging

### Traditional vs. Event Sourcing

**Traditional (State-Oriented)**:
```
Order Table:
order_id | symbol | qty | filled_qty | status | last_updated
---------|--------|-----|------------|--------|-------------
FOID-123 | AAPL   | 100 | 100        | FILLED | 10:05:23
```

You know the current state, but not how you got there.

**Event Sourcing**:
```
Event Log:
event_id | event_type | order_id | qty | ts_event
---------|------------|----------|-----|----------
E1       | NEW        | FOID-123 | 100 | 10:00:00
E2       | ROUTE      | FOID-123 | 60  | 10:00:15
E3       | FILL       | FOID-123 | 60  | 10:00:18
E4       | ROUTE      | FOID-123 | 40  | 10:00:20
E5       | FILL       | FOID-123 | 40  | 10:00:25
```

You can reconstruct the complete story and derive current state at any point in time.

### Why Event Sourcing for CAT?

1. **Regulatory audit trail**: Regulators need to see what happened, when, and why
2. **Time travel**: Reconstruct state at any point ("What was the order status at 10:00:20?")
3. **Debugging**: Replay events to reproduce issues
4. **Late data handling**: Insert late events and recompute state

## Lifecycle Linkages: Connecting the Dots

### Linkage Identifiers

Events contain IDs that connect them into a lifecycle graph:

```
graph TD
    COID[Customer Order ID<br/>COID-123] --> FOID1[Firm Order ID<br/>FOID-456<br/>NEW 100 shares]
    
    FOID1 --> FOID2[Firm Order ID<br/>FOID-789<br/>Route to NASDAQ]
    FOID1 --> FOID3[Firm Order ID<br/>FOID-790<br/>Route to NYSE]
    
    FOID2 --> RID1[Route ID<br/>RID-001]
    FOID3 --> RID2[Route ID<br/>RID-002]
    
    RID1 --> FILL1[Execution ID<br/>EID-AAA<br/>60 @ $185.10]
    RID2 --> FILL2[Execution ID<br/>EID-BBB<br/>40 @ $185.05]
```

### How Linkages Work

Each event contains identifiers that reference other events:

```json
{
  "event_type": "ROUTE",
  "customer_order_id": "COID-123",
  "firm_order_id": "FOID-789",
  "parent_firm_order_id": "FOID-456",  // Links to parent
  "route_id": "RID-001",
  "venue": "NASDAQ"
}
```

By following these links, we reconstruct the complete lifecycle graph - even when events arrive out of order.

## Streaming Architecture

### System Design

Our simplified CAT implementation uses:

```
graph LR
    A[Event<br/>Generator] --> B[Kafka Topics]
    B --> C[Spark<br/>Streaming]
    C --> D[Linkage<br/>Graph]
    C --> E[Lifecycle<br/>Snapshots]
    C --> F[Exceptions]
    E --> G[S3/Iceberg]
    E --> H[DynamoDB]
```

### Kafka Topics

We use separate topics for different concerns:

- **cat.events.v1**: Raw lifecycle events (NEW, ROUTE, FILL, etc.)
- **cat.linkages.v1**: Parent-child edges
- **cat.lifecycle.v1**: Materialized lifecycle snapshots
- **cat.exceptions.v1**: Data quality violations
- **audit.v1**: Immutable audit trail of corrections

### Spark Structured Streaming

The core processing logic:

```python
# Read events from Kafka
events = spark.readStream \
    .format("kafka") \
    .option("subscribe", "cat.events.v1") \
    .load()

# Deduplicate (idempotency)
unique_events = events.dropDuplicates(["event_id"])

# Apply watermark for late data
watermarked = unique_events \
    .withWatermark("event_time", "30 seconds")

# Build linkages
linkages = watermarked.flatMap(construct_edges)

# Materialize lifecycles
lifecycles = watermarked \
    .groupBy("customer_order_id") \
    .agg(materialize_lifecycle)

# Validate data quality
exceptions = lifecycles.flatMap(validate_lifecycle)
```

## Handling Late and Out-of-Order Events

### The Late Data Problem

Events can arrive late due to:
- Network delays
- System failures and retries
- Clock skew between systems
- Batch processing delays

### Watermarks

A **watermark** is a threshold: "I don't expect events older than X seconds anymore."

```
Current time: 10:05:00
Watermark delay: 30 seconds
Watermark: 10:04:30

Events with event_time < 10:04:30 are "late"
```

### Reconciliation

When a late event arrives:
1. **Detect**: Event timestamp is before watermark
2. **Retrieve**: Get existing lifecycle state
3. **Recompute**: Replay all events including late one
4. **Audit**: Log the correction
5. **Update**: Emit corrected lifecycle snapshot

This ensures correctness even with late-arriving data.

## Data Quality Validation

### Validation Rules

Our system checks for:

- **Sequence violations**: Execution before order receipt
- **Missing linkages**: Fill references unknown route
- **Quantity violations**: Filled more than ordered
- **Temporal anomalies**: Events with impossible timestamps
- **Orphaned events**: Events with no parent

### Exception Handling

When violations are detected:

```json
{
  "exception_type": "FILL_BEFORE_NEW",
  "severity": "ERROR",
  "customer_order_id": "COID-123",
  "description": "Execution timestamp precedes order timestamp",
  "ts_detected": 1710000030000
}
```

Exceptions are written to a dedicated topic for investigation.

## Try It Yourself

### Local Quickstart

```bash
# Clone the repository
git clone https://github.com/lukelittle/sec-613-cat-lifecycle-reconstruction-example
cd sec-613-cat-lifecycle-reconstruction-example

# Start local environment
cd local
docker-compose up -d

# Create topics
../tools/create_topics.sh

# Run Spark job
cd ../spark/lifecycle_job
spark-submit lifecycle_streaming.py

# Generate events
cd ../../services/event_generator
python generator.py --mode normal
```

### AWS Deployment

```bash
# Deploy infrastructure
cd terraform/envs/dev
terraform init
terraform apply

# Deploy Spark job
./deploy_spark_job.sh

# Start generator via API
curl -X POST https://YOUR_API_URL/generator/start \
  -d '{"mode": "normal", "duration": 300, "rate": 2.0}'
```

See the [full documentation](https://github.com/lukelittle/sec-613-cat-lifecycle-reconstruction-example/tree/main/docs) for detailed instructions.

## Key Takeaways

1. **CAT solves a real problem**: Reconstructing order lifecycles across fragmented markets
2. **Event sourcing is natural**: Store events, derive state
3. **Linkages enable reconstruction**: Identifiers connect distributed events
4. **Late data is normal**: Watermarks and reconciliation handle it
5. **Data quality matters**: Validation catches errors early
6. **Streaming is powerful**: Real-time processing with exactly-once semantics

## Educational Disclaimer

This project is **for educational purposes only**:
- Simplified version of real CAT concepts
- Synthetic data only
- Not production CAT reporting
- Not legal or compliance advice

Real CAT reporting requires:
- Registration with CAT NMS, LLC
- Adherence to complete technical specifications
- Proper security and data protection
- Qualified compliance personnel

## Sources and Further Reading

### Regulatory Sources
- [SEC Rule 613 Overview](https://www.sec.gov/about/divisions-offices/division-trading-markets/rule-613-consolidated-audit-trail)
- [17 CFR § 242.613 - Legal Text](https://www.law.cornell.edu/cfr/text/17/242.613)
- [CAT NMS Plan Website](https://www.catnmsplan.com/)
- [CAT Technical Specifications](https://www.catnmsplan.com/specifications)
- [FINRA Regulatory Notice 20-31](https://www.finra.org/rules-guidance/notices/20-31)
- [FINRA CAT Oversight](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/cat)
- [SEC 2025 Cost Reduction Order](https://www.sec.gov/newsroom/press-releases/2025-127-sec-issues-order-reduce-operating-costs-consolidated-audit-trail)
- [Cost Control Fact Sheet](https://www.sec.gov/files/34-104144-fact-sheet.pdf)

### Technical Resources
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark Structured Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)

### Project Repository
- [GitHub Repository](https://github.com/lukelittle/sec-613-cat-lifecycle-reconstruction-example)
- [Workshop Documentation](https://github.com/lukelittle/sec-613-cat-lifecycle-reconstruction-example/tree/main/docs)

## About This Project

Created for finance-minded college students to learn AWS with real-world examples. The goal is to teach practical cloud and streaming concepts through regulatory-inspired use cases that bridge technology and financial services.

---

**Ready to build your own lifecycle reconstruction system?** Check out the [full repository](https://github.com/lukelittle/sec-613-cat-lifecycle-reconstruction-example) and workshop materials!

*Content was rephrased for compliance with licensing restrictions. All regulatory sources are cited and linked.*