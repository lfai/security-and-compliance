# Best Practices and Benchmarks for AI
AI technologies are becoming pervasive in our day-to-day activities and have potential to transform our lives and society. 
However, improper use of AI technologies pose significant risks that can negatively affect individuals, communities, and the world. 
This has led to the development of AI Risk Management Frameworks such as the NIST AI RMF and the EU Artificial Intelligence Act 
specifying a set of safeguards (controls) for responsible development and use of AI systems.

This initiative will create a whitepaper on best practices and benchmarks for AI platform and workloads and the related compliance artifacts. 
We will explore the NIST AI risk management framework with focus on developing best practices for AI risk assessment and compliance 
for AI workloads and  platforms. We will look at different aspects of AI risks around data, AI models, AI applications & runtime, 
and people & governance. We will then develop best practices and benchmarks for a generic AI platform.

## Who is the intended audience?
This whitepaper is intended for teams and organizations developing AI workloads and platforms and interested in best practices for 
managing AI risks associated with them. We will look at various AI RMF such as the NIST Gen AI and EU AI Act and identify best practices 
for managing/mitigating those risks for AI systems. This whitepaper will specifically look at the NIST Gen AI RMF and identify benchmarks 
for handling those risks/controls in generic AI systems. As part of this effort we will also generate compliance artifacts such as 
AI catalog containing requirements/controls and component definitions giving best practices technology specific rules for any AI system.

## What problem are we addressing?
Improper use of AI technologies pose significant risks that can negatively affect individuals, communities, and the world. 
- What are the risks associated with AI systems (outside of standards cybersecurity risks) such as 
  - data privacy and provenance, 
  - AI models training and inferencing wrt to bias, hate, drift, etc.
  - AI applications risk leading to exposure of personal and sensitive information, wrong outputs, hateful content, bias, etc.
  - People and governance and societal risks
- What controls need to be there specifically for AI systems and workloads to cover the above risks?
- What are the best practices for securing the risks related to AI systems
- What AI metrics need to be collected to cover the risks?
- What are some of the common tools used for collecting / reporting these metrics?

This has led to the development of AI Risk Management Frameworks such as the NIST AI RMF and the EU Artificial Intelligence Act 
specifying a set of safeguards (controls) for responsible development and use of AI systems.

## What assumptions are we making about the audience or content?
Audience is familiar with:
- How AI Systems are built, deployed, and managed
- General idea of security and compliance


## Goals
Need to find answers of below questions and provide guidance for mitigations:
- Develop best practices for AI risk assessment and compliance of AI workloads and  platforms. 
- Explore different AI regulations and Acts such as NIST AI RMF, EU AI Act, etc. and identify a common set of AI controls.
- Develop best practices and benchmarks for specific rules that need to be checked for generic AI platforms for the above set of controls.
- Identify AI metrics to be collected for different aspects of AI risks - data, AI models, AI applications & runtime, and people & governance.
- Associate the AI metrics with the best practices rule to validate them
- Create OSCAL artifacts for Best practices AI controls catalogs and component definition.


## Scope

### In Scope
- Framework Dimensions, Functions, Lifecycle, and Architecture

### Out-of-Scope
- AI Safety and how to secure AI systems
- Usage of AI models for different tasks
