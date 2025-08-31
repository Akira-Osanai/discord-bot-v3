"""
ボリンジャーバンドインジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class BollingerBandsIndicator(BaseIndicator):
    """ボリンジャーバンドインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.BOLLINGER_BANDS)
        self.name = "Bollinger Bands"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20,
        std_dev: float = 2.0
    ) -> List[IndicatorValue]:
        """ボリンジャーバンドを計算"""
        df = self._to_dataframe(data)

        # 中央線（SMA）を計算
        middle = df['price'].rolling(window=period).mean()

        # 標準偏差を計算
        std = df['price'].rolling(window=period).std()

        # 上下バンドを計算
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        results = []
        for i, timestamp in enumerate(df['timestamp']):
            if not pd.isna(middle.iloc[i]):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(middle.iloc[i], 6),
                    name=f"Bollinger Bands({period}, {std_dev})",
                    parameters={
                        "period": period,
                        "std_dev": std_dev,
                        "upper": round(upper.iloc[i], 6),
                        "lower": round(lower.iloc[i], 6),
                        "bandwidth": round(
                            ((upper.iloc[i] - lower.iloc[i]) /
                             middle.iloc[i]) * 100,
                            2
                        )
                    }
                ))

        return results
