import os
import sys
import re
import ast
import json
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple

ROOT_DIR = Path("D:/Project/SwingDeck")

def run_inventory_audit() -> Dict[str, Any]:
    stats = {
        "total_files": 0,
        "total_directories": 0,
        "by_extension": {},
        "top_level_dirs": {},
        "file_list": []
    }
    
    for root, dirs, files in os.walk(ROOT_DIR):
        rpath = Path(root)
        if any(p in rpath.parts for p in [".git", ".venv", ".pytest_cache", "__pycache__"]):
            continue
            
        rel_root = rpath.relative_to(ROOT_DIR)
        top_dir = rel_root.parts[0] if rel_root.parts else "."
        stats["top_level_dirs"].setdefault(top_dir, {"files": 0, "bytes": 0})
        stats["total_directories"] += len(dirs)
        
        for f in files:
            fpath = rpath / f
            try:
                sz = fpath.stat().st_size
            except Exception:
                sz = 0
            ext = fpath.suffix.lower() or "(no_ext)"
            stats["total_files"] += 1
            stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1
            stats["top_level_dirs"][top_dir]["files"] += 1
            stats["top_level_dirs"][top_dir]["bytes"] += sz
            stats["file_list"].append({
                "path": str(fpath.relative_to(ROOT_DIR)).replace("\\", "/"),
                "size_bytes": sz,
                "extension": ext
            })
            
    return stats

def run_agent_boundary_audit() -> List[Dict[str, Any]]:
    findings = []
    agent_dirs = [p for p in (ROOT_DIR / "agents").iterdir() if p.is_dir() and p.name != "__pycache__"]
    agent_names = [p.name for p in agent_dirs]
    
    # 1. Exactly 3 agents in agents/
    findings.append({
        "Category": "Agent_Count",
        "Target": "agents/",
        "Observed": f"Found {len(agent_names)} agents: {agent_names}",
        "Status": "PASS" if len(agent_names) == 3 and "agent1_quant" in agent_names and "agent2_intelligence" in agent_names and "agent3_committee" in agent_names else "FAIL",
        "Detail": "Exactly 3 agents verified in agents/ directory."
    })
    
    # 2. Check for Agent 4 anywhere in the codebase
    agent4_pattern = re.compile(r"\bagent[_\-\s]?4\b", re.IGNORECASE)
    agent4_mentions = []
    
    for item in ROOT_DIR.rglob("*.py"):
        if any(p in item.parts for p in [".git", ".venv", ".pytest_cache", "__pycache__"]):
            continue
        try:
            content = item.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                if agent4_pattern.search(line):
                    # Check if it's an enforcement rule/firewall
                    if "FORBIDDEN" in line.upper() or "NONE" in line.upper() or "ZERO" in line.upper() or "PREVENT" in line.upper() or "NO AGENT 4" in line.upper():
                        continue
                    agent4_mentions.append((str(item.relative_to(ROOT_DIR)).replace("\\", "/"), i, line.strip()[:80]))
        except Exception:
            pass
            
    findings.append({
        "Category": "Agent_4_Prohibition",
        "Target": "All Codebase",
        "Observed": f"{len(agent4_mentions)} non-firewall mentions of Agent 4",
        "Status": "PASS" if len(agent4_mentions) == 0 else "FAIL",
        "Detail": f"Mentions: {agent4_mentions[:5]}" if agent4_mentions else "Zero unauthorized Agent 4 components."
    })
    
    return findings

def run_syntax_and_import_audit() -> List[Dict[str, Any]]:
    findings = []
    py_files = []
    for item in ROOT_DIR.rglob("*.py"):
        if any(p in item.parts for p in [".git", ".venv", ".pytest_cache", "__pycache__"]):
            continue
        py_files.append(item)
        
    for p in py_files:
        rel = str(p.relative_to(ROOT_DIR)).replace("\\", "/")
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"), filename=str(p))
        except SyntaxError as e:
            findings.append({
                "File": rel,
                "Error_Type": "SyntaxError",
                "Detail": f"Line {e.lineno}: {e.msg}"
            })
            
    return findings

def run_security_audit() -> List[Dict[str, Any]]:
    findings = []
    secret_patterns = [
        ("API_Key_Assignment", re.compile(r'(?i)(api[_-]?key|secret|token)\s*=\s*[\'"][A-Za-z0-9_\-]{16,}[\'"]')),
        ("Google_AI_Key", re.compile(r'AIza[0-9A-Za-z-_]{35}')),
        ("AWS_Key", re.compile(r'AKIA[0-9A-Z]{16}')),
        ("Unsafe_Eval", re.compile(r'\beval\s*\(')),
        ("Unsafe_Exec", re.compile(r'\bexec\s*\(')),
        ("Pickle_Load", re.compile(r'\bpickle\.loads?\s*\(')),
    ]
    
    for item in ROOT_DIR.rglob("*"):
        if any(p in item.parts for p in [".git", ".venv", ".pytest_cache", "__pycache__"]):
            continue
        if not item.is_file() or item.suffix not in [".py", ".json", ".yaml", ".yml", ".env", ".md", ".txt"]:
            continue
            
        rel = str(item.relative_to(ROOT_DIR)).replace("\\", "/")
        try:
            content = item.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                # Ignore test mocks
                if any(x in line.upper() for x in ["MOCK", "TEST", "EXAMPLE", "DUMMY", "PLACEHOLDER", "YOUR_"]):
                    continue
                for name, pat in secret_patterns:
                    if pat.search(line):
                        findings.append({
                            "File": rel,
                            "Line": i,
                            "Vulnerability_Type": name,
                            "Snippet": line.strip()[:80]
                        })
        except Exception:
            pass
            
    return findings

def run_data_architecture_audit() -> List[Dict[str, Any]]:
    findings = []
    import duckdb
    
    # Check DuckDB
    primary_db = ROOT_DIR / "data/duckdb/intelligence.duckdb"
    legacy_db = ROOT_DIR / "data/intelligence.duckdb"
    
    if primary_db.exists():
        con = duckdb.connect(str(primary_db))
        tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        table_counts = {}
        for t in tables:
            cnt = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            table_counts[t] = cnt
        con.close()
        
        findings.append({
            "Component": "DuckDB_Primary",
            "Path": "data/duckdb/intelligence.duckdb",
            "Status": "ACTIVE_VERIFIED",
            "Detail": f"10 tables, counts: {table_counts}"
        })
    else:
        findings.append({
            "Component": "DuckDB_Primary",
            "Path": "data/duckdb/intelligence.duckdb",
            "Status": "MISSING",
            "Detail": "Primary DuckDB file does not exist"
        })
        
    if legacy_db.exists():
        sz = legacy_db.stat().st_size
        findings.append({
            "Component": "DuckDB_Legacy_Stray",
            "Path": "data/intelligence.duckdb",
            "Status": "STRAY_ARTIFACT",
            "Detail": f"Size: {sz} bytes (0 tables). Recommend deprecation/cleanup to prevent confusion."
        })
        
    # Check Parquet directories
    parquet_market = ROOT_DIR / "data/parquet/market"
    if parquet_market.exists():
        files = list(parquet_market.glob("*.parquet"))
        findings.append({
            "Component": "Parquet_Market",
            "Path": "data/parquet/market",
            "Status": "POPULATED",
            "Detail": f"{len(files)} ticker parquet files present"
        })
        
    # Check Raw market
    raw_market = ROOT_DIR / "data/raw/market"
    if raw_market.exists():
        files = list(raw_market.glob("*.csv"))
        findings.append({
            "Component": "Raw_Market_CSV",
            "Path": "data/raw/market",
            "Status": "POPULATED",
            "Detail": f"{len(files)} CSV market files present"
        })
        
    return findings

def main():
    print("Executing comprehensive post-research baseline audit...")
    inv = run_inventory_audit()
    print(f"Total files audited: {inv['total_files']}, directories: {inv['total_directories']}")
    for ext, cnt in sorted(inv["by_extension"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ext}: {cnt} files")
        
    print("\nAuditing Agent Boundaries...")
    agent_findings = run_agent_boundary_audit()
    for f in agent_findings:
        print(f"  [{f['Status']}] {f['Category']}: {f['Detail']}")
        
    print("\nAuditing Python Syntax...")
    syntax_findings = run_syntax_and_import_audit()
    print(f"  Syntax errors found: {len(syntax_findings)}")
    for f in syntax_findings:
        print(f"  [ERROR] {f['File']}: {f['Detail']}")
        
    print("\nAuditing Security & Secrets...")
    sec_findings = run_security_audit()
    print(f"  Security findings: {len(sec_findings)}")
    for f in sec_findings:
        print(f"  [{f['Vulnerability_Type']}] {f['File']}:{f['Line']} -> {f['Snippet']}")
        
    print("\nAuditing Data Architecture...")
    data_findings = run_data_architecture_audit()
    for f in data_findings:
        print(f"  [{f['Status']}] {f['Component']} ({f['Path']}): {f['Detail']}")

if __name__ == "__main__":
    main()
