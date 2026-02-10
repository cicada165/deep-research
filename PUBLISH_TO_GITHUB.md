# Publishing to GitHub - Step by Step

## Option 1: Create Repository via GitHub Web Interface (Recommended)

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `deep-research`
3. **Description**: "Automated research assistant with fact-checking and Streamlit frontend"
4. **Visibility**: Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

7. **Then push your code**:
   ```bash
   git push -u origin main
   ```
   - When prompted for username: enter your GitHub username
   - When prompted for password: use a **Personal Access Token** (not your password)
     - Create one at: https://github.com/settings/tokens
     - Select scopes: `repo` (full control of private repositories)

## Option 2: Use GitHub CLI (if installed)

```bash
# Authenticate
gh auth login

# Create repository and push
gh repo create deep-research --public --source=. --remote=origin --push
```

## Option 3: Use SSH (if you have SSH keys set up)

1. **First, add your SSH key to GitHub** (if not already done):
   - https://github.com/settings/keys

2. **Change remote to SSH**:
   ```bash
   git remote set-url origin git@github.com:qu4ntum/deep-research.git
   ```

3. **Create the repository on GitHub first** (via web interface), then:
   ```bash
   git push -u origin main
   ```

## Troubleshooting Authentication

### If you get "Authentication failed":

1. **Clear stored credentials**:
   ```bash
   git credential-osxkeychain erase
   host=github.com
   protocol=https
   ```
   (Press Enter twice after the last line)

2. **Use Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Name: "deep-research-push"
   - Expiration: Choose your preference
   - Scopes: Check `repo` (full control)
   - Generate and copy the token
   - Use this token as your password when pushing

3. **Or switch to SSH**:
   ```bash
   git remote set-url origin git@github.com:qu4ntum/deep-research.git
   git push -u origin main
   ```

## After Publishing

Once pushed, your repository will be available at:
**https://github.com/qu4ntum/deep-research**

## Security Reminder

✅ All security measures are in place:
- No API keys in the repository
- Pre-commit hook will prevent future mistakes
- `.env` is gitignored
- All dependencies are secure
