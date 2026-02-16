# Git Commit Guide

## Before Committing

### 1. Clean Up Generated Files

Run the cleanup script:

**Windows:**
```bash
cleanup_before_commit.bat
```

**Linux/Mac:**
```bash
chmod +x cleanup_before_commit.sh
./cleanup_before_commit.sh
```

This removes:
- Generated CSV files (data/, outputs/, pathway_pipeline/)
- Test/demo Python files (test_api.py, check_system_status.py, gps_test.py)
- Python cache (__pycache__, *.pyc, *.pyo)
- Virtual environments (venv/)

### 2. Verify .env is NOT Committed

```bash
# Check if .env is in .gitignore
cat .gitignore | grep ".env"

# Verify .env won't be committed
git status | grep ".env"
```

**IMPORTANT:** Never commit `.env` file (contains API keys!)
- ✅ Commit: `.env.example`
- ❌ Never commit: `.env`

### 3. Check What Will Be Committed

```bash
git status
```

Review the list. Should NOT include:
- ❌ .env file
- ❌ __pycache__ directories
- ❌ *.pyc files
- ❌ Generated CSV files
- ❌ venv/ directories
- ❌ Test files (test_*.py, check_*.py)

---

## Making the Commit

### Option 1: Commit All Changes

```bash
# Add all files (respects .gitignore)
git add .

# Check what's staged
git status

# Commit with message
git commit -m "feat: Complete supply chain tracker with real-time GPS, ETA predictions, and RAG chatbot"
```

### Option 2: Commit Specific Components

```bash
# Add specific directories
git add backend/
git add dashboard/
git add pathway_pipeline/
git add genai_rag/
git add database/
git add shared/
git add docs/

# Add configuration files
git add docker-compose.yml
git add .gitignore
git add .env.example
git add requirements.txt

# Add documentation
git add README.md
git add GETTING_STARTED.md
git add */README.md

# Commit
git commit -m "feat: Complete hackathon project implementation"
```

---

## Suggested Commit Messages

### For Complete Project
```bash
git commit -m "feat: Complete real-time supply chain tracker

- GPS simulator with realistic traffic patterns
- Pathway pipeline for ETA calculations
- FastAPI backend with 15+ endpoints
- Streamlit dashboard with live map
- Groq-powered RAG chatbot
- PostgreSQL database with telemetry tracking
- Docker compose for full stack deployment"
```

### For Bug Fixes
```bash
git commit -m "fix: Resolve database connection and merge conflicts

- Fixed GPS simulator vehicle_id constraint violation
- Fixed Pathway pipeline syntax error
- Resolved dashboard merge conflict markers
- Added SQLAlchemy for pandas database queries"
```

### For Dashboard Updates
```bash
git commit -m "feat: Enhanced dashboard with real-time integration

- Integrated live GPS telemetry from PostgreSQL
- Added ETA predictions from Pathway pipeline
- Implemented Groq-powered chatbot
- Added system health monitoring
- Real-time auto-refresh every 10 seconds"
```

---

## Push to Remote

### Push to Development Branch
```bash
# Push to development branch
git push origin development
```

### Create Pull Request
1. Go to GitHub repository
2. Click "Pull Requests"
3. Click "New Pull Request"
4. Base: `main` ← Compare: `development`
5. Add title and description
6. Request review from team lead
7. Wait for approval before merging

---

## Verify Commit

### Check Commit History
```bash
# View recent commits
git log --oneline -5

# View detailed last commit
git show HEAD
```

### Check Remote Status
```bash
# Check if pushed
git status

# View remote branches
git branch -r
```

---

## What Should Be Committed

### ✅ Source Code
- `backend/*.py`
- `dashboard/*.py`
- `pathway_pipeline/*.py`
- `genai_rag/*.py`
- `shared/*.py`

### ✅ Configuration
- `docker-compose.yml`
- `Dockerfile` (all)
- `requirements.txt` (all)
- `.env.example`
- `.gitignore`

### ✅ Database
- `database/init.sql`
- `database/README.md`

### ✅ Documentation
- `README.md`
- `GETTING_STARTED.md`
- `docs/*.md`
- Component READMEs

### ✅ Scripts
- `run_all.sh`
- `run_all.bat`
- `cleanup_before_commit.sh`
- `cleanup_before_commit.bat`

---

## What Should NOT Be Committed

### ❌ Environment Files
- `.env` (contains secrets!)

### ❌ Generated Data
- `data/*.csv`
- `data/*.json`
- `outputs/*.csv`
- `pathway_pipeline/*.csv`

### ❌ Python Cache
- `__pycache__/`
- `*.pyc`
- `*.pyo`

### ❌ Virtual Environments
- `venv/`
- `env/`
- `ENV/`

### ❌ IDE Files
- `.vscode/`
- `.idea/`

### ❌ Test/Demo Files
- `test_api.py`
- `check_system_status.py`
- `gps_test.py`

### ❌ Logs
- `logs/*.log`

---

## Quick Checklist

Before committing, verify:

- [ ] Ran cleanup script
- [ ] `.env` is NOT in git status
- [ ] No `__pycache__` directories
- [ ] No generated CSV files
- [ ] No test/demo files
- [ ] All Dockerfiles present
- [ ] All requirements.txt present
- [ ] README.md updated
- [ ] .env.example has all required keys (without values)
- [ ] docker-compose.yml is complete

---

## Emergency: Undo Last Commit

If you committed something wrong:

```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and discard changes (DANGEROUS!)
git reset --hard HEAD~1

# If already pushed, revert the commit
git revert HEAD
git push origin development
```

---

## Team Workflow

1. **Member makes changes** in their feature branch
2. **Member commits** with descriptive message
3. **Member pushes** to their feature branch
4. **Member creates PR** to development branch
5. **Team lead reviews** and approves
6. **Merge to development** after approval
7. **Test in development** branch
8. **Merge to main** when ready for demo

---

## Final Check Before Demo

```bash
# Ensure you're on the right branch
git branch

# Pull latest changes
git pull origin development

# Verify all services work
docker-compose up -d

# Check system status
python check_system_status.py

# Open dashboard
# http://localhost:8501
```

Good luck with your hackathon! 🚀
