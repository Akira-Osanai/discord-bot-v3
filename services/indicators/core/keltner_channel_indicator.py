from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class KeltnerChannelIndicator(BaseIndicator):
    """Keltner Channel インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.KELTNER_CHANNEL)
        self.name = "Keltner Channel"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20,
        multiplier: float = 2.0
    ) -> List[IndicatorValue]:
        """Keltner Channelを計算"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 典型価格（Typical Price）
        typical_price = (df['high'] + df['low'] + df['price']) / 3

        # 移動平均（中線）
        middle_line = typical_price.rolling(window=period).mean()

        # 平均真の範囲（ATR）
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['price'].shift(1))
        low_close = abs(df['low'] - df['price'].shift(1))

        true_range = pd.concat(
            [high_low, high_close, low_close], axis=1
        ).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        # 上線と下線
        upper_line = middle_line + (multiplier * atr)
        lower_line = middle_line - (multiplier * atr)

        results = []

        # 中線（移動平均）
        for timestamp, value in zip(df['timestamp'], middle_line):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Keltner Middle({period})",
                    parameters={"period": period, "multiplier": multiplier}
                ))

        # 上線
        for timestamp, value in zip(df['timestamp'], upper_line):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Keltner Upper({period})",
                    parameters={"period": period, "multiplier": multiplier}
                ))

        # 下線
        for timestamp, value in zip(df['timestamp'], lower_line):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Keltner Lower({period})",
                    parameters={"period": period, "multiplier": multiplier}
                ))

        return results
