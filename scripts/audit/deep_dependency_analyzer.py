import os
import sys
import ast
import csv
import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path("d:/Project/SwingDeck").resolve()
REPORT_DIR = REPO_ROOT / "reports" / "repository_audit"

def analyze_dependencies():
    print("Starting Deep Dependency, Import, and Reference Graph Analysis...")
    
    python_files = []
    markdown_files = []
    
    ignore_dirs = {".git", ".venv", "__pycache__", ".pytest_cache"}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".venv")]
        for f in files:
            p = Path(root) / f
            if f.endswith(".py"):
                python_files.append(p)
            elif f.endswith(".md"):
                markdown_files.append(p)
                
    # 1. AST Import Extraction
    import_graph = defaultdict(set) # file_rel -> set of imported module names
    module_to_file = {} # module_name -> file_rel
    
    for pf in python_files:
        rel = str(pf.relative_to(REPO_ROOT)).replace("\\", "/")
        # Build module name
        mod_name = rel.replace(".py", "").replace("/", ".")
        if mod_name.endswith(".__init__"):
            mod_name = mod_name[:-9]
        module_to_file[mod_name] = rel
        
        try:
            with open(pf, "r", encoding="utf-8", errors="ignore") as f:
                tree = ast.parse(f.read(), filename=rel)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_graph[rel].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_graph[rel].add(node.module)
        except Exception as e:
            print(f"Error parsing {rel}: {e}")

    # Build reference counts for internal modules
    internal_ref_counts = defaultdict(int)
    dependency_rows = []
    
    for source_file, imported_mods in import_graph.items():
        for mod in sorted(imported_mods):
            # Check if internal
            is_internal = False
            target_file = "EXTERNAL"
            
            # Direct match
            if mod in module_to_file:
                is_internal = True
                target_file = module_to_file[mod]
            else:
                # Prefix match (e.g. core.config.load_yaml -> core.config)
                parts = mod.split(".")
                for i in range(len(parts)-1, 0, -1):
                    prefix = ".".join(parts[:i])
                    if prefix in module_to_file:
                        is_internal = True
                        target_file = module_to_file[prefix]
                        break
                        
            if is_internal:
                internal_ref_counts[target_file] += 1
                
            dependency_rows.append({
                "Source_File": source_file,
                "Imported_Module": mod,
                "Is_Internal": is_internal,
                "Target_File": target_file,
                "Reference_Type": "PYTHON_IMPORT"
            })
            
    # Write DEEP_REPOSITORY_DEPENDENCY_AUDIT.csv
    dep_file = REPORT_DIR / "DEEP_REPOSITORY_DEPENDENCY_AUDIT.csv"
    with open(dep_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Source_File", "Imported_Module", "Is_Internal", "Target_File", "Reference_Type"
        ])
        writer.writeheader()
        writer.writerows(dependency_rows)
    print(f"Dependency audit written to {dep_file} ({len(dependency_rows)} import edges).")

    # 2. Circular Dependency Analysis
    # Construct adjacency for internal files
    file_adj = defaultdict(set)
    for r in dependency_rows:
        if r["Is_Internal"] and r["Target_File"] != "EXTERNAL" and r["Source_File"] != r["Target_File"]:
            file_adj[r["Source_File"]].add(r["Target_File"])
            
    def find_cycles():
        visited = {} # node -> 0: unvisited, 1: visiting, 2: visited
        cycles = []
        path = []
        
        def dfs(node):
            visited[node] = 1
            path.append(node)
            for neighbor in file_adj.get(node, []):
                if visited.get(neighbor, 0) == 1:
                    cycle_idx = path.index(neighbor)
                    cycles.append(path[cycle_idx:] + [neighbor])
                elif visited.get(neighbor, 0) == 0:
                    dfs(neighbor)
            path.pop()
            visited[node] = 2
            
        for node in list(file_adj.keys()):
            if visited.get(node, 0) == 0:
                dfs(node)
        return cycles

    cycles = find_cycles()
    print(f"Circular dependency analysis: {len(cycles)} cycles detected.")
    if cycles:
        for c in cycles[:5]:
            print("  Cycle:", " -> ".join(c))

    # 3. Orphan / Dead Code Analysis
    orphan_rows = []
    # Files with 0 incoming internal imports that are NOT entrypoints, tests, or scripts
    entrypoint_whitelist = {
        "main.py", "conftest.py", "setup.py"
    }
    
    for pf in python_files:
        rel = str(pf.relative_to(REPO_ROOT)).replace("\\", "/")
        in_refs = internal_ref_counts[rel]
        
        is_test = rel.startswith("tests/")
        is_script = rel.startswith("scripts/") or rel.startswith("scratch/")
        is_entry = rel in entrypoint_whitelist
        is_research = "coba" in rel.lower() or "zzz" in rel.lower() or rel.startswith("research/") or rel.startswith("gates/")
        is_init = rel.endswith("__init__.py")
        
        if in_refs == 0 and not (is_test or is_script or is_entry or is_init or is_research):
            orphan_rows.append({
                "File_Path": rel,
                "Inbound_Internal_Imports": 0,
                "Category": "UNREFERENCED_CORE_MODULE",
                "Lineage_Retention": "AUDIT_CALLERS_OR_CLI",
                "Action_Recommendation": "CHECK_IF_DYNAMIC_OR_CLI_ENTRYPOINT"
            })
            
    orphan_file = REPORT_DIR / "DEEP_REPOSITORY_ORPHAN_AUDIT.csv"
    with open(orphan_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "File_Path", "Inbound_Internal_Imports", "Category", "Lineage_Retention", "Action_Recommendation"
        ])
        writer.writeheader()
        writer.writerows(orphan_rows)
    print(f"Orphan audit written to {orphan_file} ({len(orphan_rows)} unreferenced operational modules).")

    # 4. Markdown Link Integrity Analysis
    broken_md_links = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    for mf in markdown_files:
        rel_mf = str(mf.relative_to(REPO_ROOT)).replace("\\", "/")
        try:
            with open(mf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for m in link_pattern.finditer(content):
                label, target = m.group(1), m.group(2)
                # Ignore web links, anchors, mailto
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                # Handle file:/// or raw relative paths
                clean_target = target.replace("file:///", "").replace("file://", "").split("#")[0].strip()
                # Windows drive letter absolute paths
                if re.match(r'^[a-zA-Z]:[/\\]', clean_target):
                    target_path = Path(clean_target)
                else:
                    target_path = (mf.parent / clean_target).resolve()
                    
                if not target_path.exists():
                    broken_md_links.append({
                        "Source_Doc": rel_mf,
                        "Link_Text": label,
                        "Target_Raw": target,
                        "Resolved_Path": str(target_path).replace("\\", "/"),
                        "Status": "BROKEN_LINK"
                    })
        except Exception as e:
            pass
            
    doc_audit_file = REPORT_DIR / "DEEP_REPOSITORY_DOCUMENTATION_AUDIT.csv"
    with open(doc_audit_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Source_Doc", "Link_Text", "Target_Raw", "Resolved_Path", "Status"
        ])
        writer.writeheader()
        writer.writerows(broken_md_links)
    print(f"Documentation link audit written to {doc_audit_file} ({len(broken_md_links)} broken links detected).")

    # 5. File Naming Forensics
    naming_issues = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".venv")]
        for f in files:
            rel = str((Path(root) / f).relative_to(REPO_ROOT)).replace("\\", "/")
            name_stem = Path(f).stem
            ext = Path(f).suffix.lower()
            
            issue = None
            if "copy" in name_stem.lower():
                issue = "CONTAINS_COPY"
            elif "temp" in name_stem.lower() or "tmp" in name_stem.lower():
                issue = "CONTAINS_TEMP"
            elif "backup" in name_stem.lower() or "bak" in name_stem.lower():
                issue = "CONTAINS_BACKUP"
            elif ext == ".py" and not re.match(r'^[a-z0-9_]+$', name_stem):
                # Check if historical
                if not ("coba" in rel.lower() or "zzz" in rel.lower()):
                    issue = "NON_SNAKE_CASE_PYTHON_FILE"
            elif ext == ".py" and name_stem in ["utils", "helper", "common", "data", "model"]:
                issue = "GENERIC_AMBIGUOUS_NAME"
                
            if issue:
                naming_issues.append({
                    "Path": rel,
                    "Name": f,
                    "Issue_Type": issue,
                    "Proposed_Convention": "CONSOLIDATE_OR_RENAME" if "COPY" in issue or "BACKUP" in issue else "SPECIFIC_DOMAIN_NAME"
                })
                
    naming_file = REPORT_DIR / "DEEP_REPOSITORY_NAMING_AUDIT.csv"
    with open(naming_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Path", "Name", "Issue_Type", "Proposed_Convention"])
        writer.writeheader()
        writer.writerows(naming_issues)
    print(f"Naming audit written to {naming_file} ({len(naming_issues)} naming issues flagged).")

    # 6. Structure Audit (Top-level & Second-level folder governance)
    structure_rows = []
    top_level_items = sorted(list(REPO_ROOT.iterdir()), key=lambda x: x.name)
    for item in top_level_items:
        if item.name in ignore_dirs:
            continue
        is_dir = item.is_dir()
        name = item.name
        
        # Determine purpose and ownership
        if name == "agents":
            purpose = "Runtime execution logic for exactly 3 agents (agent1_quant, agent2_intelligence, agent3_committee)"
            owner = "AGENT_ENGINEERING"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "core":
            purpose = "Shared platform infrastructure, orchestrator, pipeline runner, schemas, replay firewall"
            owner = "PLATFORM_CORE"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "configs":
            purpose = "System YAML configurations and data source settings"
            owner = "PLATFORM_CORE"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "data":
            purpose = "Canonical data storage (duckdb, parquet, raw, processed)"
            owner = "DATA_ENGINEERING"
            mutability = "IMMUTABLE_LAKE_AND_LOCAL_DB"
            status = "CANONICAL"
        elif name == "governance":
            purpose = "Architectural maps, lineage charters, and frozen research ledgers"
            owner = "GOVERNANCE_LEAD"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "knowledge":
            purpose = "Domain patterns, memory, and context"
            owner = "KNOWLEDGE_CURATOR"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "research":
            purpose = "Historical frozen experimental lineage COBA_001 to COBA_018"
            owner = "RESEARCH_LEAD"
            mutability = "IMMUTABLE_FROZEN"
            status = "CANONICAL_FROZEN"
        elif name == "gates":
            purpose = "Historical gate evidence artifacts"
            owner = "RESEARCH_LEAD"
            mutability = "IMMUTABLE_FROZEN"
            status = "CANONICAL_FROZEN"
        elif name == "reports":
            purpose = "Audit registers, forensic findings, and human-readable operational reports"
            owner = "GOVERNANCE_AUDIT"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "tests":
            purpose = "Unit, integration, architecture, PIT, and historical regression test suites"
            owner = "QA_VALIDATION"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name == "scripts":
            purpose = "Audit scripts and operational maintenance utilities"
            owner = "PLATFORM_CORE"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL"
        elif name in ["queue", "state", "positions", "logs"]:
            purpose = f"Runtime operational ephemeral storage ({name})"
            owner = "RUNTIME_OPERATIONS"
            mutability = "MUTABLE_RUNTIME"
            status = "CANONICAL_RUNTIME"
        elif name == "scratch":
            purpose = "Temporary workspace for scratch calculations"
            owner = "DEVELOPER_SCRATCH"
            mutability = "EPHEMERAL"
            status = "EPHEMERAL_WORKSPACE"
        elif name in ["main.py", "conftest.py", "pytest.ini", "README.md", ".gitignore"]:
            purpose = f"Canonical repository root anchor file ({name})"
            owner = "PLATFORM_CORE"
            mutability = "CONTROLLED_MUTABLE"
            status = "CANONICAL_ROOT_FILE"
        else:
            purpose = "Unclassified or ghost item"
            owner = "UNKNOWN"
            mutability = "UNKNOWN"
            status = "GHOST_OR_ANOMALOUS"

        structure_rows.append({
            "Entry_Name": name,
            "Is_Directory": is_dir,
            "Owner": owner,
            "Purpose": purpose,
            "Mutability": mutability,
            "Status": status
        })
        
    struct_file = REPORT_DIR / "DEEP_REPOSITORY_STRUCTURE_AUDIT.csv"
    with open(struct_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Entry_Name", "Is_Directory", "Owner", "Purpose", "Mutability", "Status"
        ])
        writer.writeheader()
        writer.writerows(structure_rows)
    print(f"Structure audit written to {struct_file} ({len(structure_rows)} top-level entries audited).")

if __name__ == "__main__":
    analyze_dependencies()
