"""
ストキャスティクスオシレーターインジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class StochasticIndicator(BaseIndicator):
    """ストキャスティクスオシレーターインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.STOCHASTIC)
        self.name = "Stochastic"

    def calculate(
        self,
        data: List[MarketDataPoint],
        k_period: int = 14,
        d_period: int = 3,
        slowing: int = 3
    ) -> List[IndicatorValue]:
        """ストキャスティクスオシレーターを計算"""
        df = self._to_dataframe(data)

        # %Kを計算
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        k_percent = 100 * ((df['price'] - lowest_low) /
                           (highest_high - lowest_low))

        # スローイング
        k_slowed = k_percent.rolling(window=slowing).mean()

        # %Dを計算
        d_percent = k_slowed.rolling(window=d_period).mean()

        results = []
        for i, timestamp in enumerate(df['timestamp']):
            if not pd.isna(k_slowed.iloc[i]):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(k_slowed.iloc[i], 2),
                    name=f"Stochastic({k_period}, {d_period}, {slowing})",
                    parameters={
                        "k_period": k_period,
                        "d_period": d_period,
                        "slowing": slowing,
                        "k_value": round(k_slowed.iloc[i], 2),
                        "d_value": (
                            round(d_percent.iloc[i], 2)
                            if not pd.isna(d_percent.iloc[i])
                            else None
                        )
                    }
                ))

        return results
