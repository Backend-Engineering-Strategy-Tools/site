---
title: "Java"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
---

Java is my primary language for backend services. Mature ecosystem, strong tooling, and frameworks like Spring Boot and Quarkus make it productive for building production-grade APIs and microservices.

## Tooling

**IDE:** [IntelliJ IDEA](https://www.jetbrains.com/idea/) — the standard for Java development. Excellent refactoring, code analysis, and framework support (Spring, Quarkus, Jakarta EE). The free Community edition covers most needs; Ultimate adds Spring-specific tooling and database tools.

**Build:** [Gradle](https://gradle.org/) or [Maven](https://maven.apache.org/) — Gradle for flexibility and performance, Maven for convention-heavy projects where everyone knows where everything lives.

## Frameworks

[Spring Boot](https://spring.io/projects/spring-boot) — the dominant choice for enterprise Java. Convention over configuration, huge ecosystem, production-ready out of the box.

[Quarkus](https://quarkus.io/) — optimized for containers and GraalVM native compilation. Noticeably faster startup and lower memory footprint than Spring Boot. Worth considering for microservices running in Kubernetes.

## Testing with JUnit

[JUnit 5](https://junit.org/junit5/) is the standard testing framework. Combine with [Mockito](https://site.mockito.org/) for mocking and [AssertJ](https://assertj.github.io/doc/) for readable assertions.

```java
@Test
void shouldReturnGreeting() {
    var service = new GreetingService();
    assertThat(service.greet("Manfred")).isEqualTo("Hello, Manfred");
}
```

Spring Boot's `@SpringBootTest` and `@WebMvcTest` slice annotations make integration testing straightforward without spinning up a full application context.

## Resources

- [docs.spring.io](https://docs.spring.io/spring-boot/index.html)
- [quarkus.io/guides](https://quarkus.io/guides/)
- [JUnit 5 docs](https://junit.org/junit5/docs/current/user-guide/)
