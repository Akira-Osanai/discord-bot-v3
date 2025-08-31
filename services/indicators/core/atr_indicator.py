"""
平均真の範囲（ATR）インジケータ
"""

from typing import List

import numpy as np
import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class ATRIndicator(BaseIndicator):
    """平均真の範囲（ATR）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.ATR)
        self.name = "ATR"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """平均真の範囲（ATR）を計算"""
        df = self._to_dataframe(data)

        # True Rangeを計算
        high_low = df['high'] - df['low']
        high_close_prev = np.abs(df['high'] - df['price'].shift(1))
        low_close_prev = np.abs(df['low'] - df['price'].shift(1))

        true_range = pd.concat(
            [high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)

        # ATRを計算（指数移動平均）
        atr = true_range.ewm(span=period).mean()

        results = []
        for timestamp, value in zip(df['timestamp'], atr):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 6),
                    name=f"ATR({period})",
                    parameters={"period": period}
                ))

        return results
