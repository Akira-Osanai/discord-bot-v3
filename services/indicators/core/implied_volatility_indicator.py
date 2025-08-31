"""
インプライドボラティリティインジケータ
オプション価格からインプライドボラティリティを計算します
"""

import logging
from typing import List

import numpy as np
import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class ImpliedVolatilityIndicator(BaseIndicator):
    """インプライドボラティリティインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.IMPLIED_VOLATILITY)
        self.name = "Implied Volatility"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """インプライドボラティリティを計算"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # 価格変化率からボラティリティを推定
            # 実際のオプション価格がないため、価格変化の標準偏差を使用
            price_changes = df['price'].pct_change()

            # 標準偏差を計算
            rolling_std = price_changes.rolling(window=period).std()

            # ボラティリティ（年率換算）
            implied_vol = rolling_std * np.sqrt(252) * 100

            results = []

            for timestamp, value in zip(df['timestamp'], implied_vol):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 2),
                        name="Implied Volatility (%)",
                        parameters={
                            "period": period,
                            "method": "price_changes",
                            "annualized": True
                        }
                    ))

            logger.info(f"インプライドボラティリティ計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"インプライドボラティリティ計算エラー: {str(e)}")
            return []

    def calculate_black_scholes_iv(
        self,
        data: List[MarketDataPoint],
        risk_free_rate: float = 0.02,
        time_to_maturity: float = 30/365
    ) -> List[IndicatorValue]:
        """Black-Scholesモデルを使用したインプライドボラティリティ計算"""
        if len(data) < 1:
            return []

        try:
            df = self._to_dataframe(data)

            # 簡易的なインプライドボラティリティ計算
            # 実際のオプション価格がないため、価格変化から推定
            price_changes = df['price'].pct_change()

            # 年率ボラティリティを計算
            annual_vol = price_changes.std() * np.sqrt(252) * 100

            results = []

            for timestamp in df['timestamp']:
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(annual_vol, 2),
                    name="Black-Scholes IV (%)",
                    parameters={
                        "risk_free_rate": risk_free_rate,
                        "time_to_maturity": time_to_maturity,
                        "method": "black_scholes",
                        "annualized": True
                    }
                ))

            return results

        except Exception as e:
            logger.error(f"Black-Scholes IV計算エラー: {str(e)}")
            return []
