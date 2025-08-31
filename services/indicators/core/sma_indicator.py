"""
単純移動平均（SMA）インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class SMAIndicator(BaseIndicator):
    """単純移動平均（SMA）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.SMA)
        self.name = "SMA"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int
    ) -> List[IndicatorValue]:
        """単純移動平均（SMA）を計算"""
        df = self._to_dataframe(data)
        sma = df['price'].rolling(window=period).mean()

        results = []
        for i, (timestamp, value) in enumerate(zip(df['timestamp'], sma)):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 6),
                    name=f"SMA({period})",
                    parameters={"period": period}
                ))

        return results
