import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.schemas import MarketSnapshot, SignalState
from core.universe import UniverseManager
from core.liquidity import LiquidityAnalyzer
from core.market_scanner import MarketScanner, rank_candidates
from core.benchmark import BenchmarkProvider
from core.alert_engine import AlertEngine
from core.signal_state_tracker import SignalStateTracker
from core.data_platform_schemas import InvestigationRequest, InvestigationTriggerType

class Agent1QuantPipeline:
    """
    Pipeline Deterministic untuk Agent 1.
    Memfilter Universe Snapshot menjadi Top N kandidat siap di-research.
    """
    def __init__(self, scanner_config_path: str = "config/scanner.yaml"):
        self.universe_manager = UniverseManager()
        self.liquidity_analyzer = LiquidityAnalyzer(self.universe_manager)
        self.scanner = MarketScanner()
        self.benchmark_provider = BenchmarkProvider()
        self.alert_engine = AlertEngine()
        self.state_tracker = SignalStateTracker()
        
        self.top_n = 20
        cfg_path = Path(scanner_config_path)
        if cfg_path.exists():
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
                if cfg and "scanner" in cfg:
                    self.top_n = cfg["scanner"].get("top_n", 20)
                    
    def run(self, snapshots: List[MarketSnapshot]) -> Dict[str, Any]:
        # Muat benchmark untuk seluruh scan (cached per run)
        benchmark_snapshot = None
        try:
            benchmark_snapshot = self.benchmark_provider.get_snapshot()
        except Exception:
            # Tetap jalan tanpa benchmark (graceful fallback)
            pass
            
        input_count = len(snapshots)
        unique_snapshots = {}
        stage_trace = {}
        rejection_summary = {
            "DUPLICATE": 0,
            "LIQUIDITY_REJECTED": 0,
            "INSUFFICIENT_DATA": 0,
            "STALE_DATA": 0,
            "INVALID_DATA": 0,
            "LOW_QUANT_SCORE": 0
        }
        
        # 1. Deduplikasi & Initial Logging
        for snap in snapshots:
            sym = snap.symbol.upper()
            if sym not in stage_trace:
                stage_trace[sym] = {
                    "universe": "PASS",
                    "liquidity": "NOT_RUN",
                    "quant_features": "NOT_RUN",
                    "market_scanner": "NOT_RUN",
                    "candidate": "NOT_RUN"
                }
            
            meta = getattr(snap, 'metadata', None)
            if meta and meta.audit_status == "INVALID":
                rejection_summary["INVALID_DATA"] = rejection_summary.get("INVALID_DATA", 0) + 1
                stage_trace[sym]["universe"] = "REJECT"
                stage_trace[sym]["candidate"] = "REJECTED"
                continue

            if sym in unique_snapshots:
                rejection_summary["DUPLICATE"] += 1
                continue
                
            unique_snapshots[sym] = snap
            
        liquidity_eligible_count = 0
        quant_processed_count = 0
        candidates_pool = []
        
        # Iterasi deterministic dengan sorting key
        for sym, snap in sorted(unique_snapshots.items()):
            # 2. Liquidity Filter
            liq_res = self.liquidity_analyzer.calculate(snap)
            
            if not liq_res["eligible"]:
                stage_trace[sym]["liquidity"] = "REJECT"
                stage_trace[sym]["candidate"] = "REJECTED"
                
                for reason in liq_res.get("reasons", []):
                    if reason == "STALE_DATA":
                        rejection_summary["STALE_DATA"] += 1
                    elif reason == "INVALID_DATA":
                        rejection_summary["INVALID_DATA"] += 1
                    elif reason == "INSUFFICIENT_DATA":
                        rejection_summary["INSUFFICIENT_DATA"] += 1
                    else:
                        rejection_summary["LIQUIDITY_REJECTED"] += 1
                continue
                
            stage_trace[sym]["liquidity"] = "PASS"
            liquidity_eligible_count += 1
            
            # 3. Quant Processing & Market Scanner
            # Engine otomatis reject / assign fail states sesuai Batch J dan K
            scan_res = self.scanner.scan(snap, benchmark_snapshot=benchmark_snapshot)
            quant_processed_count += 1
            status = scan_res.get("status")
            
            if status == "READY_FOR_RESEARCH":
                stage_trace[sym]["quant_features"] = "PASS"
                stage_trace[sym]["market_scanner"] = "PASS"
                candidates_pool.append(scan_res)
                
                # Emit Fast Alert if the state is early
                current_state = self.state_tracker.get_state(sym)
                if current_state in [SignalState.WATCH, SignalState.EARLY_WATCH, SignalState.INVALIDATED]:
                    alert = self.alert_engine.generate_fast_alert(scan_res, current_state)
                    self.state_tracker.transition_state(sym, alert.state)
            else:
                stage_trace[sym]["quant_features"] = "PASS"
                stage_trace[sym]["market_scanner"] = "REJECT"
                stage_trace[sym]["candidate"] = "REJECTED"
                
                if status == "INSUFFICIENT_DATA":
                    rejection_summary["INSUFFICIENT_DATA"] += 1
                elif status == "INVALID":
                    rejection_summary["INVALID_DATA"] += 1
                elif status == "STALE_DATA":
                    rejection_summary["STALE_DATA"] += 1
                elif status == "NOT_SELECTED":
                    rejection_summary["LOW_QUANT_SCORE"] += 1

        # 4. Ranking Candidate
        ranked_candidates = rank_candidates(candidates_pool)
        
        # 5. Top N
        top_candidates = ranked_candidates[:self.top_n]
        
        for cand in top_candidates:
            stage_trace[cand["symbol"]]["candidate"] = "SELECTED"
            
        for cand in ranked_candidates[self.top_n:]:
            stage_trace[cand["symbol"]]["candidate"] = "NOT_SELECTED_TOP_N"
            
        run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(snapshots)}"
        
        return {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_count": input_count,
            "liquidity_eligible": liquidity_eligible_count,
            "quant_processed": quant_processed_count,
            "candidates": len(ranked_candidates),
            "selected": len(top_candidates),
            "top_candidates": top_candidates,
            "rejection_summary": rejection_summary,
            "stage_trace": stage_trace
        }
        
    def build_research_queue(self, selected_candidates: List[Dict]) -> List[Dict]:
        """
        Mempersiapkan payload JSON murni untuk dimasukkan ke message queue Agent 2.
        """
        queue = []
        for cand in selected_candidates:
            features = cand.get("features", {})
            relative_return_20d = features.get("relative_strength", {}).get("relative_return_20d")
            
            meta = cand.get("dataset_metadata", {})
            queue.append({
                "job_type": "MARKET_RESEARCH",
                "symbol": cand["symbol"],
                "quant_score": cand.get("quant_score"),
                "opportunity_score": cand.get("quant_score"),
                "quant_confidence": cand.get("quant_confidence"),
                "evidence_state": cand.get("evidence_state"),
                "candidate_quality": cand.get("candidate_quality"),
                "research_priority": cand.get("research_priority"),
                "evidence_completeness": cand.get("evidence_completeness"),
                "evidence_groups": cand.get("evidence_groups", {}),
                "stock_regime": cand.get("stock_regime"),
                "market_regime": cand.get("market_regime"),
                "regime_alignment": cand.get("regime_alignment"),
                "relative_strength_state": cand.get("relative_strength_state"),
                "relative_return_20d": relative_return_20d,
                "flow_state": features.get("flow", {}).get("flow_state", "UNKNOWN"),
                "price_volume_confirmation": features.get("flow", {}).get("price_volume_confirmation", "UNKNOWN"),
                "dataset_id": meta.get("dataset_id", "UNKNOWN"),
                "data_origin": meta.get("data_origin", "UNKNOWN"),
                "data_quality": meta.get("data_quality", "UNKNOWN"),
                "data_quality_warnings": meta.get("data_quality_warnings", []),
                "universe_method": meta.get("universe_method", "UNKNOWN"),
                "corporate_action_status": meta.get("corporate_action_status", "UNKNOWN"),
                "benchmark_available": meta.get("benchmark_available", False),
                "as_of_timestamp": meta.get("as_of_timestamp", cand.get("timestamp")),
                "history_length": meta.get("history_length", 0),
                "gap_status": meta.get("gap_status", "UNKNOWN"),
                "source": "agent1_quant",
                "destination": "agent2_intelligence"
            })
        return queue


    def build_investigation_requests(self, selected_candidates: List[Dict], as_of: Optional[str] = None) -> List[InvestigationRequest]:
        """
        Generates on-demand investigation requests for Agent 2 when quantitative anomalies are detected
        (e.g., unusual volume, breakout, relative strength surge).
        """
        requests = []
        now_ts = as_of or datetime.now(timezone.utc).isoformat()
        
        for cand in selected_candidates:
            sym = cand.get("symbol", "UNKNOWN")
            features = cand.get("features", {})
            vol_surge = features.get("volume", {}).get("relative_volume", 1.0)
            breakout = features.get("price_action", {}).get("breakout_20d", False)
            rs_surge = features.get("relative_strength", {}).get("relative_return_20d", 0.0)
            
            trigger = InvestigationTriggerType.UNUSUAL_VOLUME
            if breakout:
                trigger = InvestigationTriggerType.MOMENTUM_BREAKOUT
            elif rs_surge > 0.10:
                trigger = InvestigationTriggerType.RELATIVE_STRENGTH
            elif vol_surge > 2.0:
                trigger = InvestigationTriggerType.UNUSUAL_VOLUME
            else:
                trigger = InvestigationTriggerType.ABNORMAL_RETURN

                
            req = InvestigationRequest(
                request_id=f"INV_REQ_{sym}_{now_ts[:10]}_{trigger.value}",
                symbol=sym,
                entity_id=f"ENT_{sym.upper()}",
                trigger_type=trigger,
                as_of_timestamp=now_ts,
                lookback_hours=48,
                trigger_context={
                    "quant_score": cand.get("quant_score"),
                    "volume_ratio": vol_surge,
                    "breakout": breakout,
                    "relative_return_20d": rs_surge
                }
            )
            requests.append(req)
        return requests

