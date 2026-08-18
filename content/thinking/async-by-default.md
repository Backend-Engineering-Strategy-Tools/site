---
title: "Async by Default"
description: "How I run remote. A handful of defaults, not a philosophy: async first, overcommunicate status, virtual fika, screen share for concrete tasks, docs over meetings."
date: 2026-08-17
draft: false
showReadingTime: false
layout: single
tags: ["remote-work", "leadership", "platform-engineering"]
---

A few things that keep this practical rather than theoretical. A daily big-group morning chat, a virtual fika, helps recover some of the context you lose from not being in person, and gives everyone a bit of social presence when they're working from home. For a specific task, sharing a screen and working through it together beats describing it in a channel, it also skips the awkward moment of driving on a setup nobody else recognizes (Eclipse with vim bindings, for one). And before any of that, it helps to be clear on what you're actually trying to achieve and what output is wanted. For remote work that's usually easier if the output is something concrete: an ADR, a report, a script, or code. Anything that can be checked into git, opened as a PR, and reviewed.

---

## Async by default

The default assumption is that a message can wait for a reply, not that it needs one now. If something is actually urgent, say so explicitly and pick a synchronous channel on purpose. Don't let urgency be the default mode that everything else has to justify itself against.

This matters more than it sounds like it should, because the alternative isn't "more synchronous," it's "everyone interrupted, all the time, in whichever timezone happens to be awake." Async-by-default is what makes a team spread across timezones actually work instead of just technically function.

## Overcommunicate status

In person, status leaks. You see someone's screen, overhear a conversation, notice they look stuck. Remote, none of that happens for free. If I don't say where something is, nobody knows, and silence reads as "nothing's happening" even when it isn't.

So I default to saying more than feels necessary: what's in progress, what's blocked, what changed since yesterday. It feels redundant from the inside. It isn't, from the outside.

## Docs over meetings

If a decision or a piece of context needs to survive past the conversation it was made in, it goes in a doc, not a meeting that half the team wasn't in and nobody will remember accurately in three weeks. A meeting is for the parts that actually need real-time back-and-forth; everything else is cheaper and more durable written down.

This also means the doc has to actually get written, not just promised. "We'll write it up after" is where this default quietly fails if nobody owns it.
