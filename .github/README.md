# GitHub Configuration for Semantica

## 📋 Issue Templates

- **[Bug Report](ISSUE_TEMPLATE/bug_report.md)** - Report bugs
- **[Feature Request](ISSUE_TEMPLATE/feature_request.md)** - Suggest features
- **[Documentation](ISSUE_TEMPLATE/documentation.md)** - Report docs issues
- **[Support](ISSUE_TEMPLATE/support.md)** - Get help
- **[Grant/Partnership](ISSUE_TEMPLATE/grant.md)** - Propose partnerships or funding

## 🔄 Workflows

- **[ci.yml](workflows/ci.yml)** - Build validation (runs on push/PR)
- **[release.yml](workflows/release.yml)** - Release to GitHub & PyPI (runs on version tags)
- **[security.yml](workflows/security.yml)** - Weekly dependency scan
- **[docs.yml](workflows/docs.yml)** - Deploy docs to GitHub Pages

## 🤝 Community

- **[FUNDING.yml](FUNDING.yml)** - Sponsorship options
- **[SUPPORT.md](SUPPORT.md)** - How to get support
- **[Pull Request Template](pull_request_template.md)** - PR guidelines

## 🚀 Releasing a New Version

```bash
# Update version in pyproject.toml and CHANGELOG.md
git tag v0.0.3
git push origin v0.0.3
# GitHub Actions automatically creates release and publishes to PyPI
```

**Setup Required (one-time):**
- GitHub: Create environment named `pypi`
- PyPI: Add trusted publisher for `Hawksight-AI/semantica` with workflow `release.yml`

## 📚 Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
