"""
OBV (On-Balance Volume) インジケータ
価格と出来高の関係を分析するボリューム系インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class OBVIndicator(BaseIndicator):
    """OBV (On-Balance Volume) インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.OBV)
        self.name = "OBV"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """OBVを計算"""
        df = self._to_dataframe(data)

        if len(df) < 2:
            return []

        # 価格変化を計算
        price_change = df['price'].diff()

        # OBVの初期値を設定
        obv = pd.Series(0.0, index=df.index)
        obv.iloc[0] = df['volume'].iloc[0]  # 最初の値は最初の出来高

        # OBVを計算
        for i in range(1, len(df)):
            if price_change.iloc[i] > 0:  # 価格上昇
                obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
            elif price_change.iloc[i] < 0:  # 価格下降
                obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
            else:  # 価格変化なし
                obv.iloc[i] = obv.iloc[i-1]

        results = []
        for timestamp, value in zip(df['timestamp'], obv):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"OBV({period})",
                    parameters={"period": period}
                ))

        return results
