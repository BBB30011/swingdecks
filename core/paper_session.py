from pydantic import BaseModel
from typing import Optional, List
from core.paper_portfolio import PaperPortfolio

class PaperSession(BaseModel):
    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    starting_capital: float
    ending_equity: float = 0.0
    positions_opened: int = 0
    positions_closed: int = 0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    max_drawdown: float = 0.0
    decisions: List[str] = []
    warnings: List[str] = []
    status: str = "RUNNING"
    
class PaperSessionManager:
    @staticmethod
    def snapshot_to_session(session_id: str, start_time: str, portfolio: PaperPortfolio) -> PaperSession:
        return PaperSession(
            session_id=session_id,
            started_at=start_time,
            starting_capital=portfolio.capital,
            ending_equity=portfolio.get_equity(),
            positions_opened=len(portfolio.positions),
            positions_closed=len([p for p in portfolio.positions.values() if p.status == "CLOSED"]),
            realized_pnl=portfolio.realized_pnl,
            unrealized_pnl=sum(p.unrealized_pnl for p in portfolio.positions.values() if p.status == "OPEN"),
            max_drawdown=portfolio.max_drawdown,
            status="RUNNING"
        )
