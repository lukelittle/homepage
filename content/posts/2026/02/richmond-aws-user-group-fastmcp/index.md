---
title: "Richmond AWS User Group: FastMCP Demo on AWS"
date: 2026-02-05T19:00:00-05:00
draft: false
tags: ["AWS", "FastMCP", "AI Agents", "AWS User Group", "Richmond", "Model Context Protocol", "Discogs"]
cover:
    image: "richmond-aws-user-group-fastmcp-demo.jpeg"
    alt: "Richmond AWS User Group - FastMCP Demo"
    caption: "Richmond AWS User Group: FastMCP Demo on AWS"
---

## Live Demonstration of FastMCP on AWS

The February meetup of the Richmond AWS User Group featured a hands-on demonstration of FastMCP on AWS, exploring how modern agent frameworks can be deployed and operated in real cloud environments. Rather than focusing on theoretical concepts, the session provided attendees with practical insights into what it actually takes to run AI agent frameworks in production.

## Behind the Scenes: Unscripted AI Engineering

What made this demonstration particularly authentic was that I hadn't tested the solution beforehand. Armed with an impressively detailed prompt I'd crafted ([available on GitHub](https://github.com/lukelittle/rawsug-fastmcp-demo/blob/main/prompt.txt)), I wanted to make this a genuinely live experience—including all the potential hiccups and surprises that come with real AI development.

As part of my introduction, I surveyed attendees about their programming language preferences and AI tooling adoption. Interestingly, only about half were currently using agentic coding tools like Kiro or Claude code in their workflows, highlighting the adoption curve many teams are still navigating.

## Going Beyond the Theory

Unlike high-level overviews that often gloss over implementation details, this talk walked through a real working example. I connected an AI agent to my personal record album collection hosted on a website and worked toward building a page where the model could answer specific questions about that collection. This was an evolution of the project I described in my [January article on FastMCP and the Vinyl Collection Chatbot](../../../2026/01/mcp-fastmcp-universal-translator-ai-agents/).

The demo highlighted some important realities of working with AI agents: even with carefully prepared prompts, much of the work involves orchestration, managing component spin-up times, and making adjustments throughout the development process. 

In one of the evening's more memorable moments, I deliberately let Kiro loop for about 45 minutes while attendees engaged in a spirited debate over whether it was stuck or still processing. This unplanned "teachable moment" perfectly illustrated the sometimes opaque nature of these systems and the patience required when working with them. Eventually, we were rewarded with a working solution, but the journey there—with all its uncertainty—was perhaps more valuable than a polished, pre-prepared demo would have been.

This practical perspective gave attendees a clearer understanding of the day-to-day challenges and solutions when working with these technologies.

## The Nuances of Prompt Design

One of the most valuable discussions during the session centered around prompt design. We explored how changing topics mid-prompt can quietly degrade accuracy—not because the system is fundamentally flawed, but because the model is constantly making statistical predictions about what comes next.

Watching these effects play out in real-time reinforced an important lesson: small decisions in prompt design can have compounding effects as system complexity increases. This practical demonstration helped attendees understand the nuanced relationship between prompt structure and system performance.

## Incremental Progress and Real Results

By the end of the session, the agent was successfully answering targeted questions about the album collection. While this represented a relatively simple use case, it effectively demonstrated that effective AI systems are typically built incrementally, with careful attention to:

- Context management
- Structural considerations
- Patience during the iteration process

For professionals working in cloud, security, and related fields, the session underscored that understanding how these systems behave under real-world conditions is just as critical as familiarity with the underlying theory.

## Access to Demo Resources

The code demonstrated during the session is available on GitHub for those who want to explore the implementation details further:
[https://github.com/lukelittle/rawsug-fastmcp-demo](https://github.com/lukelittle/rawsug-fastmcp-demo)

## Community Engagement

Thanks to everyone who attended, asked thoughtful questions, and stayed after for discussions about architecture, AI agents, and practical AWS implementations. Special appreciation goes to Lucas Ward and Devin Veasna for their contributions, and to the entire RAWSUG community for maintaining an environment that's practical, curious, and enjoyable.

As we continue exploring the intersection of AI and cloud technology, these community gatherings provide invaluable opportunities to learn from each other's experiences and collectively advance our understanding of these powerful tools.

## Looking Forward

The Richmond AWS User Group remains committed to delivering practical, hands-on sessions that go beyond marketing slides to show real implementation details. Stay tuned for upcoming meetups that will continue to explore cutting-edge technologies with a focus on practical application.