# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Unoplat Code Confluence project.

## Workflows

### Python Build (`python_build.yaml`)

This workflow runs on pull requests to the `main` branch that include changes to Python projects:
- `unoplat-code-confluence-commons`
- `unoplat-code-confluence-ingestion`

It performs the following tasks:
- Builds Python packages using Poetry
- Runs tests with pytest and generates coverage reports
- Uploads test coverage reports as artifacts

### Docusaurus Build (`docusaurus_build.yaml`)

This workflow runs on pull requests to the `main` branch that include changes to the Docusaurus documentation site:
- `code-confluence`

It performs the following tasks:
- Installs dependencies with Yarn
- Runs tests (if available)
- Runs ESLint (if available)
- Performs TypeScript type checking (if available)
- Builds the Docusaurus site
- Uploads the build artifacts
- Uploads test coverage reports (if available)

## Artifacts

Both workflows upload artifacts that can be downloaded from the GitHub Actions run:
- Test coverage reports
- Docusaurus build output

These artifacts are retained for 7 days after the workflow run. 