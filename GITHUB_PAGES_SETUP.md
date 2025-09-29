# GitHub Pages Setup Guide

This guide will help you set up GitHub Pages to host your Sphinx documentation.

## 📋 Prerequisites

- Repository must be public OR you need GitHub Pro/Team/Enterprise for private repos
- You must have admin access to the repository

## 🚀 Quick Setup (5 minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/[YOUR-USERNAME]/QTframework`
2. Click **Settings** (in the repository navigation bar)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### Step 2: Verify Workflow Permissions

1. Still in **Settings**
2. Go to **Actions** → **General** (in the left sidebar)
3. Scroll to **Workflow permissions**
4. Select **Read and write permissions**
5. Check **Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

### Step 3: Run the Documentation Workflow

1. Go to the **Actions** tab in your repository
2. Find "Documentation" workflow in the left sidebar
3. Click **Run workflow** → **Run workflow** (on main branch)
4. Wait for the workflow to complete (green checkmark)

### Step 4: Access Your Documentation

After the first successful deployment:

1. Go back to **Settings** → **Pages**
2. You'll see: "Your site is live at `https://[YOUR-USERNAME].github.io/QTframework/`"
3. Click the link to view your documentation!

## 🔧 Configuration Details

### Custom Domain (Optional)

If you have a custom domain:

1. In **Settings** → **Pages**
2. Under **Custom domain**, enter your domain (e.g., `docs.example.com`)
3. Check **Enforce HTTPS**
4. Add a CNAME file in your docs output with your domain

### Branch Protection (Recommended)

Protect your main branch to ensure docs are always valid:

1. **Settings** → **Branches**
2. Add rule for `main` or `master`
3. Enable:
   - Require pull request reviews
   - Require status checks (select "Documentation")
   - Require branches to be up to date

## 📁 How It Works

```mermaid
graph LR
    A[Push to main] --> B[Docs Workflow Triggers]
    B --> C[Build Sphinx Docs]
    C --> D[Upload as Artifact]
    D --> E[Deploy to Pages]
    E --> F[Live at github.io]
```

1. **Trigger**: Push to main branch or manual trigger
2. **Build**: Sphinx builds HTML documentation
3. **Upload**: Documentation uploaded as Pages artifact
4. **Deploy**: GitHub Pages deployment action publishes it
5. **Live**: Available at `https://[username].github.io/[repo]/`

## 🏗️ Project Structure

```
QTframework/
├── docs/
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Documentation home
│   ├── _build/          # Build output (git-ignored)
│   │   └── html/        # HTML output for Pages
│   └── ...
├── .github/
│   ├── workflows/
│   │   └── docs.yml     # Documentation workflow
│   └── actions/
│       └── build-docs/  # Reusable build action
└── pyproject.toml       # Sphinx dependencies
```

## 🔍 Troubleshooting

### Documentation not appearing

1. Check workflow ran successfully (Actions tab)
2. Verify Pages is enabled with "GitHub Actions" source
3. Wait 5-10 minutes for first deployment
4. Check the Pages URL (might be cached)

### Build failures

1. Test locally first: `cd docs && make html`
2. Check Sphinx warnings/errors in workflow logs
3. Ensure all dependencies in `pyproject.toml[docs]`
4. Verify `docs/conf.py` is configured correctly

### 404 errors on subpages

- Ensure `.nojekyll` file is created (the workflow does this)
- Check that all HTML files are in the artifact
- Verify no absolute paths in your documentation

### Permission errors

```
Error: The deploy step encountered an error: The process '/usr/bin/git' failed with exit code 128
```

Fix: Settings → Actions → General → Workflow permissions → "Read and write permissions"

## 📚 Additional Features

### PR Previews (Advanced)

To preview documentation in PRs, you could:

1. Build docs in PR workflow
2. Upload to a temporary location
3. Comment on PR with preview link
4. Clean up after merge

### Multiple Versions (Advanced)

For versioned docs (v1.0, v2.0, etc.):

1. Use `sphinx-multiversion` extension
2. Modify workflow to build all versions
3. Create version switcher in theme

## 🔗 Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs (Alternative)](https://readthedocs.org/)

## ✅ Checklist

- [ ] GitHub Pages enabled with "GitHub Actions" source
- [ ] Workflow permissions set to read/write
- [ ] Documentation workflow ran successfully
- [ ] Site accessible at github.io URL
- [ ] Custom domain configured (optional)
- [ ] Branch protection enabled (optional)

---

**Note**: The first deployment might take 5-10 minutes to become available. Subsequent updates are usually faster (1-2 minutes).
