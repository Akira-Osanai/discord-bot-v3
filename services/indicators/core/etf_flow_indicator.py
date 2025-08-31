from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator


class ETFFlowIndicator(BaseIndicator):
    """ETF Flow インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.ETF_FLOW)
        self.name = "ETF Flow"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """ETF Flowを計算"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 価格ベースのフロー計算（Bitcoin用）
        # 価格の変化率をフローとして扱う
        price_change = df['price'].pct_change() * 100

        # 価格の移動平均
        price_ma = df['price'].rolling(window=period).mean()

        # 価格の強度（現在価格 / 移動平均）
        price_strength = df['price'] / price_ma

        # ボラティリティ（価格の標準偏差）
        price_volatility = df['price'].rolling(window=period).std()

        # 価格の変化率の移動平均
        change_ma = price_change.rolling(window=period).mean()

        # デバッグ用ログ
        print(f"ETF Flow計算: データ件数={len(df)}, 列名={list(df.columns)}")
        print(f"  最初の価格: {df['price'].iloc[0] if len(df) > 0 else 'N/A'}")

        results = []

        # 価格変化率
        for timestamp, value in zip(df['timestamp'], price_change):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name="ETF Flow Change(%)",
                    parameters={"period": period}
                ))

        # 価格強度
        for timestamp, value in zip(df['timestamp'], price_strength):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name="ETF Flow Strength",
                    parameters={"period": period}
                ))

        # 価格ボラティリティ
        for timestamp, value in zip(df['timestamp'], price_volatility):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name="ETF Flow Volatility",
                    parameters={"period": period}
                ))

        # 変化率移動平均
        for timestamp, value in zip(df['timestamp'], change_ma):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name=f"ETF Flow Change MA({period})",
                    parameters={"period": period}
                ))

        return results
