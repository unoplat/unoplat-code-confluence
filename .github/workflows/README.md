# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Unoplat Code Confluence project.

## Workflows

### Python Build (`python_build.yaml`)

Runs on pull requests to the `dev` branch that include changes to any Python projects:
- `unoplat-code-confluence-commons`
- `unoplat-code-confluence-ingestion`
- `unoplat-code-confluence-query-engine`

It performs the following tasks:
- Builds Python packages using uv
- Runs tests with pytest and generates coverage reports
- Uploads test coverage reports as artifacts

### Docusaurus Build (`docusaurus_build.yaml`)

Runs on pull requests to the `dev` or `main` branches that include changes to the Docusaurus documentation site (`code-confluence/**`). It performs the following tasks:
- Installs dependencies with Yarn
- Runs tests (if available)
- Runs ESLint (if available)
- Performs TypeScript type checking (if available)
- Builds the Docusaurus site
- Uploads the build artifacts
- Uploads test coverage reports (if available)

### Merge with Dev Branch (`publish_release_management.yaml`)

Runs when pull requests into `dev` are merged. It uses Release Please to publish component-level releases and, when Dockerized components are released, builds and pushes container images.

### Promote App Release (`promote_app_release.yaml`)

Runs when a pull request merging `dev` into `main` is completed. It invokes Release Please with the `simple` strategy to cut an application-wide release using the root `version.txt` and `APP_CHANGELOG.md`.

## Artifacts

Relevant workflows upload artifacts that can be downloaded from the GitHub Actions run:
- Test coverage reports
- Docusaurus build output

These artifacts are retained for 7 days after the workflow run.
