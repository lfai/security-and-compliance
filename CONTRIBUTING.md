
## How to Contribute

Thank you for your interest in contributing to the Security and Compliance Work Group's repository. The project appreciates efforts to improve our documentation, content and code.

This document outlines the process for submitting pull requests (PRs) from a private fork.

---

1. Create a public GitHub account

    The account must be associated with the same email address as registered with the Linux Foundation.

1. Install `git` on your machine and setup SSH:

    - [Connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
    - Specifically: [Adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)


1. Fork the Repository

    First, create a fork of this repository to a personal GitHub account. This creates a copy where changes can be made without directly affecting the original project.

1. Clone Your Fork

    Clone the forked repository to a local machine using Git.

    ```bash
    git clone git@github.com:lfai/security-and-compliance.git
    ```

1. Create a New Branch

    Create a dedicated branch for your changes (e.g., feature/your-feature-name or fix/issue-description). This keeps your work organized and isolated.

    ```bash
    git checkout -b feature/your-feature-name
    ```

4. Make Your Changes
    Implement your changes, adhering to the project's coding standards and conventions.

5. **Sign** & Commit Your Changes

    Commit your changes with clear and descriptive commit messages and sign using `-s` it with your email (which uses the email stored in your global or local git config file):

    ```bash
    git commit -s -m "Briefly describe your change request or new feature"
    ```

6. Push to Your Fork

    Push your new branch and commits to your private fork on GitHub.

    ```bash
    git push origin feature/your-feature-name
    ```

7. Open a Pull Request

    Navigate to the original repository on GitHub and create a pull request.

    > [!NOTE]
    > *The GitHub UI should automatically detect your has changes pushed and prompt you to create a Pull Request.*

    TO create a PR manually:

    - **Compare across forks**: On the pull request page, select the option to "compare across forks".
    - **Select your fork and branch**: Choose your fork and the branch containing your changes as the "head fork" and "compare branch".
    - **Choose the base branch**: Select the appropriate branch in the main repository (usually main or master) as the "base branch" where you want your changes merged.
    - **Provide a Title and Description**: Give your pull request a clear and concise title, and include a detailed description of the changes made, the problem it addresses, and any relevant context.

8. Review and Merge

    Project maintainers will review your pull request. They may provide feedback and suggestions for improvements. Be prepared to discuss your changes and make revisions if necessary. Once approved, your changes will be merged into the main repository.