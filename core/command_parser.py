import re
from typing import Dict, Any, Optional

from core.live_news_ingestion import LiveNewsIngestionEngine
from core.agent2_research_provider import Agent2ResearchProvider

class CommandParser:
    """
    Parses explicitly human-triggered commands for SEMI-MANUAL MODE.
    Strictly validates command intent and prevents Agent 4 autonomy.
    """
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.db_path = db_path
        self.news_engine = LiveNewsIngestionEngine(db_path)
        self.research_provider = Agent2ResearchProvider(use_live_internet=True)

    def execute_command(self, command_str: str) -> str:
        command_str = command_str.strip().upper()
        
        # Parse optional --mode flag
        requested_mode = "auto"
        if "--MODE" in command_str:
            parts = command_str.split("--MODE")
            command_str = parts[0].strip()
            requested_mode = parts[1].strip().lower()
            
        # AGENT2 UPDATE NEWS <SYMBOL> [SCOPE] [--mode <mode>]
        news_match = re.match(r"^AGENT2\s+UPDATE\s+NEWS\s+([A-Z0-9]+)(?:\s+(.*))?$", command_str)
        if news_match:
            symbol = news_match.group(1)
            scope = news_match.group(2) if news_match.group(2) else "RECENT"
            
            # Validate Ticker (Basic validation)
            if len(symbol) < 3 or len(symbol) > 6:
                return f"REJECT: ENTITY_UNCERTAIN (Invalid symbol '{symbol}')"
                
            if requested_mode == "web":
                return (
                    "REJECT: WEB mode is an IDE-assisted mode. The Python runtime cannot execute this natively without an API provider. "
                    "Please execute via IDE Agent and use 'AGENT2 INGEST NEWS <SYMBOL> <PATH>' to ingest the results, or use '--mode api'."
                )
                
            try:
                # Execute AI Research (API mode)
                research_result = self.research_provider.research(symbol, scope, requested_mode)
                
                if research_result.get("status") == "SOURCE_ACCESS_FAILURE":
                    return (
                        f"STATUS: SOURCE_ACCESS_FAILURE\n"
                        f"REQUESTED_MODE: {requested_mode.upper()}\n"
                        f"REASON: {research_result.get('reason')}"
                    )
                
                # Ingest JSON payload to DB
                cache_path = f"data/cache/agent2_research_{symbol}_api.json"
                import json
                import os
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "w") as f:
                    json.dump(research_result, f, indent=2)
                    
                report = self.news_engine.execute_ai_research_ingestion(cache_path)
                return report
            except Exception as e:
                return f"REJECT: Error executing Agent 2 AI research update: {str(e)}"
                
        # AGENT2 INGEST NEWS <SYMBOL> <PATH> (Explicit IDE-Assisted Handoff)
        ingest_match = re.match(r"^AGENT2\s+INGEST\s+NEWS\s+([A-Z0-9]+)\s+(.+)$", command_str)
        if ingest_match:
            symbol = ingest_match.group(1)
            filepath = ingest_match.group(2).strip()
            
            import os
            if not os.path.exists(filepath):
                return f"REJECT: Payload file not found at {filepath}"
                
            try:
                report = self.news_engine.execute_ai_research_ingestion(filepath)
                return report
            except Exception as e:
                return f"REJECT: Error ingesting IDE payload: {str(e)}"
                
        # Handle invalid / missing agent commands
        if not (command_str.startswith("AGENT1 ") or command_str.startswith("AGENT2 ") or command_str.startswith("AGENT3 ")):
            return "REJECT: Invalid agent or missing parameters."
            
        return f"REJECT: Unknown command '{command_str}'. Supported: AGENT2 UPDATE NEWS <SYMBOL>, AGENT2 INGEST NEWS <SYMBOL> <PATH>"

