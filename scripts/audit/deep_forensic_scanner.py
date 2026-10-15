import os
import sys
import hashlib
import json
import csv
import re
from pathlib import Path
import subprocess

REPO_ROOT = Path("d:/Project/SwingDeck").resolve()
REPORT_DIR = REPO_ROOT / "reports" / "repository_audit"
STATE_FILE = REPO_ROOT / "state" / "audit" / "deep_repository_audit_state.json"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Helper to get Git tracked files and status
def get_git_status_map():
    status_map = {}
    try:
        # Get list of tracked files
        res = subprocess.run(["git", "ls-files"], cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            status_map[line.replace("\\", "/")] = "TRACKED"
            
        # Get status modifications / untracked
        res2 = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO_ROOT), capture_output=True, text=True, check=True)
        for line in res2.stdout.splitlines():
            if len(line) >= 4:
                code = line[:2].strip()
                path = line[3:].strip().replace("\\", "/")
                # Handle rename syntax
                if " -> " in path:
                    path = path.split(" -> ")[1].strip()
                if code == "??":
                    status_map[path] = "UNTRACKED"
                elif code in ["M", "MM", "AM"]:
                    status_map[path] = "MODIFIED"
                elif code in ["A"]:
                    status_map[path] = "STAGED_NEW"
                elif code in ["D"]:
                    status_map[path] = "DELETED"
    except Exception as e:
        print(f"Warning: Git status execution error: {e}")
    return status_map

# 2. Compute SHA256
def compute_sha256(filepath):
    try:
        if filepath.stat().st_size > 100 * 1024 * 1024:
            return "SKIPPED_LARGE_FILE"
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

# 3. Layer and Owner Classifiers
def classify_artifact(rel_path_str):
    p = rel_path_str.replace("\\", "/")
    parts = p.split("/")
    top = parts[0] if parts else ""
    
    # Layer
    if top in ["research", "gates"] or "coba" in p.lower() or "zzz" in p.lower():
        layer = "LAYER_A_RESEARCH"
    elif top in ["governance", "knowledge"]:
        layer = "LAYER_C_GOVERNANCE"
    elif top in ["queue", "state", "logs", "positions"]:
        layer = "RUNTIME_EPHEMERAL"
    elif top in ["configs"]:
        layer = "CONFIG"
    elif top in ["tests"]:
        layer = "TEST"
    elif top in ["agents", "core", "scripts"]:
        layer = "LAYER_B_OPERATIONAL"
    elif top in ["data"]:
        layer = "DATA"
    elif top in ["reports"]:
        layer = "REPORT"
    else:
        layer = "INFRASTRUCTURE"
        
    # Owner
    if "agent1" in p:
        owner = "AGENT_1_QUANT"
    elif "agent2" in p:
        owner = "AGENT_2_INTELLIGENCE"
    elif "agent3" in p:
        owner = "AGENT_3_COMMITTEE"
    elif top in ["data"]:
        owner = "DATA_ENGINEERING"
    elif top in ["research", "gates"]:
        owner = "RESEARCH_LEAD"
    elif top in ["governance", "knowledge"]:
        owner = "GOVERNANCE_AUDIT"
    elif top in ["core", "scripts", "main.py", "conftest.py", "pytest.ini"]:
        owner = "PLATFORM_CORE"
    elif top in ["tests"]:
        owner = "QA_VALIDATION"
    else:
        owner = "SYSTEM_ADMIN"

    # Mutability
    if layer == "LAYER_A_RESEARCH" or top in ["gates"]:
        mutability = "IMMUTABLE_FROZEN"
    elif layer == "RUNTIME_EPHEMERAL":
        mutability = "MUTABLE_RUNTIME"
    elif layer in ["CONFIG", "LAYER_B_OPERATIONAL", "TEST", "REPORT", "LAYER_C_GOVERNANCE"]:
        mutability = "CONTROLLED_MUTABLE"
    elif top == "data" and ("raw" in p or "parquet" in p):
        mutability = "READ_ONLY_LAKE"
    else:
        mutability = "CONTROLLED_MUTABLE"

    # Status & Retention
    if layer == "LAYER_A_RESEARCH":
        status = "FROZEN"
        retention = "PERMANENT_RESEARCH"
    elif layer == "RUNTIME_EPHEMERAL":
        status = "RUNTIME"
        retention = "EPHEMERAL_CYCLE"
    elif layer == "TEST":
        status = "TEST"
        retention = "PERMANENT_QA"
    elif layer == "CONFIG":
        status = "OPERATIONAL"
        retention = "PERMANENT_CONFIG"
    elif layer == "REPORT":
        status = "OPERATIONAL"
        retention = "PERMANENT_AUDIT"
    elif layer == "LAYER_C_GOVERNANCE":
        status = "GOVERNANCE"
        retention = "PERMANENT_GOVERNANCE"
    else:
        status = "ACTIVE"
        retention = "ACTIVE_CODEBASE"

    return layer, owner, mutability, status, retention

def run_inventory():
    print("Starting Deep Repository Forensic Inventory...")
    git_map = get_git_status_map()
    
    inventory_rows = []
    hash_to_files = {}
    total_files = 0
    total_dirs = set()
    
    ignore_dirs = {".git", ".venv", "__pycache__", ".pytest_cache"}
    
    for root, dirs, files in os.walk(REPO_ROOT):
        # Exclude internal venv / git
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".venv")]
        rel_root = Path(root).relative_to(REPO_ROOT)
        if str(rel_root) != ".":
            total_dirs.add(str(rel_root).replace("\\", "/"))
            
        for file in files:
            file_path = Path(root) / file
            rel_file = file_path.relative_to(REPO_ROOT)
            rel_str = str(rel_file).replace("\\", "/")
            
            total_files += 1
            size = file_path.stat().st_size
            ext = file_path.suffix.lower() if file_path.suffix else "NO_EXT"
            sha256 = compute_sha256(file_path)
            
            git_stat = git_map.get(rel_str, "IGNORED_OR_UNTRACKED")
            layer, owner, mutability, status, retention = classify_artifact(rel_str)
            
            # Purpose inference
            if ext == ".py":
                purpose = "Python source / execution logic"
            elif ext == ".csv":
                purpose = "Structured dataset / ledger / metrics"
            elif ext == ".parquet":
                purpose = "Columnar time-series store"
            elif ext == ".duckdb":
                purpose = "Relational analytical database"
            elif ext == ".json":
                purpose = "Structured metadata / schema / cache"
            elif ext in [".yaml", ".yml"]:
                purpose = "System configuration template"
            elif ext == ".md":
                purpose = "Documentation / report / governance charter"
            else:
                purpose = "Supporting resource / text file"
                
            # Track duplicates by hash
            if sha256 not in hash_to_files:
                hash_to_files[sha256] = []
            hash_to_files[sha256].append(rel_str)
            
            inventory_rows.append({
                "Path": rel_str,
                "Type": ext,
                "Size_Bytes": size,
                "SHA256": sha256,
                "Git_Status": git_stat,
                "Purpose": purpose,
                "Layer": layer,
                "Owner": owner,
                "Mutability": mutability,
                "Status": status,
                "Retention": retention
            })
            
    print(f"Scanned {total_files} files across {len(total_dirs)} directories.")
    
    # Write DEEP_REPOSITORY_INVENTORY.csv
    inv_file = REPORT_DIR / "DEEP_REPOSITORY_INVENTORY.csv"
    with open(inv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Path", "Type", "Size_Bytes", "SHA256", "Git_Status", 
            "Purpose", "Layer", "Owner", "Mutability", "Status", "Retention"
        ])
        writer.writeheader()
        writer.writerows(inventory_rows)
        
    print(f"Inventory written to {inv_file}")
    
    # Duplication analysis
    dup_rows = []
    dup_count = 0
    for h, flist in hash_to_files.items():
        if len(flist) > 1 and h not in ["SKIPPED_LARGE_FILE"] and not h.startswith("ERROR"):
            dup_count += 1
            # Check if all files in the duplicate set are .gitkeep or empty
            first_p = REPO_ROOT / flist[0]
            is_empty = (first_p.stat().st_size == 0)
            dup_rows.append({
                "SHA256": h,
                "Duplicate_Count": len(flist),
                "Is_Empty_File": is_empty,
                "Sample_Paths": "; ".join(flist[:5]),
                "Resolution_Strategy": "RETAIN_IF_INTENTIONAL_FIXTURE_OR_GITKEEP" if is_empty else "AUDIT_REDUNDANCY"
            })
            
    dup_file = REPORT_DIR / "DEEP_REPOSITORY_DUPLICATION_AUDIT.csv"
    with open(dup_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "SHA256", "Duplicate_Count", "Is_Empty_File", "Sample_Paths", "Resolution_Strategy"
        ])
        writer.writeheader()
        writer.writerows(dup_rows)
    print(f"Duplication audit written to {dup_file} ({dup_count} duplicate content clusters found).")
    
    return inventory_rows, total_files, len(total_dirs)

if __name__ == "__main__":
    run_inventory()
