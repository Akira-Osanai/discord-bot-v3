"""
VWAP (Volume Weighted Average Price) インジケータ
出来高加重平均価格
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class VWAPIndicator(BaseIndicator):
    """VWAP (Volume Weighted Average Price) インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.VWAP)
        self.name = "VWAP"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """VWAPを計算"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 典型価格（Typical Price）
        typical_price = (df['high'] + df['low'] + df['price']) / 3

        # 出来高加重価格
        volume_price = typical_price * df['volume']

        # 累積出来高
        cumulative_volume = df['volume'].rolling(window=period).sum()

        # 累積出来高加重価格
        cumulative_volume_price = volume_price.rolling(window=period).sum()

        # VWAP計算
        vwap = cumulative_volume_price / cumulative_volume

        results = []
        for timestamp, value in zip(df['timestamp'], vwap):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"VWAP({period})",
                    parameters={"period": period}
                ))

        return results
