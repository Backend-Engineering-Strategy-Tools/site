---
title: "Point, Don't Describe"
description: "A running list of what actually works directing Claude on real projects — grounding things in something concrete beats describing them, almost every time."
date: 2026-08-13
draft: true
showReadingTime: false
layout: single
tags: ["ai", "llm", "claude-code", "workflow"]
---

I was debugging a [3D-printed bracket](/garage/door-window-guard/) with Claude — cutting one piece off a model and moving it elsewhere. Simple enough in principle. In practice it took seven attempts, and five of the wrong ones weren't wrong because the geometry logic was bad. They were wrong because I kept saying "cut the leg off" and Claude kept picking a different piece than the one I meant.

Neither of us was being unclear on purpose. The part just had two similar-looking features and no shared vocabulary to tell them apart in words. "The leg," "the block," "the other end" — every noun was ambiguous, and every attempt to disambiguate in a follow-up message just added more ambiguous nouns.

What actually broke the loop: I asked Claude how I could explain this better, and it rendered the part with the confusing sub-regions painted in different colors, plus a labeled axis gizmo — red for X, green for Y, blue for Z. Nothing fancy. The important part was that it reused the *same* colors it had already been using in every earlier render that session, so it wasn't a new thing either of us had to learn under frustration — just a reference we could both already read.

My next message used those same labels straight back: "cut perpendicular to green, main body = grey part." One exchange, and the actual structure — a compound feature I hadn't realized Claude was treating as one piece — was on the table. Five rounds of prose hadn't gotten there.

That's the literal version of the title. But the same shape of fix kept showing up in other places too, so this is turning into a running list rather than a one-off.

---

## Grounding beats describing

The general version of the bracket story: when you're describing something spatial — which piece, which direction, which region of a screenshot — you're both working from a mental model that exists only in your heads, and every round of text is a lossy re-encoding of it. A label removes the encoding step. You point at the picture that already has the thing named, instead of describing it.

Costs almost nothing to set up if you establish the convention early — pick axis colors, region labels, whatever fits the problem, and reuse them across every output in the session. Then when something actually gets stuck, there's already a shared vocabulary to reach for instead of inventing one mid-argument. Not unique to CAD work either — a UI layout, a diagram, a multi-region screenshot, anywhere "which one" is doing a lot of work in a sentence.

---

## "It passed the checks" isn't the same as "it's right"

Same bracket project, different failure mode. Claude ran automated checks after every attempt at the geometry — watertight mesh, one connected piece, correct dimensions — and four separate times those checks came back clean on a result that was still wrong. Once it was a hole that had gone subtly oval instead of round; once it was a hidden internal wall that only showed up when I actually loaded the file into my slicer.

The checks weren't useless, they just weren't checking the thing that mattered. "The mesh is technically valid" and "this is the shape I actually asked for" are different claims, and an LLM will confidently report the one it can verify, which isn't always the one you need verified. I ran into the same thing on an earlier part (parametric feet for a laser cutter frame): manifold and bounding-box checks both stayed green on a mesh that was quietly self-intersecting — only a render caught it.

The fix isn't "don't trust the checks," it's "make sure the check and the question actually match." If the real question is "does this look right," ask for a picture, not a pass/fail.

---

## When a clean fix keeps failing, the model's probably wrong, not the execution

Twice on the bracket, Claude produced a geometrically sound result — verified, rendered, no defects — and I still rejected it, because it had cut the correct-looking piece off the wrong end of the part. The technique was right both times. The target wasn't. It took stepping back and asking "wait, what do we actually think this part looks like" — not "let's try the technique again, more carefully" — to find that a piece I'd been treating as one feature was actually two stacked on top of each other.

The instinct after a rejected attempt is to refine the last approach. Sometimes that's right. But if a correction keeps landing in the same spot after supposedly-clean fixes, the more useful question is usually about the shared model of the problem, not the next iteration of the fix.

---

## Keep the human on the leash for anything that leaves a mark

Smaller than the others, but it's the one rule I never relax: Claude doesn't stage, commit, or push without me explicitly asking, every single time, no matter how obviously "done" a change looks. Edits to files are cheap to undo. A commit — let alone a push — is a decision I want to actually make, not one that happens because the work looked finished.

It's a narrow rule, but it's a good proxy for a wider one: the more permanent or visible an action, the more it should require an explicit ask, not an inference from context.

---

Four different situations, one underlying pattern: whether it's "which piece do you mean," "did this actually work," or "should this action happen" — the answer that holds up is the one grounded in something concrete (a label, a render, an explicit yes) rather than the one inferred from description or assumption. Cheaper to set the concrete thing up front than to argue your way back to it after five rounds of it not working.
