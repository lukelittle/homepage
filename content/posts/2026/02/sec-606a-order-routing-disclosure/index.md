---
title: "Deterministic Order Routing Disclosure Reporting (SEC Rule 606(a))"
slug: "sec-606a-order-routing-disclosure"
date: 2026-02-20T09:00:00-05:00
draft: true
tags: ["batch-processing", "aws", "serverless", "regulatory-tech", "sec", "finra", "compliance", "data-engineering", "reporting", "broker-dealer"]
categories: ["engineering"]
series: ["Regulated Markets on AWS"]
description: "How to build a deterministic, reproducible quarterly batch pipeline on AWS for SEC Rule 606(a) order routing disclosure, and why routing transparency matters in the payment for order flow debate"
aliases:
  - /posts/2026/02/building-a-batch-processing-system-for-sec-rule-606a-order-routing-disclosure/
cover:
    image: "sec-606a-order-routing-disclosure.png"
    alt: "Architecture diagram showing a quarterly batch pipeline on AWS for SEC Rule 606(a) order routing reports"
---

<!-- TODO(Luke): repo still uses pre-2018 categories; update repo -->

## Introduction

When you tap "buy" in a zero-commission brokerage app, your order doesn't go straight to the New York Stock Exchange. Your broker decides where to send it: an exchange, an alternative trading system, or, very often for retail market orders, a wholesale market maker that pays the broker for the privilege of filling it. That payment is called **payment for order flow (PFOF)**, and it's one of the most argued-about business models in U.S. equity markets.

The debate got loud in early 2021, when meme-stock trading put retail order routing on the front page and in front of Congress. Supporters argue that PFOF funds commission-free trading and that wholesalers often give retail orders better prices than the exchanges' displayed quotes. Critics argue that it creates a conflict of interest: a broker that gets paid more by one venue has a reason to send orders there even if another venue would do better for the customer. I'm not going to settle that argument here. What I want to look at is the piece of regulation that makes the argument possible in the first place: **SEC Rule 606(a)**, which requires broker-dealers to publish, every quarter, where they route customer orders and how much they get paid for doing it.

From an engineering point of view, 606(a) is an interesting contrast to the real-time controls earlier in this series. It's not a millisecond problem. It's a "produce the same correct answer every time someone asks, and prove it" problem. This post walks through what the rule requires, a batch architecture on AWS that fits it, and a hands-on demo you can run yourself.

## What Rule 606 Requires

### A Short History

The SEC first adopted order routing disclosure in November 2000 as Rule 11Ac1-6 (Release No. 34-43590), alongside the execution quality reports that became Rule 605. When Regulation NMS was adopted in 2005, the rule was renumbered as Rule 606 of Regulation NMS (17 CFR 242.606).

In November 2018, the SEC substantially amended the rule in Release No. 34-84528, "Disclosure of Order Handling Information." The amendments made the quarterly public report more detailed, focused it on held orders, added a new customer-requested report for not-held institutional orders, and required reports to be published in a standard XML schema with an associated PDF renderer. Broker-dealers began producing reports in the new format in 2020.

<!-- TODO(Luke): verify the exact compliance date for the amended 606(a)(1) reports (the release set 180 days after Federal Register publication; I believe the SEC later extended it to January 1, 2020) -->

If you find an older article (including earlier drafts of this one) describing 606 reports as "market orders vs. limit orders, NMS stocks vs. options," that's the pre-2018 version of the rule.

### The Quarterly Public Report: Rule 606(a)(1)

Today, every broker-dealer must make a report publicly available for each calendar quarter covering its routing of **non-directed orders**, meaning orders where the customer didn't tell the broker which venue to use. The key requirements:

- **Scope**: non-directed orders in NMS stocks that are submitted on a **held** basis (the typical retail order, where the broker is expected to execute immediately), plus non-directed customer orders in NMS securities that are option contracts.
- **Monthly breakdown**: the quarterly report is broken down by calendar month.
- **Three sections**: one for **S&P 500 stocks** (as of the first day of the quarter), one for **other NMS stocks**, and a separate section for **options**.
- **Four order types**: market orders, marketable limit orders, non-marketable limit orders, and other orders.

Each section has to include:

1. The percentage of total orders that were non-directed, and the split of non-directed orders across the four order types.
2. The top ten venues by number of non-directed orders routed, plus any venue that received 5% or more, with the percentage of total non-directed orders and the percentage of each order type routed to that venue.
3. For each of those venues, the **net aggregate amount** of payment for order flow received, payment from any profit-sharing relationship, transaction fees paid, and transaction rebates received, broken out by order type, both as a total dollar amount and per share. The SEC's XML schema expresses the per-share figure as net cents per hundred shares, and the SEC staff's Rule 606 FAQ says options should be reported in net cents per option contract.
4. A narrative discussion of the **material aspects** of the broker's relationship with each venue, including any PFOF or profit-sharing arrangement and terms that may influence routing decisions, such as volume thresholds, tiered payment schedules, or minimum order flow commitments.

The report must be posted within **one month after the end of the quarter**, and it must stay on a free, publicly accessible website for **three years** from the date it was first posted.

That third bullet is where the PFOF debate becomes concrete. Before 2018, a broker could say in prose that it received payment for order flow. Now it has to publish the dollars, per venue and per order type, in a machine-readable format anyone can download and compare.

### 606(a) Isn't the Whole Rule

Rule 606 has other parts. Rule 606(b)(1) requires brokers to tell a customer, on request, where that customer's orders were routed over the previous six months. The 2018 amendments added Rule 606(b)(3), which requires a much more detailed report, on customer request, about the handling of **not-held** NMS stock orders (the kind institutions typically send to an algorithmic trading desk), including fill rates, fees and rebates, and midpoint executions by venue. That report is customer-specific rather than public, and it's a different data problem. This post and the demo focus only on the public 606(a) report.

## Routing Disclosure vs. Best Execution

<!-- TODO(Luke): the 5310 post is still a draft; make sure it's published (or drop the link) before publishing this one. -->

It's easy to confuse 606(a) with best execution, which is covered by FINRA Rule 5310 (which I wrote about [earlier in this series](/posts/2026/02/finra-5310-best-execution-monitor/)). They're related but they answer different questions:

| | Rule 606(a) | FINRA Rule 5310 |
|---|---|---|
| Question | Where did orders go, and what did the broker get paid? | Did the broker use reasonable diligence to get the best market for the customer? |
| Audience | The public | The firm and its regulators |
| Cadence | Quarterly report, monthly breakdown | Ongoing obligation, typically met with periodic "regular and rigorous" reviews of execution quality |
| Natural architecture | Scheduled batch | Batch or near-real-time analytics, depending on the firm |

Disclosure tells you **where** orders went and what incentives existed. Best execution asks **how well** they were handled. A broker can be fully compliant with 606(a), publishing every penny of PFOF, and still have to defend its routing under 5310. That's why the two obligations drive different system designs.

## Why Batch Processing?

Once you read the rule closely, the architecture almost picks itself.

**The timing is fixed.** The report covers a closed calendar quarter and is due a month later. There's no business value in updating it every second.

**The dataset is bounded.** Every run processes a complete quarter with a clear start and end. That's the textbook case for batch.

**The answer must be reproducible.** If a regulator or an auditor asks how you produced the Q1 numbers, you need to be able to rerun Q1 and get the same answer. Batch jobs that take explicit parameters (year, quarter, input version, code version) are much easier to make deterministic than a streaming system with running state.

**It's cheap.** Compute runs a few times a year. Nothing needs to be always-on.

## Architecture Overview

The demo uses AWS serverless services and Terraform:

```
EventBridge (quarterly schedule)
    ↓
Step Functions (orchestration)
    ↓
AWS Batch on Fargate (Python / pandas container)
    ↓
S3 (report artifacts)  +  DynamoDB (run metadata table)
```

### Why These Components

**AWS Batch on Fargate, not Lambda.** To be honest, the synthetic dataset in the demo (10,000 orders per quarter by default) would run comfortably in a Lambda function, which now supports up to 10 GB of memory. The job definition asks for just 0.25 vCPU and 512 MB, and that's plenty for the demo. I chose Batch for two other reasons. First, Lambda has a hard 15-minute timeout, and a real broker-dealer's quarter can contain hundreds of millions of orders, so the runtime isn't something I want capped. Second, the same container image runs on my laptop and in AWS, so there's one code path. If the data grows, you change the vCPU and memory in the job definition, not the architecture.

**Step Functions, not Airflow.** One job, four times a year, doesn't justify running an Airflow cluster. Step Functions gives you a managed workflow with an execution history and error handling for effectively nothing.

**DynamoDB for run metadata.** The table is pay-per-request and keyed by `run_id`, with a secondary index on `year_quarter` so you can list every run for a given quarter.

**S3 for artifacts.** The Terraform enables versioning, default server-side encryption, a public access block, and a lifecycle rule.

<!-- TODO(Luke): the repo's batch/job.py writes outputs with local file I/O and never writes to S3 or DynamoDB (boto3 is imported but unused; s3fs isn't in requirements.txt), and the Step Functions "RecordMetadata" state is a Pass state. The AWS path likely doesn't work end to end yet. Fix the repo, or soften this section further. -->

<!-- TODO(Luke): the EventBridge target in terraform/modules/step_functions passes the literal string "$.time" for year and quarter instead of using an input transformer to compute the previous quarter; scheduled runs will fail validation. Fix in repo. -->

## Key Implementation Details

### Determinism and Reproducibility

If an auditor asks to see Q1 2024 again, "close enough" isn't an answer. The demo takes a few steps toward making reruns reproducible.

**Explicit parameters.** The batch job takes `--year`, `--quarter`, `--input`, and `--output`. There's no hidden "current date" logic in the aggregation itself; the quarter is filtered from each order's received timestamp.

**Immutable, per-run output paths.** Step Functions uses the execution name as the run ID and writes each run to its own prefix:

```
s3://<bucket>/reports/
  year=2024/
    quarter=Q1/
      <run_id>/      # first run
      <run_id>/      # rerun, previous output preserved
```

Nothing is overwritten. A rerun is a new directory, so you always keep the history of what was published and what was regenerated.

**Code version in every run.** The Dockerfile takes a `GIT_COMMIT` build argument and exposes it as an environment variable, which the job records in its metadata:

```python
metadata = {
    'run_id': self.run_id,
    'run_timestamp': self.run_timestamp,
    'year': self.year,
    'quarter': self.quarter,
    'total_rows_processed': total_rows,
    'input_dataset_version': input_version,
    'code_version': os.getenv('GIT_COMMIT', 'unknown')
}
```

This is written as `run_metadata.json` next to the report outputs, so each report carries its own lineage: which code, which quarter, how many rows.

<!-- TODO(Luke): input_dataset_version is hardcoded to "v1" in the repo and Step Functions always reads data/orders.csv, so input versioning is a placeholder today. Either implement versioned inputs in the repo or keep describing it as future work. -->

In a production system you'd go further: pin the input to an immutable object version or a content hash, record checksums of the outputs, and make the S3 bucket write-once (for example with Object Lock). The pattern is the same: every published number should trace back to a specific input, a specific commit, and a specific run.

### The Aggregation Logic

Here's the heart of the demo's `compute_aggregations`, lightly trimmed. It groups non-directed orders by month and security type, then computes each venue's share of total, market, and limit orders:

```python
for (month, security_type), month_df in df.groupby(['month', 'security_type']):
    total_orders = len(month_df)
    total_market = len(month_df[month_df['order_type'] == 'MARKET'])
    total_limit = len(month_df[month_df['order_type'] == 'LIMIT'])

    for venue, venue_df in month_df.groupby('route_venue'):
        venue_order_count = len(venue_df)
        venue_market_count = len(venue_df[venue_df['order_type'] == 'MARKET'])
        venue_limit_count = len(venue_df[venue_df['order_type'] == 'LIMIT'])

        pct_total = (venue_order_count / total_orders * 100) if total_orders > 0 else 0
        pct_market = (venue_market_count / total_market * 100) if total_market > 0 else 0
        pct_limit = (venue_limit_count / total_limit * 100) if total_limit > 0 else 0
```

The job then renders the same aggregates as CSV (`monthly_summary.csv`), nested JSON (`quarterly_summary.json`), and a human-readable HTML report. The unit tests check that venue percentages sum to 100 within each month and security type, and that running the aggregation twice on the same input produces identical results.

This is deliberately simple, and it's worth being clear about the gap. The demo uses the **pre-2018** categories: two security types (`NMS_STOCK`, `OPTION`), two order types (`MARKET`, `LIMIT`), and routing percentages only. To produce a current 606(a)(1) report, the input and the grouping would need to grow:

```python
# What the current rule needs (not yet in the demo repo)
SECTIONS    = ["SP500_STOCK", "OTHER_NMS_STOCK", "OPTION"]
ORDER_TYPES = ["MARKET", "MARKETABLE_LIMIT", "NON_MARKETABLE_LIMIT", "OTHER"]

# Additional input fields per routed order:
#   held_flag         -> NMS stock orders are in scope only if held
#   in_sp500          -> S&P 500 membership as of the first day of the quarter
#   marketable_at_route -> limit order marketability, assessed when routed
#   pfof_usd, profit_share_usd, fees_paid_usd, rebates_usd

# Per (month, section, venue, order_type), report:
#   pct of non-directed orders, net PFOF / profit sharing / fees / rebates
#   in total dollars and in cents per hundred shares (per contract for options)
```

A few of those fields are harder than they look. Marketability has to be determined for each order the broker routes, which the SEC staff FAQ says can be assessed at the time of routing, so you need the prevailing quote at the routing timestamp. S&P 500 membership has to be frozen as of the first day of the quarter, which is a classic reproducibility trap: if you join against today's index membership, rerunning last year's report will quietly change the answer. And the payment figures usually come from billing and invoicing systems, not the order management system, so the pipeline has to join two very different data sources and reconcile them.

### Reading the Report: Where PFOF Shows Up

Routing percentages on their own tell part of the story. The interesting signal is when a venue's share of one order type is very different from its share of the others. Here's an illustrative (synthetic) row from the S&P 500 section for one month:

```
Venue: Wholesaler A
  % of non-directed orders:                 45.0%
  % of market orders:                       60.0%
  % of marketable limit orders:             55.0%
  % of non-marketable limit orders:         20.0%
  Net PFOF received (market orders):        $X total, Y cents per hundred shares
```

This pattern, where marketable orders go disproportionately to one wholesaler while resting limit orders go elsewhere, is common in retail brokerage reports, and it's exactly what the PFOF columns and the "material aspects" narrative exist to explain. It doesn't prove anyone did anything wrong; wholesalers can and often do execute marketable retail orders at prices better than the national best bid or offer. But it tells readers where to look, and it gives researchers and journalists the data to compare brokers against each other.

Note that the counterparty here is a wholesaler, not an exchange. In equities, exchanges generally don't pay for order flow in this sense (options markets are different; some options exchanges have their own payment for order flow programs). Equity exchanges typically charge access fees for taking liquidity and pay rebates for providing it, and 606(a) reports those as separate line items (transaction fees paid and transaction rebates received) alongside PFOF.

<!-- TODO(Luke): the repo's synthetic data generator (tools/generate_synthetic_data.py) models PFOF bias by routing market orders to "BATS", an exchange. Rename to a wholesaler (e.g. "WHOLESALER_A") and add PFOF/fee/rebate fields so the repo matches this section. -->

### Data Governance

A regulatory report is only as trustworthy as the trail behind it. The demo's audit trail for each run is:

1. The Step Functions execution record, with full execution data logged to CloudWatch.
2. The Batch job's container logs in CloudWatch.
3. `run_metadata.json` stored with the outputs, plus a DynamoDB table provisioned for run metadata.
4. The report artifacts themselves, under an immutable per-run prefix.

The S3 lifecycle rule moves objects to Glacier after 90 days and expires them after seven years:

```hcl
transition {
  days          = 90
  storage_class = "GLACIER"
}

expiration {
  days = 2555  # 7 years
}
```

It's worth separating two different retention questions here. The rule's **three-year** requirement is about the public report staying posted on a website. The seven years in the demo is an internal retention choice for the underlying artifacts. Your firm's actual record-retention schedule is a question for compliance, not for a Terraform comment.

<!-- TODO(Luke): verify whether a specific books-and-records rule (e.g. 17a-4) should be cited for internal retention, or leave the seven years framed as a demo choice. -->

## Try It Yourself

The complete demo is in the [sec-606a-order-routing-disclosure-example](https://github.com/lukelittle/sec-606a-order-routing-disclosure-example) repository. You can run the whole pipeline locally without an AWS account:

```bash
pip install -r requirements.txt

# Generate a synthetic quarter of orders
python tools/generate_synthetic_data.py --year 2024 --quarter 1

# Run the report
make local-quarter YEAR=2024 Q=1

# Open the HTML report
open dist/disclosure_report.html
```

To deploy the infrastructure, `cd terraform/envs/dev`, run `terraform init` and `terraform apply`, then trigger a run with `aws stepfunctions start-execution` and an input of `{"year": 2024, "quarter": 1}`. The repo's `docs/` folder walks through each step, and the README estimates the dev environment at a dollar or two a month. Remember to `terraform destroy` when you're done.

### Suggested Exercises

1. **Upgrade to the current rule.** Split NMS stocks into S&P 500 and other NMS stocks, add the four order types, and filter stock orders to held orders only.
2. **Add the money.** Extend the synthetic data with PFOF, fees, and rebates per order, and report net amounts in total dollars and cents per hundred shares.
3. **Freeze reference data.** Add an S&P 500 membership snapshot keyed by quarter start date, and write a test proving that a rerun uses the snapshot, not current membership.
4. **Close the AWS loop.** Write the outputs to S3 and the metadata to DynamoDB from the batch job, and compute the previous quarter from the EventBridge event time.
5. **Emit the XML.** Download the SEC's published Rule 606 XML schema and generate a report that validates against it.

## Why This Matters for Students

It's tempting to think the interesting distributed systems work is all in streaming. This project is a good counterweight. It teaches:

1. **Matching architecture to requirements**: a quarterly, bounded, public report is a batch problem, and pretending otherwise adds cost and risk.
2. **Determinism as a design goal**: explicit parameters, immutable outputs, and recorded code versions are what make a rerun trustworthy.
3. **Reference data discipline**: point-in-time joins (like index membership) are where reproducibility quietly breaks.
4. **Reading regulation as a spec**: the rule text defines the schema. Sections, order types, and units all fall straight out of 17 CFR 242.606.
5. **Infrastructure as code**: the whole environment comes up and goes away with Terraform.

And it connects to a live public policy debate. Once you've built a 606 report, you can go read real brokers' reports and understand exactly what they're telling you.

## Conclusion

Rule 606(a) is the reason the payment for order flow debate has data behind it. Since the 2018 amendments, broker-dealers publish, quarter by quarter and month by month, which venues received their customers' held orders, broken down by S&P 500 stocks, other NMS stocks, and options, across four order types, along with the net payments, fees, and rebates attached to each venue.

Engineering-wise, it's a reminder that not every problem is a real-time problem. A scheduled batch job with explicit inputs, immutable outputs, and a recorded code version is simpler, cheaper, and easier to defend than a streaming system for something that's published four times a year. The demo is a simplified starting point that still uses the older report categories, and the gap between it and the current rule is itself a good lesson in how much detail hides inside a single paragraph of regulation.

The next time you see "commission-free trading," go find that broker's 606 report and see where the orders really go.

## Sources and Further Reading

### Primary Regulatory Sources

1. **Disclosure of Order Handling Information (2018 amendments)**
   Securities and Exchange Commission, Release No. 34-84528 (November 2, 2018)
   [https://www.sec.gov/files/rules/final/2018/34-84528.pdf](https://www.sec.gov/files/rules/final/2018/34-84528.pdf)

2. **Disclosure of Order Execution and Routing Practices (original adopting release)**
   Securities and Exchange Commission, Release No. 34-43590 (November 17, 2000)
   [https://www.sec.gov/rule-release/34-43590](https://www.sec.gov/rule-release/34-43590)

3. **Code of Federal Regulations: 17 CFR § 242.606**
   [https://www.law.cornell.edu/cfr/text/17/242.606](https://www.law.cornell.edu/cfr/text/17/242.606)

4. **SEC Division of Trading and Markets: Responses to Frequently Asked Questions Concerning Rule 606 of Regulation NMS**
   [https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions/faq-rule-606-regulation](https://www.sec.gov/rules-regulations/staff-guidance/trading-markets-frequently-asked-questions/faq-rule-606-regulation)

5. **Regulation NMS Adopting Release**
   Securities and Exchange Commission, Release No. 34-51808 (June 9, 2005)
   [https://www.sec.gov/rule-release/34-51808](https://www.sec.gov/rule-release/34-51808)

6. **FINRA Rule 5310: Best Execution and Interpositioning**
   [https://www.finra.org/rules-guidance/rulebooks/finra-rules/5310](https://www.finra.org/rules-guidance/rulebooks/finra-rules/5310)

### Demo Repository

7. **sec-606a-order-routing-disclosure-example**
   [https://github.com/lukelittle/sec-606a-order-routing-disclosure-example](https://github.com/lukelittle/sec-606a-order-routing-disclosure-example)

---

**Disclaimer**: This blog post and associated demo are for educational purposes only. They do not constitute legal advice, compliance guidance, or investment advice. The architecture described does not represent any former employer's actual systems or implementations. The demo uses synthetic data and a simplified, pre-2018 interpretation of the report format, and it is not intended for production regulatory filing. Real Rule 606 reporting requires the current XML schema, complete order and billing data, legal review, and compliance oversight. Always consult with legal and compliance professionals when building regulatory reporting systems.

*This article is designed to help finance-minded college students learn AWS with real-world examples that bridge technology and financial services.*
