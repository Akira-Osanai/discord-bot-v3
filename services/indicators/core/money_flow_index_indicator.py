"""
Money Flow Index (MFI) インジケータ
出来高を考慮したRSIの改良版
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class MoneyFlowIndexIndicator(BaseIndicator):
    """Money Flow Index (MFI) インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.MONEY_FLOW_INDEX)
        self.name = "Money Flow Index"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """MFIを計算"""
        df = self._to_dataframe(data)

        if len(df) < period + 1:
            return []

        # 典型価格（Typical Price）
        typical_price = (df['high'] + df['low'] + df['price']) / 3

        # マネーフロー（Money Flow）
        money_flow = typical_price * df['volume']

        # 正のマネーフローと負のマネーフロー
        positive_flow = pd.Series(0.0, index=df.index)
        negative_flow = pd.Series(0.0, index=df.index)

        # 価格の変化を計算
        price_change = typical_price.diff()

        # 正の変化と負の変化を分離
        positive_flow[price_change > 0] = money_flow[price_change > 0]
        negative_flow[price_change < 0] = money_flow[price_change < 0]

        # 期間内の累積
        positive_money_flow = positive_flow.rolling(window=period).sum()
        negative_money_flow = negative_flow.rolling(window=period).sum()

        # マネーフロー比率
        money_ratio = positive_money_flow / negative_money_flow

        # MFI計算
        mfi = 100 - (100 / (1 + money_ratio))

        results = []
        for timestamp, value in zip(df['timestamp'], mfi):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"MFI({period})",
                    parameters={"period": period}
                ))

        return results
