"""
MACD（移動平均収束発散）インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class MACDIndicator(BaseIndicator):
    """MACD（移動平均収束発散）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.MACD)
        self.name = "MACD"

    def calculate(
        self,
        data: List[MarketDataPoint],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> List[IndicatorValue]:
        """MACD（移動平均収束発散）を計算"""
        df = self._to_dataframe(data)

        # EMAを計算
        ema_fast = df['price'].ewm(span=fast).mean()
        ema_slow = df['price'].ewm(span=slow).mean()

        # MACDラインを計算
        macd_line = ema_fast - ema_slow

        # シグナルラインを計算
        signal_line = macd_line.ewm(span=signal).mean()

        # ヒストグラムを計算
        histogram = macd_line - signal_line

        results = []
        for i, timestamp in enumerate(df['timestamp']):
            if not pd.isna(macd_line.iloc[i]):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(macd_line.iloc[i], 6),
                    name="MACD",
                    parameters={
                        "fast": fast,
                        "slow": slow,
                        "signal": signal,
                        "signal_value": (
                            round(signal_line.iloc[i], 6)
                            if not pd.isna(signal_line.iloc[i])
                            else None
                        ),
                        "histogram": (
                            round(histogram.iloc[i], 6)
                            if not pd.isna(histogram.iloc[i])
                            else None
                        )
                    }
                ))

        return results
