"""
Williams %R インジケータ
価格の過熱感・過冷感を測定するオシレーター系インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class WilliamsRIndicator(BaseIndicator):
    """Williams %R インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.WILLIAMS_R)
        self.name = "Williams %R"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """Williams %Rを計算"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 最高値と最安値の期間内での最大・最小を計算
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()

        # Williams %R = (最高値 - 終値) / (最高値 - 最安値) * -100
        williams_r = ((highest_high - df['price']) /
                      (highest_high - lowest_low)) * -100

        results = []
        for timestamp, value in zip(df['timestamp'], williams_r):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Williams %R({period})",
                    parameters={"period": period}
                ))

        return results
