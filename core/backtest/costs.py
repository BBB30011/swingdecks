class TransactionCostEngine:
    """
    Menghitung slippage dan commission untuk entry dan exit trade.
    """
    
    @staticmethod
    def calculate_entry(price: float, shares: float, commission_rate: float, slippage_rate: float) -> tuple[float, float]:
        """
        Mengembalikan (effective_price, total_cost)
        Effective price pada entry (BUY) = price * (1 + slippage_rate)
        """
        effective_price = price * (1 + slippage_rate)
        notional = effective_price * shares
        commission = notional * commission_rate
        return effective_price, commission
        
    @staticmethod
    def calculate_exit(price: float, shares: float, commission_rate: float, slippage_rate: float) -> tuple[float, float]:
        """
        Mengembalikan (effective_price, total_cost)
        Effective price pada exit (SELL) = price * (1 - slippage_rate)
        """
        effective_price = price * (1 - slippage_rate)
        notional = effective_price * shares
        commission = notional * commission_rate
        return effective_price, commission
