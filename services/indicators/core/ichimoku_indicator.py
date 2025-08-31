"""
一目均衡表（Ichimoku Cloud）インジケータ
日本の伝統的なテクニカル分析手法
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class IchimokuIndicator(BaseIndicator):
    """一目均衡表（Ichimoku Cloud）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.ICHIMOKU)
        self.name = "Ichimoku Cloud"

    def calculate(
        self,
        data: List[MarketDataPoint],
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_span_b_period: int = 52,
        displacement: int = 26
    ) -> List[IndicatorValue]:
        """一目均衡表を計算（転換線のみ）"""
        df = self._to_dataframe(data)

        if len(df) < tenkan_period:
            return []

        # 転換線（Tenkan-sen）のみを計算
        tenkan_high = df['high'].rolling(window=tenkan_period).max()
        tenkan_low = df['low'].rolling(window=tenkan_period).min()
        tenkan = (tenkan_high + tenkan_low) / 2

        results = []

        # 最新の転換線の値を返す
        for timestamp, value in zip(df['timestamp'], tenkan):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"Ichimoku Tenkan({tenkan_period})",
                    parameters={"tenkan_period": tenkan_period}
                ))
                break  # 最新の値のみを返す

        return results
