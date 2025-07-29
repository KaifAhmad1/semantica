Building Great SDKs: A Comprehensive Guide for Developers and LLMs
This guide provides a detailed, structured approach to creating Software Development Kits (SDKs) that are intuitive, robust, and maintainable for both developers and Large Language Models (LLMs). Drawing on modern practices, tools, and real-world examples, it explores the why, what, and how of building high-quality SDKs, with insights from veteran SDK engineer Quentin Pradet. This document is optimized for GitHub Markdown rendering.

Table of Contents

Introduction to SDKs
What is an SDK?
Why Build an SDK?


Why Not Just Use an API?
Example: Elasticsearch Query


The SDK Development Ladder
Level 1: Manually-Written SDKs
Level 2: In-House Generators
Level 3: General-Purpose Generators
Level 4: OpenAPI Generators


API-First Design
Using LLMs to Generate SDKs
Day-to-Day Life of an SDK Maintainer
Should SDKs Be Open Source?
Best Practices for Building SDKs
Reusing Existing SDKs
Case Study: Elasticsearch SDKs
Conclusion


1. Introduction to SDKs
What is an SDK?
A Software Development Kit (SDK) is a collection of tools, libraries, and documentation designed to help developers build applications for a specific platform, framework, or API. Historically distributed on CD-ROMs (e.g., Windows CE Platform SDK in the 1990s), modern SDKs are digital, hosted on package registries like npm or PyPI, with documentation accessible online.
SDKs vs. Frameworks:

SDKs: Libraries you call from your code, offering flexibility without enforcing architecture.
Frameworks: Invoke your code, enforcing opinionated design patterns.

This guide focuses on SDKs for HTTP APIs, which simplify interactions with web-based services.
Why Build an SDK?
SDKs enhance the developer experience by abstracting API complexities. Key benefits include:

Simplified API Usage: Intuitive interfaces with IDE autocompletion and type hints reduce errors.
Improved Documentation: Language-specific docs (reference, tutorials, examples) aid developers and LLMs.
Robust Error Handling: Specific exceptions and retry mechanisms (e.g., exponential backoff for HTTP 429) improve reliability.
Language-Specific Features: Leverage idioms like async/await in Python or LINQ in C#.
Authentication Management: Simplify credential handling (e.g., API keys, OAuth).
Backward Compatibility: Stable APIs minimize code changes during upgrades.
Configurability: Extensive parameters (e.g., timeouts, retries) adapt to user needs.
Observability: Built-in metrics (e.g., OpenTelemetry) monitor performance.
Helpers and Utilities: Features like auto-pagination or streaming simplify tasks.
Ecosystem Integration: Support tools like LangChain or protocols like Apache Arrow.


2. Why Not Just Use an API?
HTTP APIs, while standard, require manual handling of headers, authentication, and errors, which can be cumbersome. SDKs abstract these concerns, making development faster and more reliable.
Example: Elasticsearch Query
Without SDK (Raw HTTP):
POST /my-index/_search
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"user": "quentin"}},
        {"range": {"age": {"gte": 30}}}
      ]
    }
  }
}

This requires manual HTTP requests, authentication, and error handling.
With Elasticsearch Python SDK:
from elasticsearch import Elasticsearch

client = Elasticsearch("http://localhost:9200")
response = client.search(
    index="my-index",
    query={
        "bool": {
            "filter": [
                {"term": {"user": "quentin"}},
                {"range": {"age": {"gte": 30}}}
            ]
        }
    }
)

The SDK handles authentication, headers, and errors, simplifying the query.
With DSL (Domain-Specific Language):
from elasticsearch_dsl import Search

s = Search(using=client, index="my-index") \
    .filter("term", user="quentin") \
    .filter("range", age={"gte": 30})
response = s.execute()

The DSL leverages Python’s syntax for conciseness and readability.

3. The SDK Development Ladder
Building an SDK involves choosing an approach based on scale and maintenance needs. The "SDK ladder" outlines four levels:
Level 1: Manually-Written SDKs

Description: Developers manually write SDKs for specific APIs, common in early-stage or open-source projects.
Pros:
Quick to start for small APIs.
Full control over code quality.


Cons:
Inconsistent across languages.
Hard to scale as APIs grow.
Difficult to maintain consistency.


Example: Early Elasticsearch SDKs were community-driven, leading to incomplete implementations.

Level 2: In-House Generators

Description: Generate SDKs from a custom specification (e.g., TypeScript, JSON) using in-house tools.
Pros:
Ensures consistency across languages.
Scales better than manual coding.


Cons:
High development cost for custom generators.
Requires maintaining generators for each language.


Example: Elasticsearch generates SDKs from a TypeScript specification for 500+ APIs, producing JSON for language-specific generators.

Level 3: General-Purpose Generators

Description: Use standardized tools like AWS Smithy or Microsoft TypeSpec.
Pros:
Reduces maintenance overhead.
Leverages battle-tested tools.


Cons:
Less flexibility for language-specific optimizations.
Learning curve for new tools.


Example: AWS uses Smithy for consistent SDKs across services like S3.

Level 4: OpenAPI Generators

Description: Use OpenAPI specifications with tools like OpenAPI Generator.
Pros:
Industry-standard format.
Supports multiple languages with minimal effort.


Cons:
Limited customization for complex use cases.
May produce less idiomatic code.


Example: REST APIs use OpenAPI to generate SDKs for Python, Java, and JavaScript.


4. API-First Design
An API-first design prioritizes defining the API specification before coding, ensuring:

Consistency across SDKs and APIs.
Clear documentation from the start.
Easier retrofitting for existing codebases.

Challenges:

Retrofitting legacy systems is complex.
Requires upfront planning.

Example: Elasticsearch’s SDKs are generated from a TypeScript specification, ensuring uniformity across eight languages.

5. Using LLMs to Generate SDKs
LLMs can assist in SDK development but have limitations:

Strengths:
Generate boilerplate or translate code (e.g., Java to Rust).
Provide examples based on documentation.


Weaknesses:
Struggle with complex APIs.
May produce outdated code (e.g., missing URL schemes).
Require human validation.


Best Practice: Use LLMs for prototyping, but rely on human review for production.


6. Day-to-Day Life of an SDK Maintainer
Maintainers handle:

User Support: Answering questions on GitHub or forums.
Documentation: Writing tutorials, reference docs, and examples.
Code Maintenance: Fixing bugs, adding features, ensuring compatibility.
Performance Monitoring: Using OpenTelemetry for metrics.
Community Engagement: Reviewing pull requests.

Rule of Thumb: One engineer can maintain 1–2 manual SDKs or 4–5 generated SDKs.

7. Should SDKs Be Open Source?
Yes, because:

Transparency: Developers can debug and understand SDK behavior.
Community Contributions: Pull requests improve SDKs.
LLM Benefits: LLMs can analyze tests and code.
No Competitive Risk: SDKs expose APIs, not proprietary logic.

Example: AWS S3 and OpenAI SDKs are open source, fostering adoption (e.g., S3-compatible services like MinIO).

8. Best Practices for Building SDKs

Simplify Developer Experience:
Use autocompletion-friendly interfaces.
Provide type hints and parameter descriptions.


Robust Documentation:
Follow the Diátaxis framework (tutorials, how-to guides, reference, explanations).
Include Markdown files for LLMs (e.g., /llms.txt).


Error Handling:
Raise specific exceptions (e.g., ResourceConflict for HTTP 409).
Implement retries with exponential backoff.


Leverage Language Features:
Python: Support async/await via unasync.
JavaScript: Support CommonJS, ES Modules, Deno.
C#: Use LINQ or expression trees.


Authentication:
Simplify credential management.
Handle edge cases (e.g., Kerberos via Requests).


Backward Compatibility:
Use long deprecation periods.
Avoid breaking changes.


Configurability:
Support extensive parameters (e.g., Elasticsearch’s 50+ parameters).
Document all options.


Observability:
Integrate OpenTelemetry for metrics.
Provide tracing for custom monitoring.


Helpers and Utilities:
Add streaming, auto-pagination, or bulk operations.
Optimize serialization (e.g., orjson for JSON).


Ecosystem Integration:
Support tools like LangChain.
Optimize for protocols like Apache Arrow.




9. Reusing Existing SDKs
Instead of building new SDKs, make APIs compatible with existing ones:

OpenAI API: Supported by Google Vertex, Amazon Bedrock, etc.
AWS S3 API: Supported by MinIO, Backblaze B2, though compatibility issues arise (e.g., data integrity).

Trade-Offs:

Pros: Reduces development effort.
Cons: Evolving APIs may break compatibility.


10. Case Study: Elasticsearch SDKs
Elasticsearch’s Python SDK exemplifies best practices:

Conciseness: DSL simplifies complex queries.
Configurability: 50+ parameters for authentication, retries, etc.
Observability: OpenTelemetry integration.
Backward Compatibility: Long deprecation periods.
Open Source: Community-driven improvements.

Example Specification (TypeScript):
{
  "name": "synonyms_set.put",
  "path": "/_synonyms/{synonyms_set}",
  "methods": ["PUT"],
  "params": {
    "synonyms_set": { "type": "string", "required": true },
    "body": { "type": "SynonymSet", "required": true }
  }
}


11. Conclusion
Great SDKs balance developer experience, maintainability, and scalability. Key takeaways:

Use the SDK ladder to choose the right approach.
Prioritize simplicity, documentation, and error handling.
Embrace open-source for community and transparency.
Integrate with tools like OpenTelemetry and LangChain.

For further reading, explore Elasticsearch SDKs or tools like AWS Smithy and OpenAPI Generator.

Authored by Quentin Pradet, with contributions from Gergely Orosz. Published on July 29, 2025.
