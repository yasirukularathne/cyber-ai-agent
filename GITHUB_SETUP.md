# How to Push Your Project to GitHub

## Step-by-Step Instructions

### **Step 1: Initialize Git Repository (Run Once)**

```bash
cd c:\Users\yasiru\Desktop\cyber-ai-agent
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

**Example:**
```bash
git config user.name "Yasiru"
git config user.email "yasiru@example.com"
```

---

### **Step 2: Create .gitignore (Optional but Recommended)**

Create a file named `.gitignore` in the project root with this content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment files
.env
.env.local

# Large files
*.csv
trained_models/
*.pkl
*.keras
*.h5

# OS
.DS_Store
Thumbs.db
```

---

### **Step 3: Add All Files to Git**

```bash
git add .
```

**Check what will be added:**
```bash
git status
```

---

### **Step 4: Create First Commit**

```bash
git commit -m "Initial commit: Cyber AI Agent v2.0.0 - Network threat detection system"
```

**Or a more detailed commit:**
```bash
git commit -m "Initial commit: Cyber AI Agent v2.0.0

- Complete ML pipeline with 4 training notebooks
- Backend: FastAPI with 8-layer threat detection
- Frontend: React + Vite dashboard
- Models: XGBoost (94.2%), BERT (91.7%), Autoencoder (85.6%)
- Ensemble accuracy: 95.2%"
```

---

### **Step 5: Create GitHub Repository**

1. Go to **https://github.com/new**
2. **Repository name:** `cyber-ai-agent`
3. **Description:** Network intrusion detection system using ensemble AI
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (you already have these)
6. Click **"Create repository"**

---

### **Step 6: Connect Local Git to GitHub**

Copy the commands GitHub shows you. They'll look like this:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cyber-ai-agent.git
git push -u origin main
```

**Replace `YOUR-USERNAME`** with your actual GitHub username!

**Example:**
```bash
git branch -M main
git remote add origin https://github.com/yasiru/cyber-ai-agent.git
git push -u origin main
```

---

### **Step 7: Push to GitHub (First Time)**

When you run the `git push` command above, GitHub will ask for authentication:

**Option A: Personal Access Token (Recommended)**
1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `GitHub CLI Token`
4. Select scopes: `repo` (full control of private/public repos)
5. Copy the token
6. Paste it when asked for password in terminal

**Option B: SSH Key**
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your.email@example.com"`
2. Press Enter for default path
3. Create a passphrase (optional)
4. Add to GitHub: https://github.com/settings/ssh/new
5. Use SSH URL: `git@github.com:YOUR-USERNAME/cyber-ai-agent.git`

---

## **Complete Commands (Copy & Paste)**

If you want to run everything at once, paste this into PowerShell:

```powershell
# Navigate to project
cd "c:\Users\yasiru\Desktop\cyber-ai-agent"

# Initialize Git
git init
git config user.name "Yasiru"
git config user.email "your-email@example.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Cyber AI Agent v2.0.0 - Network threat detection system"

# Verify commit
git log --oneline
```

**Then add the remote and push** (after creating repo on GitHub):

```powershell
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cyber-ai-agent.git
git push -u origin main
```

---

## **After First Push: Future Updates**

Once set up, to push future changes:

```bash
# Make changes to files...

# Stage and commit
git add .
git commit -m "Your commit message here"

# Push to GitHub
git push
```

---

## **Useful Git Commands**

```bash
# Check status
git status

# View commit history
git log --oneline

# View what changed
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See remote URL
git remote -v

# Check current branch
git branch
```

---

## **If You Get Errors**

**Error: "fatal: not a git repository"**
→ Run `git init` first

**Error: "authentication failed"**
→ Use Personal Access Token instead of password

**Error: "rejected (non-fast-forward)"**
→ Run `git pull origin main` first, then `git push`

---

## **What Gets Uploaded to GitHub?**

✅ **All code files** (*.py, *.jsx, *.md)  
✅ **Notebooks** (*.ipynb)  
✅ **Configuration** (requirements.txt, package.json, etc.)  
✅ **Documentation** (README.md, PROJECT_REPORT.md, etc.)  
❌ **Large model files** (blocked by .gitignore)  
❌ **Dataset CSV** (blocked by .gitignore)  
❌ **Node modules** (blocked by .gitignore)  
❌ **Pycache/venv** (blocked by .gitignore)  

---

## **Next: Share Your Repository**

After pushing, share the GitHub URL:
```
https://github.com/YOUR-USERNAME/cyber-ai-agent
```

Add this link to your project report and presentation! 🚀

