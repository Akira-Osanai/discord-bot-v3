"""
Parabolic SAR インジケータ
トレンド転換とストップロス設定を行うトレンド系インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class ParabolicSARIndicator(BaseIndicator):
    """Parabolic SAR インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.PARABOLIC_SAR)
        self.name = "Parabolic SAR"

    def calculate(
        self,
        data: List[MarketDataPoint],
        acceleration: float = 0.02,
        maximum: float = 0.2
    ) -> List[IndicatorValue]:
        """Parabolic SARを計算"""
        df = self._to_dataframe(data)

        if len(df) < 2:
            return []

        # 初期値を設定
        sar = pd.Series(0.0, index=df.index)
        ep = pd.Series(0.0, index=df.index)  # Extreme Point
        af = pd.Series(0.0, index=df.index)  # Acceleration Factor

        # 最初の値の設定
        sar.iloc[0] = df['low'].iloc[0]
        ep.iloc[0] = df['high'].iloc[0]
        af.iloc[0] = acceleration

        # トレンド方向を判定（最初は上昇トレンドと仮定）
        trend_up = True

        for i in range(1, len(df)):
            if trend_up:
                # 上昇トレンド
                sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * \
                    (ep.iloc[i-1] - sar.iloc[i-1])

                # 前回のSARが現在の安値より低いかチェック
                low_prev = df['low'].iloc[i-1]
                if sar.iloc[i] > low_prev:
                    sar.iloc[i] = low_prev

                # 極値の更新
                if df['high'].iloc[i] > ep.iloc[i-1]:
                    ep.iloc[i] = df['high'].iloc[i]
                    af.iloc[i] = min(af.iloc[i-1] + acceleration, maximum)
                else:
                    ep.iloc[i] = ep.iloc[i-1]
                    af.iloc[i] = af.iloc[i-1]

                # トレンド転換チェック
                if df['low'].iloc[i] < sar.iloc[i-1]:
                    trend_up = False
                    sar.iloc[i] = ep.iloc[i-1]
                    ep.iloc[i] = df['low'].iloc[i]
                    af.iloc[i] = acceleration
            else:
                # 下降トレンド
                sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * \
                    (ep.iloc[i-1] - sar.iloc[i-1])

                # 前回のSARが現在の高値より高いかチェック
                high_prev = df['high'].iloc[i-1]
                if sar.iloc[i] < high_prev:
                    sar.iloc[i] = high_prev

                # 極値の更新
                if df['low'].iloc[i] < ep.iloc[i-1]:
                    ep.iloc[i] = df['low'].iloc[i]
                    af.iloc[i] = min(af.iloc[i-1] + acceleration, maximum)
                else:
                    ep.iloc[i] = ep.iloc[i-1]
                    af.iloc[i] = af.iloc[i-1]

                # トレンド転換チェック
                if df['high'].iloc[i] > sar.iloc[i-1]:
                    trend_up = True
                    sar.iloc[i] = ep.iloc[i-1]
                    ep.iloc[i] = df['high'].iloc[i]
                    af.iloc[i] = acceleration

        results = []
        for timestamp, value in zip(df['timestamp'], sar):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name="Parabolic SAR",
                    parameters={"acceleration": acceleration,
                                "maximum": maximum}
                ))

        return results
