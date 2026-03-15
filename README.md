# 🏠 Homelab AI Red Team Platform

> A fully private, air-gapped AI-powered red team infrastructure built on VMware ESXi.
> No cloud. No telemetry. No trust.

---

## 🚧 Build Status

> **This project is actively being built.** The AI Brain VM is fully operational. Remaining VMs are being configured.

| Component | Status | Notes |
|---|---|---|
| 🖥️ ESXi Hypervisor | ![Done](https://img.shields.io/badge/status-DONE-brightgreen) | Running on Supermicro H12SSL-CT |
| 🎮 RTX 3060 GPU Passthrough | ![Done](https://img.shields.io/badge/status-DONE-brightgreen) | Driver 580 + CUDA 13.0 confirmed |
| 🧠 VM3 — LLM Brain | ![Done](https://img.shields.io/badge/status-DONE-brightgreen) | DeepSeek R1 14B running at ~45 tok/s |
| 🗄️ VM2 — Vector Database | ![In Progress](https://img.shields.io/badge/status-IN%20PROGRESS-orange) | Qdrant setup pending |
| 📥 VM1 — Ingestor | ![In Progress](https://img.shields.io/badge/status-IN%20PROGRESS-orange) | RAG pipeline pending |
| 🌐 VM4 — Agent / Open WebUI | ![In Progress](https://img.shields.io/badge/status-IN%20PROGRESS-orange) | Chat interface pending |
| 🔒 Air-Gap VLAN | ![Planned](https://img.shields.io/badge/status-PLANNED-blue) | Network isolation config |
| 📚 Book Ingestion | ![Planned](https://img.shields.io/badge/status-PLANNED-blue) | 10TB security library |

---

## ✅ What Works Right Now

```
nvidia-smi output (confirmed working):
────────────────────────────────────────────────────────────────
NVIDIA-SMI 580.126.09    Driver Version: 580.126.09    CUDA Version: 13.0
GPU:    NVIDIA GeForce RTX 3060
VRAM:   9495MiB / 12288MiB  ← DeepSeek R1 14B loaded
Speed:  ~45 tokens/second
Proc:   /usr/local/bin/ollama   PID 23677   GPU Memory: 9486MiB
Temp:   43C    Power: 9W idle / 170W max
────────────────────────────────────────────────────────────────
```

**VM3 (ubkleinai) is fully operational:**
- ✅ Ubuntu 22.04 LTS
- ✅ NVIDIA driver 580 + CUDA 13.0
- ✅ Ollama installed and running
- ✅ DeepSeek R1 14B — 9.4GB VRAM loaded on GPU
- ✅ RTX 3060 PCIe passthrough confirmed

---

## 🗺️ Roadmap

```
Phase 1 — AI Brain          ████████████████████  100% ✅ DONE
Phase 2 — Vector DB         ░░░░░░░░░░░░░░░░░░░░    0% ⏳ Tonight
Phase 3 — Book Ingestor     ░░░░░░░░░░░░░░░░░░░░    0% ⏳ Tonight
Phase 4 — Agent / WebUI     ░░░░░░░░░░░░░░░░░░░░    0% ⏳ Tonight
Phase 5 — Air-Gap Network   ░░░░░░░░░░░░░░░░░░░░    0% 📅 Planned
Phase 6 — Book Library      ░░░░░░░░░░░░░░░░░░░░    0% 📅 Planned
```

---

## 📋 Table of Contents

- [Hardware](#hardware)
- [Storage Layout](#storage-layout)
- [VM Architecture](#vm-architecture)
- [GPU Passthrough](#gpu-passthrough-rtx-3060)
- [Network Config](#network-config)
- [VM Setup Guides](#vm-setup-guides)
- [AI Stack](#ai-stack)
- [Scripts](#scripts)

---

## 🖥️ Hardware

| Component | Spec |
|---|---|
| **CPU** | AMD EPYC 7282 — 16c/32t, 2.8→3.2GHz, 120W |
| **Motherboard** | Supermicro H12SSL-CT ATX |
| **RAM** | 2 × Samsung 64GB DDR4-3200 ECC RDIMM = 128GB |
| **GPU** | ASUS RTX 3060 Dual OC 12GB GDDR6 PCIe 4.0 |
| **NVMe** | 2 × Samsung 990 PRO 4TB PCIe 4.0 = 8TB |
| **HDD** | 3 × Toshiba X300 14TB 7200RPM SATA |
| **RAID** | RAID 5 → 28TB usable |
| **Hypervisor** | VMware ESXi |

---

## 💾 Storage Layout

```
NVMe (8TB total — fast, AI workloads):
├── NVMe Disk 1 (4TB)
│   ├── VM-AI-BRAIN datastore    2TB  ✅ Active
│   └── VM-AI-STACK datastore    2TB  ⏳ Pending
└── NVMe Disk 2 (4TB)
    ├── AI Model Store           4TB  ✅ Active (DeepSeek R1 stored here)
    └── Vector DB storage        2TB  ⏳ Pending

RAID 5 HDD (28TB usable — bulk/cold storage):
├── AI-Books-Store              10TB  📅 Planned
├── VM-OS-Disks                  3TB  ✅ Active
└── Backup-Archive              15TB  📅 Planned
```

---

## 🏗️ VM Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   VMware ESXi Host                      │
│          AMD EPYC 7282 | 128GB RAM | RTX 3060           │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  VM1         │  │  VM2         │                     │
│  │  INGESTOR    │  │  VECTOR DB   │                     │
│  │  ⏳ Pending  │  │  ⏳ Pending  │                     │
│  │  192.168.1.11│  │  192.168.1.12│                     │
│  └──────────────┘  └──────────────┘                     │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  VM3         │  │  VM4         │                     │
│  │  LLM BRAIN   │  │  AGENT/UI    │                     │
│  │  ✅ RUNNING  │  │  ⏳ Pending  │                     │
│  │  192.168.1.13│  │  192.168.1.14│                     │
│  │  RTX 3060 ✅ │  │              │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

### VM Specs

| | VM1 Ingestor | VM2 VectorDB | VM3 LLM Brain | VM4 Agent UI |
|---|---|---|---|---|
| **Hostname** | ingestor-vm | vectordb-vm | ubkleinai | agent-vm |
| **OS** | Ubuntu 22.04 | Ubuntu 22.04 | Ubuntu 22.04 | Ubuntu 22.04 |
| **vCPU** | 6 | 4 | 16 | 6 |
| **RAM** | 16GB | 16GB | 40GB | 8GB |
| **Data Disk** | 10TB RAID | 2TB NVMe | 4TB NVMe | 2TB NVMe |
| **GPU** | ❌ | ❌ | ✅ RTX 3060 | ❌ |
| **Status** | ⏳ Pending | ⏳ Pending | ✅ Running | ⏳ Pending |

---

## 🎮 GPU Passthrough (RTX 3060)

> ✅ **CONFIRMED WORKING** — See nvidia-smi output above

### Steps That Were Done

**Step 1 — BIOS (Supermicro H12SSL-CT):**
```
Advanced → AMD CBS → NBIO → IOMMU → Enabled
```

**Step 2 — ESXi Passthrough:**
```
ESXi UI → Host → Manage → Hardware → PCI Devices
RTX 3060 → Toggle Passthrough = ON → Reboot ESXi
VM3 Settings → Add PCI Device → RTX 3060
Memory Reservation = ALL (40GB)
```

**Step 3 — Ubuntu Driver:**
```bash
sudo apt install nvidia-driver-545 -y
sudo reboot
nvidia-smi   # confirmed ✅
```

---

## 🌐 Network Config

```
ESXi Host:    192.168.1.10
VM1 Ingestor: 192.168.1.11  ⏳
VM2 VectorDB: 192.168.1.12  ⏳
VM3 LLM:      192.168.1.13  ✅ Running
VM4 Agent:    192.168.1.14  ⏳
```

---

## 🔧 VM Setup Guides

### ✅ VM3 — LLM Brain (COMPLETE)

```bash
# Ollama installed and running
curl -fsSL https://ollama.ai/install.sh | sh

# DeepSeek R1 14B pulled
ollama pull deepseek-r1:14b

# Verify GPU usage
nvidia-smi
# Process: /usr/local/bin/ollama  9486MiB ✅
```

### ⏳ VM2 — Vector Database (Pending)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Run Qdrant on NVMe
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 \
  -v /mnt/nvme/qdrant:/qdrant/storage \
  qdrant/qdrant
```

### ⏳ VM1 — Ingestor (Pending)

```bash
# Install dependencies
pip install pymupdf sentence-transformers \
    qdrant-client llama-index watchdog tqdm \
    --break-system-packages

# Run ingestion pipeline
python3 ingest.py --books-path /mnt/books \
                  --qdrant-host 192.168.1.12
```

### ⏳ VM4 — Open WebUI (Pending)

```bash
# Run Open WebUI — private ChatGPT interface
docker run -d \
  --name open-webui \
  --restart always \
  -p 3000:8080 \
  -e OLLAMA_BASE_URL=http://192.168.1.13:11434 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Access at: http://192.168.1.14:3000
```

---

## 🤖 AI Stack

| Component | Details | Status |
|---|---|---|
| **Ollama** | Model manager | ✅ Running |
| **DeepSeek R1 14B** | Primary LLM | ✅ GPU accelerated |
| **NVIDIA Driver** | 580.126.09 | ✅ Installed |
| **CUDA** | 13.0 | ✅ Ready |
| **Qdrant** | Vector database | ⏳ Pending |
| **Open WebUI** | Chat interface | ⏳ Pending |
| **FastAPI** | Private API | ⏳ Pending |
| **Book Pipeline** | 10TB RAG library | 📅 Planned |

### Pipeline (When Complete)
```
RAID (PDFs/Books 10TB)  📅
        ↓
VM1 Ingestor            ⏳
        ↓
VM2 VectorDB (Qdrant)   ⏳
        ↓
VM3 LLM Brain ✅  ←── Only this part is running today
        ↓
VM4 Agent/UI            ⏳
```

---

## 📜 Scripts

| Script | Purpose | Status |
|---|---|---|
| `scripts/lab-manager.sh` | Start/stop AI VMs via ESXi | ✅ Ready |
| `ai-security-pipeline/ingest.py` | PDF → Qdrant pipeline | ⏳ Pending test |
| `ai-security-pipeline/query.py` | CLI RAG query interface | ⏳ Pending test |

---

## 🔐 Privacy & Security

```
✅ 100% offline — no internet required after setup
✅ No cloud API keys — all models run locally
⏳ Air-gapped VLAN — coming soon
⏳ UFW firewall on all VMs — coming soon
✅ ECC RAM — data integrity on all operations
✅ RAID 5 — fault tolerant storage
```

---

## 📄 Full Documentation

[📥 Download Complete Build Documentation](./Homelab_AI_RedTeam_Documentation mein.docx)

Includes: Hardware specs, GPU passthrough steps, VM setup guides, AI stack configuration, network layout, GitHub setup, knowledge base strategy, and full build checklist.

---

## ⚠️ Known Risks

- RAID 5 with 3 × 14TB HDDs — high URE risk during rebuild. Adding 4th drive → RAID 6 planned.
- GPU passthrough requires Memory Reservation = ALL in ESXi VM settings.
- Mixed RAM brands (Samsung + Hynix + Micron) confirmed working — never mix RDIMM + LRDIMM.

---

*Built with: Ubuntu 22.04 LTS | VMware ESXi | Ollama | DeepSeek R1 | Qdrant | Docker*
*Last updated: March 2026*
