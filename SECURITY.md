# Security Policy

## 🔒 Security Best Practices

This repository follows security best practices to protect API keys and sensitive information.

### ✅ What's Protected

1. **Secret Files are Gitignored**
   - `.env` - Local environment variables
   - `.streamlit/secrets.toml` - Streamlit secrets
   - `.env.local`, `.streamlit/secrets.toml.local` - Local overrides

2. **Pre-commit Hook**
   - Automatically prevents committing secret files
   - Scans for potential hardcoded API keys
   - Located at `.git/hooks/pre-commit`

3. **Secret Masking**
   - All logs and output automatically mask API keys
   - Uses `utils.secret_masker` for safe logging
   - See [SECRET_MASKING.md](SECRET_MASKING.md) for details

4. **CI/CD Security**
   - GitHub Actions workflow scans for secret leaks
   - No secrets stored in workflow files
   - Uses environment variables and secrets management

### 🚫 What NOT to Commit

**Never commit these files:**
- `.env` or `.env.local`
- `.streamlit/secrets.toml` or `.streamlit/secrets.toml.local`
- Any file containing real API keys
- Log files that might contain secrets

**Never hardcode:**
- API keys in source code
- Passwords or tokens
- Private keys or certificates

### ✅ Safe to Commit

- `.env.example` - Template file with placeholder values
- Documentation with example keys (clearly marked)
- Test files with fake/test keys (clearly marked)

### 🔑 Setting Up API Keys

#### Option 1: Environment Variables (Recommended for Local Development)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual API keys:
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

3. The `.env` file is automatically gitignored

#### Option 2: Streamlit Secrets (Recommended for Production)

1. Create `.streamlit/secrets.toml`:
   ```toml
   [api_keys]
   openai_api_key = "sk-your-actual-key-here"
   anthropic_api_key = "sk-ant-your-actual-key-here"
   ```

2. The `secrets.toml` file is automatically gitignored

#### Option 3: Streamlit Cloud Secrets

For Streamlit Cloud deployments, use the Streamlit Cloud secrets management interface.

### 🔍 Verifying Security

Before pushing to GitHub, verify:

1. **Check for tracked secret files:**
   ```bash
   git ls-files | grep -E "\.env$|secrets\.toml$"
   ```
   Should return nothing.

2. **Check git history for secrets:**
   ```bash
   git log --all --full-history -S "sk-" --source
   ```
   Should only show example/placeholder keys.

3. **Test pre-commit hook:**
   ```bash
   .git/hooks/pre-commit
   ```

4. **Scan for hardcoded keys:**
   ```bash
   grep -r "sk-[a-zA-Z0-9]\{32,\}" --include="*.py" . | grep -v "MASKED" | grep -v "example"
   ```
   Should return nothing.

### 🛡️ Dependency Security

This repository uses secure, up-to-date dependencies:

- **LangChain**: `>=0.2.5` (fixes CVE-2024-2965)
- **LangChain Community**: `>=0.2.19` (fixes CVE-2024-8309, CVE-2024-5998)
- **Streamlit**: `>=1.37.0` (fixes CVE-2024-42474)

See `requirements.txt` for the full list.

### 🚨 If You Accidentally Commit a Secret

1. **Immediately revoke the exposed key** in the provider's dashboard
2. **Generate a new key** and update your local files
3. **Remove from git history** (if not yet pushed):
   ```bash
   git reset HEAD~1  # If last commit
   # Or use git filter-branch/git filter-repo for older commits
   ```
4. **If already pushed**, you must:
   - Revoke the key immediately
   - Consider the key compromised
   - Use git history rewriting tools (advanced)

### 📝 Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email the maintainer directly
3. Include details about the vulnerability
4. Allow time for a fix before public disclosure

### ✅ Security Checklist Before Publishing

- [ ] `.env` is in `.gitignore` and not tracked
- [ ] `.streamlit/secrets.toml` is in `.gitignore` and not tracked
- [ ] No hardcoded API keys in source code
- [ ] Pre-commit hook is installed and working
- [ ] All dependencies are up-to-date and secure
- [ ] `.env.example` exists with placeholder values
- [ ] Git history scanned for secrets
- [ ] CI/CD workflows don't expose secrets

---

**Last Updated**: 2026-01-16
