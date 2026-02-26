# Branch Protection Setup Guide

## For Repository Owner (AYUSH)

### Why Branch Protection?
- Prevents team members from pushing directly to `development` and `main`
- Requires Pull Requests for all changes
- You review and approve all code before it's merged
- Maintains code quality and prevents conflicts

---

## Setup Instructions

### Step 1: Go to Repository Settings
1. Visit: https://github.com/AYUSH-0305/pathway_hackathon
2. Click **Settings** (top navigation)
3. Click **Branches** (left sidebar)

### Step 2: Protect `development` Branch
1. Click **Add rule** under "Branch protection rules"
2. **Branch name pattern**: `development`
3. Enable these settings:

#### Required Settings:
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  
- ✅ **Restrict who can push to matching branches**
  - Click "Restrict pushes that create matching branches"
  - Add only yourself (AYUSH) to the list
  - This prevents direct pushes from team members

- ✅ **Do not allow bypassing the above settings**
  - Make sure this is checked
  - Don't add anyone to bypass list

#### Optional Settings:
- ⚪ Require status checks to pass (if you have CI/CD)
- ⚪ Require conversation resolution before merging
- ⚪ Require signed commits

4. Click **Create** or **Save changes**

### Step 3: Protect `main` Branch
Repeat the same steps for `main` branch:
- **Branch name pattern**: `main`
- Same settings as `development`

---

## How It Works Now

### Team Members CANNOT:
- ❌ Push directly to `development`
- ❌ Push directly to `main`
- ❌ Merge their own Pull Requests
- ❌ Bypass your review

### Team Members CAN:
- ✅ Create their own feature branches
- ✅ Push to their feature branches
- ✅ Create Pull Requests
- ✅ View and comment on PRs

### You (AYUSH) CAN:
- ✅ Review all Pull Requests
- ✅ Request changes
- ✅ Approve and merge PRs
- ✅ Push directly (if needed)
- ✅ Manage all branches

---

## New Workflow for Team

### Member Creates Feature Branch
```bash
git checkout development
git pull origin development
git checkout -b member1/my-feature
# Make changes
git add .
git commit -m "My changes"
git push origin member1/my-feature
```

### Member Creates Pull Request
1. Go to GitHub
2. Click "Pull requests"
3. Click "New pull request"
4. Base: `development`, Compare: `member1/my-feature`
5. Create PR and assign you as reviewer

### You Review and Approve
1. Receive notification
2. Review code changes
3. Add comments or request changes
4. Approve PR
5. Click "Merge pull request"

### Member Updates Local After Merge
```bash
git checkout development
git pull origin development
```

---

## Handling Pull Requests

### When You Receive a PR:

#### 1. Review the Code
- Check for bugs
- Verify it follows project structure
- Ensure it doesn't break existing code
- Check if tests pass (if any)

#### 2. Add Comments
- Click on specific lines to add comments
- Ask questions if something is unclear
- Suggest improvements

#### 3. Request Changes (if needed)
- Click "Request changes"
- Member fixes issues
- Pushes new commits to same branch
- PR updates automatically

#### 4. Approve and Merge
- Click "Approve"
- Click "Merge pull request"
- Choose merge method:
  - **Merge commit** (recommended) - keeps full history
  - **Squash and merge** - combines all commits into one
  - **Rebase and merge** - linear history
- Click "Confirm merge"

#### 5. Delete Branch (optional)
- After merge, GitHub will suggest deleting the feature branch
- Click "Delete branch" to keep repo clean

---

## Troubleshooting

### Team Member Says "Permission Denied"
✅ This is correct! They should create a PR instead.

### Team Member Pushed to Development Before Protection
1. Revert the commit if needed
2. Ask them to create a feature branch
3. Cherry-pick their changes to the feature branch
4. Create PR

### You Need to Push Directly (Emergency)
You can still push directly as the owner, but try to use PRs too for consistency.

### Member's PR Has Conflicts
1. Ask member to:
```bash
git checkout development
git pull origin development
git checkout their-feature-branch
git merge development
# Resolve conflicts
git add .
git commit -m "Resolved conflicts"
git push origin their-feature-branch
```
2. PR will update automatically

---

## Best Practices

### For You (AYUSH):
- Review PRs within 24 hours
- Provide constructive feedback
- Approve quickly if code is good
- Use PR comments for discussions
- Keep `development` stable

### For Team Members:
- Create small, focused PRs
- Write clear PR descriptions
- Test code before creating PR
- Respond to review comments
- Don't create huge PRs (hard to review)

### PR Naming Convention:
- `[Member1] Implement ETA calculation`
- `[Member2] Add GPS simulator`
- `[Member3] Update dashboard UI`
- `[Member4] Add RAG chatbot`

---

## Summary

✅ Branch protection prevents direct pushes  
✅ All changes go through Pull Requests  
✅ You review and approve everything  
✅ Maintains code quality  
✅ Prevents conflicts and bugs  

**Your repository is now protected! 🔒**
