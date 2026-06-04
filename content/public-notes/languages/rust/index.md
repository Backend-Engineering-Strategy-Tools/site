---
title: "Rust"
date: 2026-06-03
draft: false
showReadingTime: false
layout: single
tags: ["rust", "systems-programming", "cli", "wasm", "performance"]
---

Systems language with memory safety guarantees without a garbage collector. The ownership and borrow checker model enforces at compile time what other languages leave to the runtime or the programmer.

The pitch: C/C++ performance and control, without the entire class of memory safety bugs that makes systems programming treacherous. In practice the borrow checker is the learning curve, it rejects code that would be valid in any other language until you understand why it is wrong.

---

## Where Rust is winning

**CLI tooling**: a significant share of modern CLI tools are written in Rust. `ripgrep`, `fd`, `bat`, `exa`/`eza`, `zoxide`, `tokei`. Startup time and binary distribution (single static binary) are the wins.

**WebAssembly**: Rust compiles to WASM with first-class tooling (`wasm-pack`, `wasm-bindgen`). Running near-native code in the browser or at the edge.

**Embedded / systems**: where C used to be the only option. The safety guarantees matter more, not less, when there is no OS underneath.

**Cloud infrastructure tooling**: parts of the ecosystem are being rewritten in Rust. Firecracker (AWS Lambda's VMM), parts of the Linux kernel, Cloudflare Workers runtime.

---

## Tooling

**Cargo**: the build system and package manager. Handles dependencies, building, testing, and publishing. One of the better-designed package managers in any ecosystem.

**rustup**: toolchain manager. Manages Rust versions and targets (cross-compilation).

**clippy**: linter. Catches more than the compiler, opinionated in useful ways.

**rustfmt**: formatter. Like `gofmt`, one style, no debate.

**IDE:** VS Code with `rust-analyzer` extension, or IntelliJ/CLion with the Rust plugin.

---

## The learning curve

The borrow checker is a genuine obstacle. Rust enforces at compile time:
- Exactly one owner of any value
- Any number of immutable references OR one mutable reference — not both
- References cannot outlive the value they point to

This is unfamiliar to anyone coming from languages with a GC. The compiler error messages are unusually helpful, but expect to spend real time understanding ownership before writing idiomatic Rust.

---

## Resources

- [The Rust Book](https://doc.rust-lang.org/book/): the standard introduction, free online
- [Rustlings](https://github.com/rust-lang/rustlings): small exercises for learning by doing
- [crates.io](https://crates.io/): the package registry
- [Blessed.rs](https://blessed.rs/): curated crate recommendations by category

## The trend pattern

Language adoption tends to follow ecosystem trends rather than purely technical merit. I started with Java. Then OpenStack brought Python into infrastructure work. Then Kubernetes arrived and its ecosystem was written in Go — so Go became the language of the cloud-native world by proximity as much as by choice.

Rust looks like the next turn of that cycle. The "rewrite it in Rust" trend is real and growing — CLI tooling, parts of the Linux kernel, browser engines, cloud infrastructure. If the pattern holds, the ecosystem will pull Rust into more places where it becomes the pragmatic choice rather than the deliberate one.

Haven't given it a serious attempt yet. Worth doing — not because Rust is clearly the right tool for the things currently being built, but because being ahead of the ecosystem trend rather than behind it is how you end up with useful experience when the moment arrives. The tooling is good, the learning resources are good, and the borrow checker will teach you something about memory regardless of whether you end up writing Rust in production.
