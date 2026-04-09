---
title: "Go"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Go is my go-to language for backend services, CLI tools, and DevOps tooling. The standard library covers most of what you need, the compiler is fast, and the concurrency model (goroutines + channels) makes it well suited for infrastructure-adjacent work.

## Tooling

**IDE:** [GoLand](https://www.jetbrains.com/go/) — JetBrains' Go-specific IDE. Solid refactoring, built-in debugger, good test runner integration.

**Formatting:** `gofmt` / `goimports` — no debates about style, just run it.

**Linting:** [golangci-lint](https://golangci-lint.run/) — meta-linter that runs a configurable set of linters in one pass. Worth wiring into CI.

## Testing

Testing is built into the standard library — `go test ./...` is all you need to get started. Table-driven tests are the idiomatic pattern for covering multiple cases cleanly.

```go
func TestAdd(t *testing.T) {
    cases := []struct{ a, b, want int }{
        {1, 2, 3},
        {0, 0, 0},
    }
    for _, c := range cases {
        if got := Add(c.a, c.b); got != c.want {
            t.Errorf("Add(%d, %d) = %d, want %d", c.a, c.b, got, c.want)
        }
    }
}
```

## Resources

- [go.dev](https://go.dev/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com/)
