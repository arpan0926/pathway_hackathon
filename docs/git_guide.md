# Git Workflow Guide for Team Members

## First Time Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AYUSH-0305/pathway_hackathon.git
cd pathway_hackathon
```

### 2. Switch to Development Branch
```bash
git checkout development
```

### 3. Verify You're on Development Branch
```bash
git branch
# You should see: * development
```

## Daily Workflow - Feature Branch & Pull Requests

### Step 1: Create Your Feature Branch
```bash
# Make sure you're on development
git checkout development
git pull origin development

# Create your feature branch
# Use format: memberX/feature-name
git checkout -b member1/eta-calculation
# or
git checkout -b member2/gps-simulator
# or
git checkout -b member3/dashboard-updates
```

### Step 2: Check What Files You Changed
```bash
git status
# This shows all modified, added, or deleted files
```

### Step 3: Stage Your Changes
```bash
# To add all changes
git add .

# OR to add specific files only
git add pathway_pipeline/pipeline.py
git add backend/simulator.py
```

### Step 4: Commit Your Changes
```bash
git commit -m "Brief description of what you did"

# Examples:
git commit -m "Added GPS data ingestion logic"
git commit -m "Implemented ETA calculation"
git commit -m "Created dashboard map component"
git commit -m "Fixed alert logic bug"
```

### Step 5: Push Your Feature Branch
```bash
# Push to YOUR branch (not development!)
git push origin member1/eta-calculation
```

### Step 6: Create Pull Request on GitHub
1. Go to https://github.com/AYUSH-0305/pathway_hackathon
2. Click "Pull requests" tab
3. Click "New pull request"
4. **Base**: `development`
5. **Compare**: `member1/eta-calculation` (your branch)
6. Click "Create pull request"
7. Add title and description
8. Assign AYUSH as reviewer
9. Click "Create pull request"

### Step 7: Wait for Approval
- AYUSH will review your code
- He may request changes
- Once approved, he will merge it
- You'll get a notification

### Step 8: After Merge - Update Your Local
```bash
# Switch back to development
git checkout development

# Pull the merged changes
git pull origin development

# Delete your old feature branch (optional)
git branch -d member1/eta-calculation
```

## Complete Example

```bash
# 1. Start from development branch
git checkout development
git pull origin development

# 2. Create your feature branch
git checkout -b member2/gps-simulator

# 3. Make your changes, then check status
git status

# 4. Add your changes
git add .

# 5. Commit with a message
git commit -m "Implemented GPS simulator with route generation"

# 6. Push to YOUR branch
git push origin member2/gps-simulator

# 7. Go to GitHub and create Pull Request
# 8. Wait for AYUSH to review and approve
# 9. After merge, update your local development
git checkout development
git pull origin development
```

## Handling Merge Conflicts

If you get a conflict when pulling:

```bash
# 1. Git will tell you which files have conflicts
# 2. Open those files and look for conflict markers:
#    <<<<<<< HEAD
#    Your changes
#    =======
#    Someone else's changes
#    >>>>>>> 

# 3. Edit the file to keep the correct code
# 4. Remove the conflict markers
# 5. Stage the resolved files
git add <conflicted-file>

# 6. Complete the merge
git commit -m "Resolved merge conflict in <file>"

# 7. Push
git push origin development
```

## Quick Commands Reference

```bash
# Check current branch
git branch

# Switch to development
git checkout development

# See what changed
git status

# See detailed changes
git diff

# Add all changes
git add .

# Commit changes
git commit -m "Your message"

# Pull latest
git pull origin development

# Push changes
git push origin development

# View commit history
git log --oneline

# Discard local changes (careful!)
git checkout -- <file>
```

## Best Practices

1. **Commit Often**: Make small, frequent commits rather than one huge commit
2. **Write Clear Messages**: Describe what you did, not how you did it
3. **Pull Before Push**: Always pull latest changes before pushing
4. **Test Before Commit**: Make sure your code works before committing
5. **Communicate**: Let team know if you're working on shared files

## Common Issues

### "Permission denied" or "Authentication failed"
```bash
# Make sure you have access to the repository
# You may need to set up SSH keys or use HTTPS with credentials
```

### "Your branch is behind"
```bash
# Just pull the latest changes
git pull origin development
```

### "Your branch is ahead"
```bash
# You have local commits that aren't pushed yet
git push origin development
```

### "Merge conflict"
```bash
# Follow the "Handling Merge Conflicts" section above
```

## Need Help?
- Ask your team members
- Check: `git status` to see current state
- Check: `git log` to see recent commits
- Use: `git --help` for command help
