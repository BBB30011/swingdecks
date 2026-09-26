import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.data_onboarding import DataOnboardingService
from core.data_compatibility import DataCompatibilityChecker
from core.data_import_wizard import DataImportWizard
from core.data_provisioning import DataProvisioningReporter

def main():
    parser = argparse.ArgumentParser(description="Dataset Onboarding CLI")
    parser.add_argument("--compatibility", action="store_true", help="Run compatibility analysis")
    parser.add_argument("--inventory", action="store_true", help="Run dataset inventory only")
    parser.add_argument("--validate", action="store_true", help="Run full validation")
    parser.add_argument("--report", action="store_true", help="Generate reports")
    parser.add_argument("--wizard", action="store_true", help="Run data import wizard")
    parser.add_argument("--preflight", action="store_true", help="Generate pre-backtest checklist")
    parser.add_argument("--provisioning-status", action="store_true", help="Generate final data provisioning status")
    args = parser.parse_args()
    
    # If no flags provided, default to dry-run / inventory
    if not any(vars(args).values()):
        args.inventory = True

    print("=== DATA ONBOARDING CLI ===")
    
    if args.provisioning_status:
        reporter = DataProvisioningReporter("data/raw/historical")
        status = reporter.generate_status()
        if not status["real_data_present"]:
            print("REAL_DATA_NOT_PROVISIONED")
            sys.exit(3)
        print(f"Dataset Status: {status['dataset_status']}")
        if status["dataset_ready"]:
            sys.exit(0)
        sys.exit(2)

    
    if args.wizard:
        wizard = DataImportWizard("data/raw/historical")
        wizard.generate_operator_instructions()
        print("Generated import instructions at reports/import_instructions.md")
        sys.exit(0)
        
    if args.preflight:
        wizard = DataImportWizard("data/raw/historical")
        ins = wizard.inspect()
        wizard.generate_pre_backtest_checklist(ins)
        if ins.get("dataset_status") == "REAL_DATA_NOT_PROVISIONED":
            print("REAL_DATA_NOT_PROVISIONED")
            sys.exit(3)
        print("Generated pre-backtest checklist at reports/pre_backtest_checklist.md")
        if ins.get("dataset_status") == "NOT_READY":
            sys.exit(2)
        sys.exit(0)
    
    if args.compatibility:
        checker = DataCompatibilityChecker("data/raw/historical")
        res = checker.check_directory()
        if res.get("status") == "REAL_DATA_NOT_PROVISIONED":
            print("REAL_DATA_NOT_PROVISIONED")
            sys.exit(3)
        print(f"Dataset Status: {res.get('dataset_status')}")
        print("Generated compatibility report and checklist.")
        if res.get("dataset_status") == "NOT_READY":
            sys.exit(2)
        sys.exit(0)
        
    service = DataOnboardingService("data/raw/historical")
    
    if args.inventory:
        disc = service.discover()
        if disc["status"] == "REAL_DATA_NOT_PROVISIONED":
            print("REAL_DATA_NOT_PROVISIONED")
            sys.exit(3)
        print("Inventory completed.")
        sys.exit(0)
        
    if args.validate or args.report:
        result = service.onboard()
        if result.get("readiness") == "REAL_DATA_NOT_PROVISIONED":
            print("REAL_DATA_NOT_PROVISIONED")
            sys.exit(3)
            
        print(f"Status: {result.get('dataset_acceptance')}")
        print(f"Readiness: {result.get('readiness')}")
        print(f"Total Symbols: {result.get('symbol_count')}")
        
        if result.get("dataset_acceptance") == "ACCEPTED":
            sys.exit(0)
        elif result.get("dataset_acceptance") == "ACCEPTED_WITH_WARNINGS":
            sys.exit(1)
        else:
            sys.exit(2)

if __name__ == "__main__":
    main()
