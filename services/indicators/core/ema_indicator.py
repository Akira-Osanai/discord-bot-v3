"""
指数移動平均（EMA）インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class EMAIndicator(BaseIndicator):
    """指数移動平均（EMA）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.EMA)
        self.name = "EMA"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int
    ) -> List[IndicatorValue]:
        """指数移動平均（EMA）を計算"""
        df = self._to_dataframe(data)
        ema = df['price'].ewm(span=period).mean()

        results = []
        for timestamp, value in zip(df['timestamp'], ema):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 6),
                    name=f"EMA({period})",
                    parameters={"period": period}
                ))

        return results
