"""
CCI (Commodity Channel Index) インジケータ
価格の周期性とトレンドを測定するオシレーター系インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class CCIIndicator(BaseIndicator):
    """CCI (Commodity Channel Index) インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.CCI)
        self.name = "CCI"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """CCIを計算"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 典型的価格 (Typical Price) = (High + Low + Close) / 3
        typical_price = (df['high'] + df['low'] + df['price']) / 3

        # 移動平均
        sma_tp = typical_price.rolling(window=period).mean()

        # 平均偏差
        mean_deviation = typical_price.rolling(window=period).apply(
            lambda x: abs(x - x.mean()).mean()
        )

        # CCI = (典型的価格 - 移動平均) / (0.015 × 平均偏差)
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)

        results = []
        for timestamp, value in zip(df['timestamp'], cci):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"CCI({period})",
                    parameters={"period": period}
                ))

        return results
