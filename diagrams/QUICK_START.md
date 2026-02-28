# Quick Start - Viewing Diagrams

## 🚀 Three Ways to View Diagrams

### Method 1: Open All Diagrams at Once
```bash
python diagrams/view_diagrams.py
```
Opens all 6 diagrams in your default image viewer.

---

### Method 2: Interactive Menu
```bash
python diagrams/show_diagram.py
```
Interactive menu to select specific diagrams to view.

---

### Method 3: Manual (Windows)
```bash
# Open specific diagram
start diagrams/01_system_overview.png

# Or navigate to folder
explorer diagrams
```

---

## 📊 Available Diagrams

| # | File Name | Description | Size |
|---|-----------|-------------|------|
| 1 | `01_system_overview.png` | High-level architecture | 54 KB |
| 2 | `02_verification_pipeline.png` | 7-stage verification process | 29 KB |
| 3 | `03_self_hosted_architecture.png` | Self-hosted vs external API | 58 KB |
| 4 | `04_multilingual_pipeline.png` | 19 languages support | 67 KB |
| 5 | `05_deployment_architecture.png` | Production deployment | 95 KB |
| 6 | `06_data_flow.png` | Concrete example | 11 KB |

---

## 🔄 Regenerate Diagrams

If you need to modify or regenerate:

```bash
# Edit the generation script
notepad diagrams/generate_architecture.py

# Regenerate all diagrams
python diagrams/generate_architecture.py

# View the new diagrams
python diagrams/view_diagrams.py
```

---

## 🎯 For Presentations

**Recommended order:**
1. System Overview (big picture)
2. Verification Pipeline (how it works)
3. Self-Hosted Architecture (cost advantage)
4. Multilingual Pipeline (unique feature)
5. Data Flow (concrete example)
6. Deployment Architecture (production-ready)

**Key points to highlight:**
- Self-hosted: $0 vs $1,500/month
- Multilingual: 19 languages (9 Indian)
- Accuracy: 95% with NLI
- Production-ready: Docker + monitoring

---

## 📁 Files in This Folder

```
diagrams/
├── 01_system_overview.png              ← Generated diagram
├── 02_verification_pipeline.png        ← Generated diagram
├── 03_self_hosted_architecture.png     ← Generated diagram
├── 04_multilingual_pipeline.png        ← Generated diagram
├── 05_deployment_architecture.png      ← Generated diagram
├── 06_data_flow.png                    ← Generated diagram
├── generate_architecture.py            ← Generation script
├── view_diagrams.py                    ← View all diagrams
├── show_diagram.py                     ← Interactive viewer
├── README.md                           ← Full documentation
└── QUICK_START.md                      ← This file
```

---

## 💡 Tips

- **For presentations**: Use `view_diagrams.py` to open all at once
- **For review**: Use `show_diagram.py` for interactive selection
- **For sharing**: PNG files are in `diagrams/` folder
- **For editing**: Modify `generate_architecture.py` and regenerate

---

## ✅ You're Ready!

All diagrams are generated and ready for your mentor presentation. Good luck! 🚀
