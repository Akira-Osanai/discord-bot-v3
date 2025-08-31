"""
相対力指数（RSI）インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class RSIIndicator(BaseIndicator):
    """相対力指数（RSI）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.RSI)
        self.name = "RSI"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """相対力指数（RSI）を計算"""
        df = self._to_dataframe(data)

        # 価格変化を計算
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        results = []
        for timestamp, value in zip(df['timestamp'], rsi):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"RSI({period})",
                    parameters={"period": period}
                ))

        return results
