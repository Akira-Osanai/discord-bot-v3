"""
実現ボラティリティインジケータ
過去の価格変動から実現ボラティリティを計算します
"""

import logging
from typing import List

import numpy as np
import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class RealizedVolatilityIndicator(BaseIndicator):
    """実現ボラティリティインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.REALIZED_VOLATILITY)
        self.name = "Realized Volatility"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """実現ボラティリティを計算"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # 対数収益率を計算
            log_returns = np.log(df['price'] / df['price'].shift(1))

            # 実現ボラティリティ（年率換算）
            realized_vol = log_returns.rolling(
                window=period).std() * np.sqrt(252) * 100

            results = []

            for timestamp, value in zip(df['timestamp'], realized_vol):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 2),
                        name="Realized Volatility (%)",
                        parameters={"period": period, "annualized": True}
                    ))

            logger.info(f"実現ボラティリティ計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"実現ボラティリティ計算エラー: {str(e)}")
            return []

    def calculate_parkinson_volatility(self, data: List[MarketDataPoint], period: int = 20) -> List[IndicatorValue]:
        """Parkinsonボラティリティを計算（High-Lowデータ使用）"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # High-Lowデータからボラティリティを計算
            log_hl = np.log(df['high'] / df['low'])
            parkinson_vol = np.sqrt(
                (1 / (4 * np.log(2))) *
                (log_hl ** 2).rolling(window=period).mean()
            ) * np.sqrt(252) * 100

            results = []

            for timestamp, value in zip(df['timestamp'], parkinson_vol):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 2),
                        name="Parkinson Volatility (%)",
                        parameters={"period": period,
                                    "method": "high_low", "annualized": True}
                    ))

            return results

        except Exception as e:
            logger.error(f"Parkinsonボラティリティ計算エラー: {str(e)}")
            return []

    def calculate_garman_klass_volatility(self, data: List[MarketDataPoint], period: int = 20) -> List[IndicatorValue]:
        """Garman-Klassボラティリティを計算（OHLCデータ使用）"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # OHLCデータからボラティリティを計算
            log_hl = np.log(df['high'] / df['low'])
            log_co = np.log(df['price'] / df['open'])

            gk_vol = np.sqrt(
                (0.5 * (log_hl ** 2) - (2 * np.log(2) - 1) *
                 (log_co ** 2)).rolling(window=period).mean()
            ) * np.sqrt(252) * 100

            results = []

            for timestamp, value in zip(df['timestamp'], gk_vol):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 2),
                        name="Garman-Klass Volatility (%)",
                        parameters={"period": period,
                                    "method": "ohlc", "annualized": True}
                    ))

            return results

        except Exception as e:
            logger.error(f"Garman-Klassボラティリティ計算エラー: {str(e)}")
            return []
