# Add SSH Key to GitHub - Quick Steps

## Your SSH Public Key (already copied to clipboard):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAgk7B3r4UhbY8WA2c6S1al2ku7dYNOk9a8f6ev/+bC4 qu4ntum@github
```

## Steps to Add to GitHub:

1. **Go to GitHub SSH Settings**: https://github.com/settings/keys

2. **Click "New SSH key"** (green button)

3. **Fill in the form**:
   - **Title**: `Mac - deep-research` (or any name you prefer)
   - **Key type**: `Authentication Key`
   - **Key**: Paste your public key (it's already in your clipboard, or copy from above)

4. **Click "Add SSH key"**

5. **Verify it works**:
   ```bash
   ssh -T git@github.com
   ```
   You should see: `Hi qu4ntum! You've successfully authenticated...`

6. **Then push your code**:
   ```bash
   git push -u origin main
   ```

## That's it! 🎉

Once you add the key to GitHub, you'll be able to push without entering passwords.
