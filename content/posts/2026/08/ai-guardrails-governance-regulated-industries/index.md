---
title: "Richmond AWS User Group: AI Guardrails and Governance for Regulated Industries"
date: 2026-08-13T19:00:00-04:00
draft: true
tags: ["AWS", "AI", "Bedrock", "Security", "Compliance", "governance", "Enterprise"]
categories: ["engineering"]
description: "Notes from my Richmond AWS User Group presentation on AI guardrails and how I approach designing governance strategies for AI in regulated industries."
cover:
    image: "cover.png"
    alt: "Title card: AI Guardrails and Governance for Regulated Industries, a Richmond AWS User Group talk"
    relative: true
hero:
    style: "card"
    color: "talk"
    label: "Talk · Richmond AWS User Group"
    title: "AI Guardrails and Governance for Regulated Industries"
    ghost: "Guardrails"
    chip: "Aug 2026"
---

On August 13th I presented at the Richmond AWS User Group on AI guardrails, focused on how I approach designing governance strategies for AI in regulated industries. This is a topic I spend a lot of my time on, and it was good to step back from the day-to-day and talk through the patterns that keep coming up.

It was good to be back in front of this group after the [FastMCP demo]({{< relref "/posts/2026/02/richmond-aws-user-group-fastmcp" >}}) earlier this year.

<!-- TODO(Luke): anything about the audience or turnout worth mentioning -->

## The Problem Isn't the Model

I started from the same observation I keep coming back to: everyone can demo generative AI, but almost no one can run it safely in production.

In regulated industries, that gap usually isn't technical. The models are capable. The demo looks great. Then someone from Legal or Compliance asks a reasonable question. What happens if it leaks customer data? What if it says something that sounds like advice we're not allowed to give? What if a user talks it into ignoring its instructions?

If the team doesn't have good answers, the project stalls. Not because the technology isn't ready, but because the governance layer isn't there.

That's the layer the talk was about.

## Guardrails Wrap the Invocation

The core mental model I shared is simple: guardrails wrap the model invocation, not the model itself.

You don't try to make the model perfectly safe on its own. You put a policy layer between your application and the model, and every prompt and every response gets evaluated against those policies before anything reaches a user.

That means two evaluation passes:

**Input evaluation** happens before the prompt ever reaches the model. If a request violates a policy, like an attempted prompt injection or a question in a denied topic area, the model never sees it.

**Output evaluation** happens after the model responds. A response can pass the input check and still fail on the way out, because it surfaced sensitive data from retrieved context or drifted away from what the source documents actually say.

I went deeper into how this works on AWS in [The Missing Layer in Your Enterprise AI Stack]({{< relref "/posts/2026/02/the-missing-layer-in-your-enterprise-ai-stack-aws-bedrock-guardrails" >}}), including content filters, denied topics, PII redaction, and contextual grounding checks in Amazon Bedrock Guardrails.

## Defense in Depth

A point I tried to drive home is that guardrails are one layer, not the whole strategy. In regulated environments you want defense in depth.

That looks like private model access with no public internet exposure. IAM-first access control tied to your enterprise identity. Input handling that sanitizes prompts and attaches metadata about who sent them and why. Output filtering. And an audit trail that records what happened without storing raw sensitive data.

Each layer catches things the others miss. None of them is enough on its own. I laid out a full reference architecture for this in [From Prompt to Production]({{< relref "/posts/2026/02/prompt-to-production-safe-genai-aws" >}}), and a lot of the talk walked through the thinking behind it.

## Governance Is a Design Problem

The part of the talk I care about most is that governance has to be designed in from the start. It's not a checklist you run through the week before launch.

When I work on governance strategies for AI in regulated industries, a few principles keep showing up:

**Centralize the policy.** One guardrail definition applied consistently across every application and every model call. If every team writes its own safety logic, you end up with inconsistent behavior and nothing your governance team can review.

**Version it like code.** Policies change. You should be able to test a new version, promote it deliberately, and know exactly which version was running at any point in time.

**Make it observable.** A guardrail that blocks things quietly is only half useful. You need to know what was blocked, when, and why, both for incident response and for the conversation with auditors.

**Keep it model-agnostic.** Most organizations won't standardize on a single model forever. Your safety policies shouldn't need to be rewritten every time the underlying model changes.

**Bring compliance in early.** The fastest path to production is getting risk and compliance partners involved while you're still designing, not after the demo.

<!-- TODO(Luke): a specific example or pattern from your work you're comfortable sharing publicly (no client names) -->

## What I Heard Back

<!-- TODO(Luke): a question from the audience that stuck with you, or themes from the Q&A -->

The broader takeaway I left people with: the future of AI in regulated industries isn't about fancier demos. It's about building trust. Organizations that treat AI like enterprise infrastructure, secured, monitored, audited, and governed, are the ones that will actually get it into production.

## Thank You

<!-- TODO(Luke): thank the organizers / hosts -->

Thanks to everyone who came out and engaged with the material. These conversations are how the patterns get better.

If your team, meetup, or conference would like a session on AI guardrails or governance for regulated environments, connect with me on [LinkedIn](https://www.linkedin.com/in/lucaslittle/). I'm always glad to talk about this stuff.
