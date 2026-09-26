import os
import re
import csv
import json

def audit():
    with open('clean_tree.txt', 'r', encoding='utf-8') as f:
        files = f.read().splitlines()
    
    files = [f for f in files if f and not f.startswith('migration_proposal')]
    
    classifications = []
    cobas = []
    batches = []
    duplicates = []
    ambiguous = []
    
    # Pre-defined known duplicates from prompt
    known_duplicates = {
        'tests/fixtures/BBCA_duplicate.csv',
        'tests/fixtures/historical/BBCA_DUP_ROW.csv'
    }
    
    # Reports about duplicates (not duplicates themselves)
    dup_reports = {
        'reports/repository_audit/DUPLICATE_ANALYSIS.md',
        'scratch/zzz116_duplicates.json',
        'scratch/zzz1411_event_dedup.json',
        'scratch/zzz141_event_dedup.json'
    }
    
    for f in files:
        if 'COBA_' in f:
            cobas.append(f)
            
        if 'batch_' in f:
            batches.append(f)
            
        category = 'UNKNOWN'
        status = 'ACTIVE'
        target = f
        action = 'KEEP ACTIVE'
        reason = 'Active component'
        risk = 'Low'
        
        # Classification logic
        if f in known_duplicates:
            category = 'FIXTURE'
            status = 'DUPLICATE'
            action = 'REGISTER + ARCHIVE'
            target = f.replace('tests/fixtures/', 'archive/duplicates/')
            duplicates.append({'file': f, 'canonical': 'tests/fixtures/BBCA_valid.csv'})
        elif f in dup_reports:
            category = 'TECHNICAL' if 'reports' in f else 'HISTORICAL_RESEARCH'
            status = 'HISTORICAL_RESEARCH' if 'zzz' in f else 'ACTIVE'
            action = 'PRESERVE'
            target = f
            reason = 'Report about duplicates, not a duplicate file itself'
        elif 'COBA_' in f:
            category = 'COBA'
            status = 'EXPERIMENT'
            action = 'PRESERVE'
        elif 'batch_' in f:
            category = 'HISTORICAL_RESEARCH'
            status = 'CLOSED_GATE'
            action = 'PRESERVE + ORGANIZE'
            target = 'gates/closed/' + os.path.basename(f)
            if 'test_batch_' in f:
                target = 'tests/scientific/' + os.path.basename(f)
        elif 'zzz14_9_' in f:
            category = 'CURRENT_RESEARCH'
            status = 'ACTIVE'
            action = 'KEEP ACTIVE'
            target = 'research/current/' + os.path.basename(f)
            if 'tests/' in f:
                target = 'tests/scientific/' + os.path.basename(f)
        elif 'zzz' in f and 'zzz14_9' not in f:
            category = 'HISTORICAL_RESEARCH'
            status = 'CLOSED_GATE'
            action = 'PRESERVE + ORGANIZE'
            if f.startswith('reports/'):
                target = 'gates/closed/' + os.path.basename(f)
            elif f.startswith('scratch/'):
                target = 'gates/evidence/' + os.path.basename(f)
            elif f.startswith('tests/'):
                target = 'tests/scientific/' + os.path.basename(f)
        elif f.startswith('core/') or f.startswith('agents/'):
            category = 'ACTIVE'
            status = 'FROZEN' if 'core/' in f else 'ACTIVE'
            target = f
        elif f.startswith('data/'):
            category = 'ACTIVE'
            target = f
        elif f.startswith('config/'):
            category = 'OPERATIONAL'
            target = 'configs/' + os.path.basename(f)
        elif f.startswith('tests/'):
            category = 'FIXTURE' if 'fixtures' in f else 'TEST'
            target = f
        elif 'scratch_historical' in f:
            category = 'LEGACY'
            status = 'SUPERSEDED'
            action = 'ARCHIVE'
            target = 'archive/legacy/' + os.path.basename(f)
        
        classifications.append({
            'Current': f,
            'Target': target,
            'Classification': category,
            'Status': status,
            'Action': action,
            'Reason': reason,
            'Risk': risk
        })
        
    return classifications, cobas, batches, duplicates, ambiguous

cls, c, b, d, a = audit()
print(f"Total files audited: {len(cls)}")
print(f"COBA found: {len(c)}")
print(f"Batches found: {len(b)}")

with open('audit_summary.json', 'w') as f:
    json.dump({
        'coba': c,
        'batch': b,
        'duplicates': d,
        'ambiguous': a
    }, f, indent=2)
