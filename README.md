
# Security and Compliance Work Group

This repository is used to develop and manage the Security and Compliance Work Group's assets as well as those from its subgroups.  This may include use cases, threat models, profiles, and other artifacts.

## Mission statement

 <div style="background-color: #C8F0FF;">
 <p style="margin: 8px;">
  The LF AI & Data Security and Compliance Work Group is dedicated to formulating interconnected security use cases, threat models, and policies that can be leveraged to create a comprehensive security and compliance strategy for AI-enabled applications throughout their lifecycle. The committee will establish a framework, which references and incorporates existing AI and ML standards and technologies, that enables an automated, self-sustaining cycle where effective governance fosters secure AI development, deployment and operations and AI-driven governance systems that can reduce risk and improve compliance in critical regulated environments.</p>
</div>

## How to get involved

#### Meetings and mailing lists

You will need to assure you have accounts created in both the Linux Foundation (LF) and the LF AI & Data Foundation (LFAI):

The work group will use the LF meeting management platform for all calls and formal communications and requires an LF account to participate.

In addition, the LF AI & Data Foundation has a separate account to which will be used by work group members for work group-specific communications and calendaring:

- https://lists.lfaidata.foundation/g/security-and-compliance-work-group


##### Creating LF accounts

1. Create an Linux Foundation account

    - https://docs.linuxfoundation.org/lfx/sso/create-an-account
    - Fill out your LF profile in the Individual Dashboard: [openprofile.dev](openprofile.dev)
        - *Please “Connect your Github” using an email address associated with your Github account.*

1. Register for an LF AI & Data Account
    - https://lists.lfaidata.foundation/register
        - *Please use the same email address as your LF account.*

##### Meeting sign-up

The LF AI & Data Foundation allows for self-registration to meetings via the foundation's Zoom.

- Using the LF AI & Data Community Calendar: [https://zoom-lfx.platform.linuxfoundation.org/meetings/lf-ai-foundation](https://zoom-lfx.platform.linuxfoundation.org/meetings/lf-ai-foundation?view=week)

- Find and click on the meeting that interests you, and click "Register" to sign up.

#### Agendas, Meeting minutes

<div><img src="images/logos/google-drive-40x36.png" style="width: 20px; margin-right: 10px;" alt="Google drive logo">
Request access to the project's <span style="color: gray;"><strong>Google drive folder</strong></span> which will be used to hold agendas, meeting notes, presentations, etc.

- [Link to Google drive folder](https://drive.google.com/drive/folders/0ABt8Tcg9DXLoUk9PVA)

#### Communication channels

<div><img src="images/logos/slack-logo-40x40.png" style="width: 20px; margin-right: 10px;" alt="Slack logo">
Please join the <span style="color: gray;"><strong>LF AI & Data Foundation Slack</strong></span> for informal communication with work group members and other registered users:</p>
</div>

- https://slack.lfaidata.foundation/

then join the project channel:

- [#security-and-compliance-work-group](https://lfaifoundation.slack.com/archives/C041ZAXCSJ0)

---

## Project structure

Initially, the work group will establish two subgroups to better divide and focus work against specific subject areas.

- Use cases and threat models
- Compliance and risk management

Work group members are encouraged to join and contribute to these subgroups each of which hosts its own bi-weekly meetings.

The subgroups will provide updates of its activities as part of the work group's meeting agenda.

#### Planned activities

A high-level view of the activity areas the work group and its subgroups will explore and develop concrete assets for:

![Planned activities diagram](images/diagrams/work-group-planned-activities-small.png)

#### Standards and project collaboration

The work group intends to collaborate with and reference work from other foundations and organizations including:

![](images/logos/collaboration-logos.png)

- [OWASP Foundation](https://owasp.org/)
    – [GenAI Security Project](https://genai.owasp.org/),
    - [Application Security Verification Standard (ASVS)](https://owasp.org/www-project-application-security-verification-standard/)
    - [Software Component Verification Standard (SCVS)](https://owasp.org/www-project-software-component-verification-standard/)
    - [CycloneDX](https://cyclonedx.org/) - Bill-of-Materials (BOM) standard and its [work groups](https://cyclonedx.org/participate/working-groups/) and profiles including:
        - *Machine Learning Transparency (MLBOM)*
        - *Threat Modeling (TMBOM)*
- [Linux Foundation](https://www.linuxfoundation.org/) and its projects including:
  - [Software Package Data Exchange (SPDX)](https://spdx.dev/) - Bill-of-Materials (BOM) standard and its area of interest including:
    - *[SPDX AI](https://spdx.dev/learn/areas-of-interest/ai/)*
- [OpenSSF](https://openssf.org/) and its work groups and guidelines:
    - [AI/ML Security work group](https://openssf.org/technical-initiatives/ai-ml-security/)
    - [Supply-chain Levels for Software Artifacts (SLSA)](https://openssf.org/projects/slsa/) - specification and its ability to measure [Secure Software Development Framework (SSDF)](https://csrc.nist.gov/Projects/ssdf) compliance.
- [NIST](https://www.nist.gov/) and its standards:
    - [Open Security Controls Assessment Language (OSCAL)](https://pages.nist.gov/OSCAL/) - security controls and profiles.s
    - [Secure Software Development Framework (SSDF)](https://csrc.nist.gov/Projects/ssdf) - secure software development practices.

---

## References

This section contains additional references to projects and resources that the work group might find useful:

##### Model transparency

- [OpenSSF Model Signing (OMS)]()
    - Specification: [ossf/model-signing-spec](https://github.com/ossf/model-signing-spec)
    - Tooling: [sigstore/model-transparency](https://github.com/sigstore/model-transparency)

##### Threat modeling

- [OWASP AI Exchange](https://owaspai.org/docs/ai_security_overview/) - website with general AI threat matrix, controls and risks.
    - [AI Security Matrix](https://owaspai.org/docs/ai_security_overview/#ai-security-matrix)
    - [Controls Overview](https://owaspai.org/docs/ai_security_overview/#controls-overview)
- [OWASP Threat Model Library](https://github.com/OWASP/www-project-threat-model-library) - first, open-sourced, structured, peer-reviewed threat modeling dataset.
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/) - a modeling tool used to create threat model diagrams as part of a secure development lifecycle.


##### Security compliance standards

- European Commission - [EU Cybersecurity Policies](https://digital-strategy.ec.europa.eu/en/policies/cybersecurity-policies)
    - [EU Cyber Resilience Act (CRA)](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
- Cybersecurity and Infrastructure Security Agency ([CISA](https://www.cisa.gov/))
    - [MITRE](https://cwe.mitre.org/)
        - [Common Weakness Enumeration (CWE)](https://en.wikipedia.org/wiki/Common_Weakness_Enumeration) - a category system for hardware and software weaknesses and vulnerabilities.
        - *As threat modeling aims to identify and address potential weaknesses, CWE provides a standard for categorization of actual weaknesses. Our WGs should look to assure semantic similarity*


## Code of Conduct

The work group and its subgroups adhere to the LF AI & Data's Code of Conduct (CoC) as published here:

- https://github.com/lfai/foundation/blob/main/codeofconduct.md

## License

All repository content is licensed under the [Apache 2.0 license](LICENSE) unless otherwise noted. Including:

- *Displayed [logos](images/logos) are copyrighted and/or  trademarked by their respective owners.*
