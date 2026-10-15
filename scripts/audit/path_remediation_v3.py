import os

def run_remediation():
    allowlist = [
        "tests/test_batch_zzz1421_agent2_replay_integration.py",
        "tests/test_zzz1421R_adversarial_acceptance.py",
        "tests/test_zzz1421_acceptance_evidence_review.py",
        "tests/test_batch_zzz141_dataset_v2_integrity.py",
        "tests/test_batch_zzz1411_research_readiness.py",
        "gates/evidence/run_zzz1411_research_readiness.py",
        "gates/evidence/run_zzz1421R_adversarial_challenge.py",
        "gates/evidence/run_zzz141_dataset_v2_integrity.py",
        "gates/evidence/run_zzz142_historical_replay.py",
        "gates/evidence/run_zzz1421_pilot_acceptance.py",
        "tests/test_config.py",
        "tests/test_csv_data_source.py"
    ]
    
    replacements = [
        ('SCRATCH_DIR = "gates/evidence"', 'SCRATCH_DIR = "gates/evidence"'),
        ('SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "gates/evidence")', 'SCRATCH_DIR = os.path.join(WORKSPACE_DIR, "gates/evidence")'),
        ('configs/settings.yaml', 'configs/settings.yaml'),
        ('configs/models.yaml', 'configs/models.yaml'),
        ('configs/risk.yaml', 'configs/risk.yaml'),
        ('configs/universe.yaml', 'configs/universe.yaml'),
        ('configs/data_source.yaml', 'configs/data_source.yaml'),
    ]
    
    # Actually apply to all tests and gates/evidence python files as they all follow the same pattern
    target_dirs = ["tests", "gates/evidence", "core", "scripts"]
    
    modified_count = 0
    for d in target_dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file).replace('\\', '/')
                    
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    orig_content = content
                    for old_text, new_text in replacements:
                        content = content.replace(old_text, new_text)
                        
                    if content != orig_content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        modified_count += 1
                        print(f"Patched: {filepath}")
                        
    print(f"Total files patched: {modified_count}")

if __name__ == "__main__":
    run_remediation()
