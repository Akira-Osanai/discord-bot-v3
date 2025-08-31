from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class DonchianChannelIndicator(BaseIndicator):
    """Donchian Channel インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.DONCHIAN_CHANNEL)
        self.name = "Donchian Channel"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """Donchian Channelを計算"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 上線（期間内の最高値）
        upper_line = df['high'].rolling(window=period).max()

        # 下線（期間内の最安値）
        lower_line = df['low'].rolling(window=period).min()

        # 中線（上線と下線の平均）
        middle_line = (upper_line + lower_line) / 2

        results = []

        # 上線
        for timestamp, value in zip(df['timestamp'], upper_line):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Donchian Upper({period})",
                    parameters={"period": period}
                ))

        # 中線
        for timestamp, value in zip(df['timestamp'], middle_line):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Donchian Middle({period})",
                    parameters={"period": period}
                ))

        # 下線
        for timestamp, value in zip(df['timestamp'], lower_line):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Donchian Lower({period})",
                    parameters={"period": period}
                ))

        return results
