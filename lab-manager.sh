#!/bin/bash
# lab-manager.sh — ESXi VM lifecycle manager
# Controls AI VMs on VMware ESXi via vim-cmd
# Usage: ./lab-manager.sh [command]

ESXI_HOST="192.168.1.10"
ESXI_USER="root"

# VM Display Names (must match ESXi)
VM_LLM="ubkleinai"          # VM3 — LLM Brain (RTX 3060)
VM_INGESTOR="ingestor-vm"   # VM1 — Book Ingestor
VM_VECTORDB="vectordb-vm"   # VM2 — Qdrant VectorDB
VM_AGENT="agent-vm"         # VM4 — Open WebUI / FastAPI

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Helpers ──────────────────────────────────────────────────────────────────

esxi_cmd() {
    ssh "${ESXI_USER}@${ESXI_HOST}" "$@"
}

get_vmid() {
    local vm_name="$1"
    esxi_cmd "vim-cmd vmsvc/getallvms 2>/dev/null | grep '${vm_name}' | awk '{print \$1}'"
}

vm_power_on() {
    local vm_name="$1"
    local vmid
    vmid=$(get_vmid "$vm_name")
    if [ -z "$vmid" ]; then
        echo -e "${RED}[!] VM not found: ${vm_name}${NC}"
        return 1
    fi
    echo -e "${CYAN}[>] Starting ${vm_name} (ID: ${vmid})...${NC}"
    esxi_cmd "vim-cmd vmsvc/power.on ${vmid}" > /dev/null 2>&1
    echo -e "${GREEN}[✓] ${vm_name} powered on${NC}"
}

vm_power_off() {
    local vm_name="$1"
    local vmid
    vmid=$(get_vmid "$vm_name")
    if [ -z "$vmid" ]; then
        echo -e "${RED}[!] VM not found: ${vm_name}${NC}"
        return 1
    fi
    echo -e "${YELLOW}[>] Shutting down ${vm_name} (ID: ${vmid})...${NC}"
    esxi_cmd "vim-cmd vmsvc/power.shutdown ${vmid}" > /dev/null 2>&1
    echo -e "${GREEN}[✓] ${vm_name} shutdown initiated${NC}"
}

vm_status() {
    local vm_name="$1"
    local vmid
    vmid=$(get_vmid "$vm_name")
    if [ -z "$vmid" ]; then
        echo -e "  ${RED}✗ ${vm_name}: NOT FOUND${NC}"
        return
    fi
    local state
    state=$(esxi_cmd "vim-cmd vmsvc/power.getstate ${vmid} 2>/dev/null | tail -1")
    if echo "$state" | grep -q "Powered on"; then
        echo -e "  ${GREEN}✓ ${vm_name}: RUNNING${NC}"
    else
        echo -e "  ${RED}✗ ${vm_name}: STOPPED${NC}"
    fi
}

# ─── Commands ─────────────────────────────────────────────────────────────────

cmd_ai_start() {
    echo -e "${CYAN}[*] Starting AI stack...${NC}"
    vm_power_on "$VM_LLM"
    sleep 5
    vm_power_on "$VM_VECTORDB"
    sleep 3
    vm_power_on "$VM_INGESTOR"
    sleep 3
    vm_power_on "$VM_AGENT"
    echo -e "\n${GREEN}[✓] AI stack started. Allow ~2 minutes for full boot.${NC}"
    echo -e "${CYAN}[*] Open WebUI will be at: http://192.168.1.14:3000${NC}"
}

cmd_ai_stop() {
    echo -e "${YELLOW}[*] Stopping AI stack...${NC}"
    vm_power_off "$VM_AGENT"
    vm_power_off "$VM_INGESTOR"
    vm_power_off "$VM_VECTORDB"
    vm_power_off "$VM_LLM"
    echo -e "${GREEN}[✓] AI stack stopped. RAM freed for other VMs.${NC}"
}

cmd_status() {
    echo -e "${CYAN}[*] AI VM Status:${NC}"
    vm_status "$VM_LLM"
    vm_status "$VM_VECTORDB"
    vm_status "$VM_INGESTOR"
    vm_status "$VM_AGENT"
}

cmd_gpu_check() {
    echo -e "${CYAN}[*] Checking GPU status on ${VM_LLM}...${NC}"
    ssh "grossbruder@192.168.1.13" "nvidia-smi"
}

cmd_raid_check() {
    echo -e "${CYAN}[*] RAID health check...${NC}"
    esxi_cmd "esxcli storage core device list | grep -i 'toshiba\|hdd\|state'"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

case "$1" in
    ai-start)   cmd_ai_start ;;
    ai-stop)    cmd_ai_stop ;;
    status)     cmd_status ;;
    gpu-check)  cmd_gpu_check ;;
    raid-check) cmd_raid_check ;;
    *)
        echo -e "${CYAN}Homelab AI Manager${NC}"
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  ai-start    Start all 4 AI VMs"
        echo "  ai-stop     Stop all 4 AI VMs (free RAM)"
        echo "  status      Show VM power states"
        echo "  gpu-check   Check RTX 3060 status"
        echo "  raid-check  Check RAID 5 health"
        ;;
esac
