"""
ADX (Average Directional Index) インジケータ
トレンドの強さを測定するトレンド系インジケータ
"""

from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class ADXIndicator(BaseIndicator):
    """ADX (Average Directional Index) インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.ADX)
        self.name = "ADX"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """ADXを計算"""
        df = self._to_dataframe(data)

        if len(df) < period + 1:
            return []

        # True Range (TR) の計算
        high_low = df['high'] - df['low']
        high_close_prev = abs(df['high'] - df['price'].shift(1))
        low_close_prev = abs(df['low'] - df['price'].shift(1))

        tr_data = [high_low, high_close_prev, low_close_prev]
        tr = pd.concat(tr_data, axis=1).max(axis=1)

        # Directional Movement (DM) の計算
        up_move = df['high'] - df['high'].shift(1)
        down_move = df['low'].shift(1) - df['low']

        plus_dm = pd.Series(0.0, index=df.index)
        minus_dm = pd.Series(0.0, index=df.index)

        # +DM: 上昇幅が下降幅より大きく、かつ上昇幅が0より大きい場合
        plus_condition = (up_move > down_move) & (up_move > 0)
        plus_dm[plus_condition] = up_move[plus_condition]

        # -DM: 下降幅が上昇幅より大きく、かつ下降幅が0より大きい場合
        minus_condition = (down_move > up_move) & (down_move > 0)
        minus_dm[minus_condition] = down_move[minus_condition]

        # 平滑化されたTR、+DM、-DM
        tr_smooth = tr.rolling(window=period).mean()
        plus_dm_smooth = plus_dm.rolling(window=period).mean()
        minus_dm_smooth = minus_dm.rolling(window=period).mean()

        # Directional Indicators (+DI, -DI)
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)

        # Directional Index (DX)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # Average Directional Index (ADX)
        adx = dx.rolling(window=period).mean()

        results = []
        for timestamp, value in zip(df['timestamp'], adx):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"ADX({period})",
                    parameters={"period": period}
                ))

        return results
