"""
Rate of Change (ROC) インジケータ
価格の変化率を測定し、モメンタムの強さを判断
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class RateOfChangeIndicator(BaseIndicator):
    """Rate of Change (ROC) インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.RATE_OF_CHANGE)
        self.name = "Rate of Change"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 10
    ) -> List[IndicatorValue]:
        """ROCを計算"""
        df = self._to_dataframe(data)

        if len(df) < period + 1:
            return []

        # 現在価格とn期間前の価格の比率を計算
        current_price = df['price']
        previous_price = df['price'].shift(period)

        # ROC = ((現在価格 - n期間前の価格) / n期間前の価格) × 100
        roc = ((current_price - previous_price) / previous_price) * 100

        results = []
        for timestamp, value in zip(df['timestamp'], roc):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"ROC({period})",
                    parameters={"period": period}
                ))

        return results
