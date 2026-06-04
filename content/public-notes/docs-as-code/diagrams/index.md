---
title: "Diagrams as Code — Mermaid and PlantUML"
date: 2026-06-03
draft: false
showReadingTime: false
layout: single
tags: ["mermaid", "plantuml", "diagrams", "docs-as-code"]
---

Diagrams as code: describe a diagram in text, render it as an image. No drag-and-drop, no binary file that diffs as noise, no diagram that goes stale because it's a PNG nobody updates. The source lives in Git alongside the code it describes.

## Mermaid

Mermaid is a JavaScript-based diagramming tool with a simple, readable syntax. It renders natively in GitHub Markdown, GitLab, and many documentation tools — paste a fenced code block with `mermaid` as the language and the diagram appears inline. No server needed for basic use.

Flowchart:

````markdown
```mermaid
flowchart LR
    A[Source] --> B{Build}
    B -- pass --> C[Test]
    B -- fail --> D[Notify]
    C --> E[Deploy]
```
````

Sequence diagram:

````markdown
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB
    Client->>API: POST /order
    API->>DB: INSERT order
    DB-->>API: ok
    API-->>Client: 201 Created
```
````

Other supported types: class diagrams, entity-relationship, state machines, Gantt charts, Git graphs.

The [Mermaid live editor](https://mermaid.live) is the fastest way to iterate on a diagram.

## PlantUML

PlantUML predates Mermaid and has a wider set of diagram types — UML sequence, class, component, deployment, activity, state, and non-UML types like C4 (architecture), BPMN, and Gantt. The syntax is more verbose than Mermaid but more expressive for complex diagrams.

PlantUML requires a rendering server (Java-based, self-hostable) or the hosted server at `plantuml.com`. Most IDE plugins (IntelliJ, VS Code) bundle a renderer.

Sequence diagram:

```plantuml
@startuml
actor Client
participant API
database DB

Client -> API : POST /order
API -> DB : INSERT order
DB --> API : ok
API --> Client : 201 Created
@enduml
```

Component diagram:

```plantuml
@startuml
package "Frontend" {
  [Web App]
}

package "Backend" {
  [API Server]
  [Worker]
}

database "PostgreSQL"

[Web App] --> [API Server]
[API Server] --> PostgreSQL
[Worker] --> PostgreSQL
@enduml
```

## Which to use

| | Mermaid | PlantUML |
|---|---|---|
| Renders in GitHub/GitLab | Yes, natively | No, requires plugin or pre-rendering |
| Setup | Zero | Rendering server or plugin |
| Syntax | Simple, readable | More verbose, more powerful |
| Diagram types | Core UML + Git/Gantt | Full UML + C4 + more |
| Best for | Quick diagrams in docs and READMEs | Complex architecture and UML diagrams |

## Resources

- [Mermaid documentation](https://mermaid.js.org/)
- [Mermaid live editor](https://mermaid.live)
- [PlantUML documentation](https://plantuml.com/)
- [PlantUML online server](https://www.plantuml.com/plantuml/uml/)
