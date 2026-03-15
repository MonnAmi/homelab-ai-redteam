# 📋 GitHub Setup Instructions — Step by Step

Complete guide to create your GitHub profile and repositories from scratch.

---

## STEP 1 — Create GitHub Account (if needed)

1. Go to https://github.com
2. Click **Sign up**
3. Username suggestion: something professional
   - `[yourname]-sec`
   - `[yourname]-redteam`
   - `[yourname]-infosec`
4. Verify email

---

## STEP 2 — Create Your Profile README

This is the first thing Praetorian will see.

1. Go to: https://github.com/new
2. Repository name = **YOUR EXACT USERNAME**
   - Example: if username is `johnsmith` → repo name = `johnsmith`
3. Set to **Public**
4. Check ✅ **Add a README file**
5. Click **Create repository**
6. Click the pencil ✏️ icon to edit README.md
7. Delete everything
8. Paste contents from: `profile/README.md`
9. Replace placeholders:
   - `[YOUR NAME]` → your real name
   - `[your.email@gmail.com]` → your email
   - `YOUR_PROFILE` → your LinkedIn username
10. Click **Commit changes**

---

## STEP 3 — Create homelab-ai-redteam Repository

1. Go to: https://github.com/new
2. Repository name: `homelab-ai-redteam`
3. Description: `Private AI-powered red team homelab on VMware ESXi with GPU passthrough`
4. Set to **Public**
5. Check ✅ **Add a README file**
6. Click **Create repository**

### Add README:
1. Click pencil ✏️ on README.md
2. Paste contents from: `homelab-ai-redteam/README.md`
3. Commit changes

### Add lab-manager.sh script:
1. Click **Add file** → **Create new file**
2. Name: `scripts/lab-manager.sh`
3. Paste contents from: `homelab-ai-redteam/scripts/lab-manager.sh`
4. Commit changes

---

## STEP 4 — Create ai-security-pipeline Repository

1. Go to: https://github.com/new
2. Repository name: `ai-security-pipeline`
3. Description: `Private RAG pipeline — feed security books into local AI (Ollama + Qdrant + DeepSeek R1)`
4. Set to **Public**
5. Check ✅ **Add a README file**
6. Click **Create repository**

### Add files one by one:

**README.md:**
1. Click pencil ✏️ on README.md
2. Paste contents from: `ai-security-pipeline/README.md`
3. Commit changes

**ingest.py:**
1. Click **Add file** → **Create new file**
2. Name: `ingest.py`
3. Paste contents from: `ai-security-pipeline/ingest.py`
4. Commit changes

**query.py:**
1. Click **Add file** → **Create new file**
2. Name: `query.py`
3. Paste contents from: `ai-security-pipeline/query.py`
4. Commit changes

---

## STEP 5 — Create ad-exploit-capstone Repository

1. Go to: https://github.com/new
2. Repository name: `ad-exploit-capstone`
3. Description: `Active Directory attack chain simulation with MITRE ATT&CK mapping`
4. Set to **Public**
5. Check ✅ **Add a README file**
6. Click **Create repository**
7. Paste contents from: `ad-exploit-capstone/README.md`
8. Commit changes

---

## STEP 6 — Pin Your Repositories

This makes them visible on your profile.

1. Go to your profile: https://github.com/YOUR_USERNAME
2. Click **Customize your pins**
3. Select all 3 repos:
   - `homelab-ai-redteam`
   - `ai-security-pipeline`
   - `ad-exploit-capstone`
4. Click **Save pins**

---

## STEP 7 — Add Topics/Tags to Each Repo

Topics help people find your work and show expertise.

For each repo → click ⚙️ gear next to **About**:

**homelab-ai-redteam topics:**
```
vmware-esxi, homelab, gpu-passthrough, nvidia, ollama,
ubuntu, red-team, cybersecurity, deepseek, llm
```

**ai-security-pipeline topics:**
```
rag, ollama, qdrant, python, llm, cybersecurity,
private-ai, deepseek-r1, vector-database, offline-ai
```

**ad-exploit-capstone topics:**
```
active-directory, red-team, penetration-testing,
mitre-attack, kerberoasting, cybersecurity, offensive-security
```

---

## STEP 8 — Final Profile Checklist

```
✅ Profile README visible on your profile page
✅ Profile photo added (professional)
✅ Bio filled in
✅ Location added
✅ All 3 repos pinned
✅ Topics added to each repo
✅ Email visible (or contact method)
✅ LinkedIn linked
```

---

## STEP 9 — Link in Praetorian Application

In the GitHub/Portfolio field:
```
https://github.com/YOUR_USERNAME
```

---

## 📋 Replace These Placeholders

Before submitting to Praetorian, search and replace in all files:

| Placeholder | Replace With |
|---|---|
| `[YOUR NAME]` | Your full name |
| `YOUR_USERNAME` | Your GitHub username |
| `YOUR_PROFILE` | Your LinkedIn username |
| `[your.email@gmail.com]` | Your email |
| `192.168.1.x` | Your actual VM IPs (optional — can leave generic) |

---

## ✅ Done!

Your GitHub will show:
- Professional profile with homelab architecture
- Working GPU passthrough documentation
- Real Python code for AI pipeline
- Active Directory attack chain research
- Everything Praetorian wants to see 🎯
