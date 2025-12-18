---
title: "I Tried to Deploy a Simple Website on AWS. It Became a Full-Blown Side Quest."
date: 2025-12-08T09:00:00-05:00
draft: false
tags: ["AWS", "Hugo", "CloudFront", "Terraform", "infrastructure"]
categories: ["engineering"]
description: "I tried to launch a Hugo site on AWS and ended up doing four hours of DNS archaeology and CloudFront forensics."
---

Recently I came across another engineer's personal blog — clean layout, good typography, that "I actually finish my side projects" energy — and it pushed me to finally build one of my own.

I picked Hugo because I like Go, and because using Jekyll in 2025 feels like opting into pain. I briefly considered Ghost, remembered it either requires paying Ghost or hosting Ghost, and closed the tab. And since I'm "the AWS guy," it felt morally necessary to deploy the whole thing on AWS. Maybe I'd even use Kiro if I felt extra fancy.

So I wrote some Terraform, vibe-coded a theme, deployed it, and immediately remembered that I don't build personal websites very often.

---

## First realization: `www` doesn't redirect itself

I wanted `www.lukelittle.com` → `lukelittle.com`.  
Simple enough — except CloudFront doesn't have `.htaccess` or Apache-style rewrite configs.

The fix is a **CloudFront Function** on `viewer-request`:

- check the `Host` header  
- if it equals `www.lukelittle.com`, return a 301 redirect  
- send the user to the apex domain while preserving the URI

In pseudo-JavaScript:

```js
if (host === 'www.lukelittle.com') {
    return {
        statusCode: 301,
        headers: {
            location: { value: 'https://lukelittle.com' + request.uri }
        }
    };
}
```

CloudFront Functions are perfect for this because they run at the edge and don't require a Lambda, bucket change, or origin rewrite.

That part was easy.

---

## Second realization: CloudFront does *not* assume `index.html`

Hugo outputs directories like:

```
/posts/
/posts/index.html
```

Apache and Nginx automatically serve `index.html` when you access `/posts/`.  
CloudFront does not. It will happily 404 unless you rewrite the URI yourself.

So I added a second bit of logic:

```js
if (uri.endsWith('/')) {
    request.uri += 'index.html';
} else if (!uri.includes('.')) {
    request.uri += '/index.html';
}
```

That makes CloudFront behave like a normal web server from 2008. Hugo pages immediately started working.

For a moment.

---

## Where everything went off the rails

I tried to add `www.lukelittle.com` as an alternate domain name on the CloudFront distribution.

CloudFront refused.  
The error claimed it was **already associated with another distribution**.

It wasn't — at least not in any AWS account I currently have access to.

So I did what any rational engineer does:

- Googled  
- Re-Googled  
- Asked ChatGPT  
- Deleted the distribution  
- Recreated the distribution  
- Repeated the cycle  
- Began questioning my past life choices

After four hours, I accepted defeat and temporarily upgraded my support plan.

The answer was unexpected:

`www.lukelittle.com` *was* attached to a CloudFront distribution — in **another AWS account**.

Which account?  
I have no clue.  
Possibilities include:
- some forgotten sandbox from 2017  
- a leftover test account  
- an old attempt at this blog I completely wiped from memory  
- a parallel universe

Support asked me to add a TXT record to prove I owned the domain. I added it in Route 53, they cleared the stale binding, and immediately everything began working exactly as expected.

---

## And now the site actually exists

Despite writing constantly — deep dives, rants, slides, Data Pour episodes — I've never had a single place to put any of it. Everything has been scattered across GitHub repos, Slack threads, LinkedIn posts, and random folders.

This site fixes that.

Hugo prerenders everything.  
CloudFront serves it globally.  
There's no backend.  
No patching.  
No maintenance.  
Just HTML, a CDN, and vibes.

---

## The unexpected benefit

Honestly, getting stuck for a few hours was probably good for me. I had to slow down, re-read documentation, and remember exactly how CloudFront, ACM, and Route 53 interact — instead of relying on half-remembered muscle memory.

Not the night I planned, but not wasted either.

Anyway — the blog is live now. Hopefully the next update doesn't require another round of DNS archaeology or CloudFront forensics.
