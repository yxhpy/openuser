# CI/CD Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipelines for OpenUser.

## Overview

OpenUser uses GitHub Actions for automated testing, building, and deployment. The CI/CD pipeline ensures code quality, security, and reliable deployments.

## Workflows

### 1. CI - Continuous Integration (`ci.yml`)

**Triggers**: Push to `main`/`develop`, Pull Requests

**Jobs**:
- **Backend Tests**: Run Python tests with 100% coverage requirement
- **Frontend Tests**: Run JavaScript/TypeScript tests
- **Code Quality**: Linting, type checking, security scans
- **Docker Build**: Build and validate Docker image

**Services**:
- PostgreSQL 15
- Redis 7

**Artifacts**:
- Coverage reports (HTML, XML)
- Security scan results

### 2. CD - Continuous Deployment (`cd.yml`)

**Triggers**: Version tags (`v*.*.*`), Releases, Manual dispatch

**Jobs**:
- **Build and Push**: Build multi-arch Docker images and push to GitHub Container Registry
- **Scan Image**: Vulnerability scanning with Trivy
- **Deploy Staging**: Automatic deployment to staging environment
- **Deploy Production**: Manual approval required, deploys to production
- **Release Notes**: Generate and update release notes

**Artifacts**:
- SBOM (Software Bill of Materials)
- Vulnerability scan results

### 3. Code Quality and Security (`code-quality.yml`)

**Triggers**: Push, Pull Requests, Weekly schedule

**Jobs**:
- **CodeQL Analysis**: Static code analysis for Python and JavaScript
- **Dependency Review**: Check for vulnerable dependencies
- **Python Security**: Bandit, Safety, pip-audit scans
- **JavaScript Security**: npm audit
- **License Check**: Verify license compliance
- **Coverage Tracking**: Track code coverage over time

**Artifacts**:
- Security reports
- License reports
- Coverage reports

### 4. Release Management (`release.yml`)

**Triggers**: Push to `main`, Manual dispatch

**Jobs**:
- **Semantic Release**: Automatic versioning based on commit messages
- **Manual Release**: Manual version bump (major/minor/patch)
- **Update Changelog**: Generate and update CHANGELOG.md

### 5. Performance Testing (`performance.yml`)

**Triggers**: Push to `main`, Pull Requests, Weekly schedule, Manual

**Jobs**:
- **Performance Tests**: Run pytest-benchmark tests
- **Load Tests**: Run Locust load tests
- **Frontend Performance**: Bundle size analysis
- **Lighthouse CI**: Web performance metrics

**Artifacts**:
- Benchmark results
- Load test reports
- Bundle analysis
- Lighthouse reports

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer Workflow                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Push to Branch │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   CI Workflow   │
                    │  - Tests        │
                    │  - Linting      │
                    │  - Build        │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Pull Request   │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Code Review    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Merge to Main  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Semantic Release│
                    │  - Version      │
                    │  - Tag          │
                    │  - Changelog    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  CD Workflow    │
                    │  - Build Image  │
                    │  - Scan         │
                    │  - Deploy       │
                    └─────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │    Staging    │         │  Production   │
        │  (Automatic)  │         │   (Manual)    │
        └───────────────┘         └───────────────┘
```

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for automatic versioning and changelog generation.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature (triggers minor version bump)
- `fix`: Bug fix (triggers patch version bump)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### Breaking Changes

Add `BREAKING CHANGE:` in the footer to trigger a major version bump:

```
feat(api): redesign authentication system

BREAKING CHANGE: The authentication API has been completely redesigned.
Old tokens are no longer valid.
```

### Examples

```bash
# Feature (minor version bump)
git commit -m "feat(api): add user profile endpoint"

# Bug fix (patch version bump)
git commit -m "fix(auth): resolve token expiration issue"

# Documentation
git commit -m "docs: update deployment guide"

# Breaking change (major version bump)
git commit -m "feat(api): redesign REST API

BREAKING CHANGE: API endpoints have been restructured"
```

## Secrets Configuration

### Required Secrets

Configure these secrets in GitHub repository settings:

#### Docker Registry
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

#### Kubernetes Deployment
- `KUBE_CONFIG_STAGING`: Base64-encoded kubeconfig for staging cluster
- `KUBE_CONFIG_PRODUCTION`: Base64-encoded kubeconfig for production cluster

#### Notifications
- `SLACK_WEBHOOK`: Slack webhook URL for deployment notifications

#### Code Coverage
- `CODECOV_TOKEN`: Codecov upload token (optional)

### Setting Secrets

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 > kubeconfig.b64

# Add to GitHub Secrets
# Go to: Settings > Secrets and variables > Actions > New repository secret
```

## Environments

### Staging

- **URL**: https://staging-api.openuser.example.com
- **Deployment**: Automatic on version tags
- **Purpose**: Pre-production testing

### Production

- **URL**: https://api.openuser.example.com
- **Deployment**: Manual approval required
- **Purpose**: Live production environment

### Environment Configuration

Configure environments in GitHub:
1. Go to Settings > Environments
2. Create `staging` and `production` environments
3. Add protection rules for production:
   - Required reviewers
   - Wait timer
   - Deployment branches

## Version Management

### Automatic Versioning (Recommended)

Semantic Release automatically determines version based on commit messages:

1. Commit with conventional commit format
2. Push to `main` branch
3. Semantic Release analyzes commits
4. Creates version tag and release
5. Updates CHANGELOG.md

### Manual Versioning

Trigger manual version bump:

1. Go to Actions > Release Management
2. Click "Run workflow"
3. Select version bump type (major/minor/patch)
4. Run workflow

Or use CLI:

```bash
# Install bump2version
pip install bump2version

# Bump version
bump2version patch  # 0.1.0 -> 0.1.1
bump2version minor  # 0.1.0 -> 0.2.0
bump2version major  # 0.1.0 -> 1.0.0

# Push changes
git push origin main --tags
```

## Deployment Process

### Staging Deployment

1. Create version tag: `git tag v0.1.0 && git push origin v0.1.0`
2. CD workflow triggers automatically
3. Builds Docker image
4. Scans for vulnerabilities
5. Deploys to staging
6. Runs smoke tests

### Production Deployment

1. Create GitHub release from tag
2. CD workflow triggers
3. Requires manual approval
4. Deploys to production
5. Runs smoke tests
6. Sends Slack notification

### Rollback

```bash
# Kubernetes rollback
kubectl rollout undo deployment/openuser-api -n openuser-production

# Or rollback to specific revision
kubectl rollout history deployment/openuser-api -n openuser-production
kubectl rollout undo deployment/openuser-api --to-revision=2 -n openuser-production
```

## Monitoring CI/CD

### GitHub Actions Dashboard

View workflow runs:
- Go to Actions tab in GitHub repository
- Filter by workflow, branch, or status
- View logs and artifacts

### Status Badges

Add to README.md:

```markdown
![CI](https://github.com/yxhpy/openuser/workflows/CI/badge.svg)
![CD](https://github.com/yxhpy/openuser/workflows/CD/badge.svg)
![Code Quality](https://github.com/yxhpy/openuser/workflows/Code%20Quality/badge.svg)
```

### Notifications

Configure notifications:
- GitHub: Settings > Notifications
- Slack: Add webhook URL to secrets
- Email: GitHub sends email on workflow failures

## Troubleshooting

### Workflow Fails

1. Check workflow logs in Actions tab
2. Review error messages
3. Check service health (PostgreSQL, Redis)
4. Verify secrets are configured
5. Re-run failed jobs

### Deployment Fails

1. Check Kubernetes cluster status
2. Verify kubeconfig secrets
3. Check pod logs: `kubectl logs -f deployment/openuser-api -n openuser`
4. Verify image was pushed to registry
5. Check resource availability

### Tests Fail

1. Run tests locally first
2. Check database connection
3. Verify environment variables
4. Review test logs
5. Check for flaky tests

## Best Practices

1. **Always run tests locally** before pushing
2. **Use conventional commits** for automatic versioning
3. **Keep workflows fast** - optimize test execution
4. **Cache dependencies** - use GitHub Actions cache
5. **Fail fast** - stop on first error
6. **Monitor workflow duration** - optimize slow jobs
7. **Review security scans** - address vulnerabilities promptly
8. **Test deployments in staging** before production
9. **Use environment protection rules** for production
10. **Document workflow changes** in this file

## Performance Optimization

### Caching

Workflows use caching for:
- Python pip packages
- Node.js npm packages
- Docker layers

### Parallel Execution

Jobs run in parallel when possible:
- Backend and frontend tests
- Multiple security scans
- Independent deployments

### Resource Limits

- Workflow timeout: 60 minutes
- Job timeout: 30 minutes
- Artifact retention: 7-90 days

## Security

### Code Scanning

- **CodeQL**: Static analysis for vulnerabilities
- **Dependency Review**: Check for vulnerable dependencies
- **Trivy**: Container image scanning
- **Bandit**: Python security linting
- **npm audit**: JavaScript dependency scanning

### Secrets Management

- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly
- Use environment-specific secrets
- Audit secret access

## Maintenance

### Regular Tasks

- **Weekly**: Review security scan results
- **Monthly**: Update dependencies
- **Quarterly**: Review and optimize workflows
- **Annually**: Audit secrets and access

### Workflow Updates

1. Test changes in feature branch
2. Review workflow syntax
3. Test with workflow_dispatch
4. Monitor first production run
5. Document changes

## Support

- **Documentation**: https://docs.github.com/en/actions
- **Issues**: https://github.com/yxhpy/openuser/issues
- **Discussions**: https://github.com/yxhpy/openuser/discussions
