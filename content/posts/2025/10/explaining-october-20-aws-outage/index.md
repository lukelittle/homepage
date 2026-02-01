---
title: "Learning from the October 20 AWS Outage: Questions Every Team Should Ask"
date: 2025-10-20T09:00:00-05:00
draft: false
tags: ["AWS", "outage", "resilience", "DynamoDB", "DNS", "us-east-1", "architecture"]
categories: ["engineering", "cloud"]
description: "What happened during the October 20 AWS outage, how to communicate impact to leadership, and the critical questions every team should ask about their infrastructure resilience"
cover:
    image: "explaining-october-20-aws-outage.png"
    alt: "Learning from the October 20 AWS Outage"
---

On the morning of October 20, AWS us-east-1 services were degraded—in particular, DNS services for DynamoDB. Most of us didn't find out from monitoring alerts or dashboards. We found out because the apps on our phones stopped working.

That's the reality of modern infrastructure incidents: they often surface as user-facing failures long before the official root cause analysis lands in your inbox.

I wrote about this outage for [Ippon Technologies](https://blog.ippon.tech/explaining-the-october-20-aws-outage-to-leadership/), focusing on three critical aspects that go beyond just understanding what broke:

## What Actually Happened

This wasn't a full region going dark—it was a DNS problem at a foundational layer. DNS (Domain Name System) is the internet's address book. When DNS breaks, everything that depends on it breaks too.

It's like someone removing all the street signs in a city overnight—your services are still there, but nothing can find its way.

For many teams, it meant increased error rates, intermittent failures, and retry storms. Not catastrophic downtime, but the kind of disruption that floods support tickets and frustrates users.

## Having the Leadership Conversation

This is where many engineers struggle. You know the issue was upstream. You know it's AWS's infrastructure. But leadership doesn't care about the cloud provider—they care about impact and what you're doing about it.

The key is framing it as a **dependency visibility problem**, not a blame game:

> "We were affected by a regional outage in AWS's us-east-1 region due to DNS issues. This exposed areas where we're overly dependent on single-region infrastructure. We're using this to map our regional dependencies, prioritize applications by criticality, and identify where we need fallback logic and multi-region routing."

That's ownership. That's a path forward.

## The Hard Questions You Need to Answer

The article explores four critical questions every team should be able to answer confidently:

1. **Which of your apps run in us-east-1?**
2. **Which rely on DynamoDB?**
3. **Which of those are Tier 1 or customer-facing?**
4. **Which of those have active-active failover across regions?**

Most teams can't answer these questions. Not because they're negligent—but because cloud estates grow organically. Services get deployed. Teams change. Documentation drifts. Before you know it, you're running critical workloads on infrastructure patterns that no one fully understands anymore.

## Making Resilience Visible

The full article dives into:

- **Structured risk assessment** using tools like AWS Resilience Hub to define applications and assess risk against RTO/RPO targets
- **Chaos engineering** with AWS Fault Injection Service (FIS) to validate that resilience isn't just theoretical
- **Cultural shifts** to prioritize resilience alongside feature delivery
- **Practical next steps** for mapping dependencies and building observability around failure modes

## Why This Matters

Today's outage wasn't catastrophic—but it was loud enough to get everyone's attention. It revealed real architectural risks that often go unnoticed until they become outages.

Outages like this are reminders, not just disruptions. They're opportunities to begin conversations across architecture, risk, and engineering teams about what resilience really means for your organization.

Not in terms of making everything indestructible, but in making risk visible, decisions intentional, and recovery predictable.

👉 **[Read the full article on the Ippon blog](https://blog.ippon.tech/explaining-the-october-20-aws-outage-to-leadership/)** for detailed guidance on communicating with leadership, assessing your infrastructure, and building measurable resilience practices.

The goal isn't perfection—it's visibility, intention, and readiness for when the next incident inevitably arrives.
