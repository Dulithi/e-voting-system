# Git Repository Setup Guide

## 📦 Push to GitHub/GitLab

### Step 1: Initialize Git Repository
```powershell
# Navigate to project root
cd "d:\Dulithi\Semester 7\crypto-project\e-voting-system"

# Initialize Git
git init

# Check status (should show many untracked files)
git status
```

### Step 2: Stage All Files
```powershell
# Add all files (respects .gitignore)
git add .

# Verify what will be committed
git status
```

**Note:** `.gitignore` is already configured to exclude:
- `venv/`, `__pycache__/`, `node_modules/`
- `*.key`, `*.pem`, `.env` (secrets)
- `uploads/`, `code-sheets/` (generated files)
- IDE configs, OS files

### Step 3: Create Initial Commit
```powershell
# Make first commit with descriptive message
git commit -m "feat: Initial commit - MVP Phase 1 complete with admin web and backend services"
```

### Step 4: Create Main Branch
```powershell
# Rename default branch to main
git branch -M main
```

### Step 5: Add Remote Repository

#### For GitHub:
1. Go to https://github.com
2. Click "New Repository"
3. Name: `e-voting-system`
4. Description: "Secure E-Voting System with Threshold Cryptography and Blind Signatures"
5. **Do NOT** initialize with README (we already have one)
6. Click "Create Repository"
7. Copy the repository URL (e.g., `https://github.com/yourusername/e-voting-system.git`)

```powershell
# Add GitHub remote
git remote add origin https://github.com/yourusername/e-voting-system.git
```

#### For GitLab:
1. Go to https://gitlab.com
2. Click "New Project" → "Create blank project"
3. Project name: `e-voting-system`
4. Visibility: Private (recommended for academic project)
5. **Uncheck** "Initialize with README"
6. Click "Create Project"
7. Copy the repository URL

```powershell
# Add GitLab remote
git remote add origin https://gitlab.com/yourusername/e-voting-system.git
```

### Step 6: Push to Remote
```powershell
# Push main branch to remote
git push -u origin main
```

**If authentication fails:**
- GitHub: Use Personal Access Token (Settings → Developer settings → Personal access tokens)
- GitLab: Use Deploy Token or Personal Access Token

### Step 7: Verify Push
1. Open your repository URL in browser
2. Confirm files are uploaded
3. Check README.md displays correctly
4. Verify `.env`, `venv/`, secrets are NOT visible

---

## 👥 Add Teammate as Collaborator

### GitHub:
1. Go to repository → Settings → Collaborators
2. Click "Add people"
3. Enter teammate's GitHub username/email
4. Set permission: **Write** (can push code)
5. Teammate will receive invitation email

### GitLab:
1. Go to repository → Settings → Members
2. Click "Invite members"
3. Enter teammate's GitLab username/email
4. Role: **Developer** (can push code)
5. Click "Invite"

---

## 🔄 Teammate Setup (After Invitation)

### 1. Clone Repository
```powershell
# Clone to local machine
git clone <repository-url>
cd e-voting-system
```

### 2. Follow Team Handoff Guide
- See [TEAM_HANDOFF.md](./TEAM_HANDOFF.md) for complete setup
- Install Python 3.13, PostgreSQL 18, Node 20
- Setup database with `scripts/db-init.sql`
- Start services per [START_SERVICES.md](../START_SERVICES.md)

### 3. Create Feature Branch
```powershell
# Create branch for your work
git checkout -b feature/webauthn-implementation

# Work on your feature
# ... make changes ...

# Commit and push
git add .
git commit -m "feat: Add WebAuthn biometric authentication"
git push origin feature/webauthn-implementation
```

### 4. Create Pull Request
1. Go to repository on GitHub/GitLab
2. Click "New Pull Request" / "New Merge Request"
3. Select your feature branch
4. Add description of changes
5. Request review from team member
6. Merge after approval

---

## 🌿 Git Workflow (Team Development)

### Branch Naming Convention
```
feature/feature-name      - New features
fix/bug-description       - Bug fixes
refactor/what-changed     - Code refactoring
docs/what-documented      - Documentation
test/what-tested          - Tests
```

### Daily Workflow
```powershell
# 1. Start your day - get latest code
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-task

# 3. Make changes, commit frequently
git add .
git commit -m "feat: Add specific feature"

# 4. Push your branch
git push origin feature/your-task

# 5. Create Pull Request online

# 6. After PR merged, update local main
git checkout main
git pull origin main

# 7. Delete old feature branch
git branch -d feature/your-task
```

### Commit Message Format
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, missing semicolons
- `refactor:` - Code change that neither fixes bug nor adds feature
- `test:` - Adding tests
- `chore:` - Updating build tasks, package manager configs

**Examples:**
```
feat: Add blind signature implementation to token service
fix: Resolve timezone issue in session expiry validation
docs: Update API documentation for election endpoints
refactor: Simplify database connection pooling logic
test: Add unit tests for RSA blind signature operations
chore: Update dependencies to Python 3.13 compatible versions
```

---

## 🚨 Important Rules

### ❌ Never Commit These Files:
- `.env` - Environment variables with secrets
- `*.key`, `*.pem` - Private keys
- `venv/` - Virtual environments (teammate creates their own)
- `node_modules/` - Dependencies (teammate runs `npm install`)
- `__pycache__/`, `*.pyc` - Python compiled files
- `uploads/`, `code-sheets/` - Generated content

### ✅ Always Do:
- Pull latest `main` before creating feature branch
- Test code locally before pushing
- Write meaningful commit messages
- Create Pull Request for review (don't push directly to main)
- Update documentation when adding features
- Run services and verify no errors

### ⚠️ Handle Merge Conflicts:
```powershell
# If you get merge conflicts
git checkout main
git pull origin main
git checkout your-feature-branch
git merge main

# Resolve conflicts in files
# Then:
git add .
git commit -m "fix: Resolve merge conflicts with main"
git push origin your-feature-branch
```

---

## 📊 Check Repository Status

### View Current Branch
```powershell
git branch
```

### View Remote URL
```powershell
git remote -v
```

### View Commit History
```powershell
git log --oneline -10
```

### View File Changes
```powershell
git status
git diff
```

### View What's Ignored
```powershell
git status --ignored
```

---

## 🔧 Troubleshooting

### "Permission denied (publickey)"
**Solution:** Setup SSH key or use HTTPS with token authentication

For HTTPS:
```powershell
git remote set-url origin https://username:token@github.com/username/repo.git
```

### "Large files rejected"
**Solution:** Files over 100MB are rejected by GitHub.
Check `.gitignore` excludes large uploads.

### "Merge conflict"
**Solution:** See "Handle Merge Conflicts" section above.

### "Detached HEAD state"
```powershell
git checkout main
```

### Undo Last Commit (before push)
```powershell
git reset --soft HEAD~1
```

### Undo Changes to File
```powershell
git checkout -- filename
```

---

## 📋 Pre-Push Checklist

Before pushing to main or creating PR:

- [ ] Code runs without errors locally
- [ ] All services start successfully
- [ ] Tests pass (if any exist)
- [ ] No console errors in browser
- [ ] Documentation updated (if API changed)
- [ ] No hardcoded secrets or keys
- [ ] Meaningful commit message
- [ ] `.env` not included in commit
- [ ] `git status` shows only intended changes

---

## 🎯 Next Steps After Push

1. **Share repository URL with teammate**
2. **Add teammate as collaborator** (see above)
3. **Teammate clones and sets up** (see [TEAM_HANDOFF.md](./TEAM_HANDOFF.md))
4. **Divide tasks** (see Priority list in TEAM_HANDOFF.md)
5. **Use feature branches** for all new work
6. **Create PRs** for code review
7. **Merge to main** after approval

---

## 📚 Git Resources

- **Git Cheat Sheet:** https://training.github.com/downloads/github-git-cheat-sheet/
- **Git Documentation:** https://git-scm.com/doc
- **GitHub Guides:** https://guides.github.com/
- **GitLab Docs:** https://docs.gitlab.com/ee/gitlab-basics/

---

**Repository is now ready for team collaboration! 🚀**

**Group F:** MUNASINGHE S.K. (210396E) | JAYASOORIYA D.D.M. (210250D)
