import sys
from core.command_parser import CommandParser

def main():
    print("=" * 50)
    print("AI SWING TRADING DESK - SEMI-MANUAL MODE")
    print("=" * 50)
    
    parser = CommandParser()
    
    if len(sys.argv) > 1:
        command_str = " ".join(sys.argv[1:])
        report = parser.execute_command(command_str)
        print(report)
    else:
        print("Environment : LIVE INTELLIGENCE INGESTION")
        print("Dry Run     : TRUE")
        print("Status      : READY FOR COMMANDS")
        print("Type 'exit' or 'quit' to terminate.")
        print("=" * 50)
        
        while True:
            try:
                cmd = input("swingdeck> ")
                if cmd.strip().lower() in ['exit', 'quit']:
                    break
                if not cmd.strip():
                    continue
                
                report = parser.execute_command(cmd)
                print(report)
                print("-" * 50)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
