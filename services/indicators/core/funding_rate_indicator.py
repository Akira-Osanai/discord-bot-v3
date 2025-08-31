"""
ファンディングレートインジケータ
Binanceの先物ファンディングレートを計算します
"""

import logging
from typing import List

import pandas as pd
import requests

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class FundingRateIndicator(BaseIndicator):
    """ファンディングレートインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.FUNDING_RATE)
        self.name = "Funding Rate"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 8
    ) -> List[IndicatorValue]:
        """ファンディングレートを計算"""
        if len(data) < period:
            return []

        try:
            # Binance APIからファンディングレートを取得
            url = "https://fapi.binance.com/fapi/v1/fundingRate"
            params = {
                "symbol": "BTCUSDT",
                "limit": period * 3  # 8時間ごとなので3倍
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            funding_data = response.json()

            results = []

            for item in funding_data:
                timestamp = pd.to_datetime(item["fundingTime"], unit="ms")
                funding_rate = float(item["fundingRate"]) * 100  # パーセントに変換

                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(funding_rate, 4),
                    name="Funding Rate (%)",
                    parameters={"period": period, "symbol": "BTCUSDT"}
                ))

            logger.info(f"ファンディングレート計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"ファンディングレート計算エラー: {str(e)}")
            return []

    def _estimate_from_price_volatility(self, data: List[MarketDataPoint], period: int) -> List[IndicatorValue]:
        """価格ボラティリティからファンディングレートを推定（フォールバック）"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 価格の変化率の標準偏差を計算
        price_returns = df['price'].pct_change()
        volatility = price_returns.rolling(window=period).std()

        # ボラティリティが高いとファンディングレートも高くなる傾向
        estimated_funding_rate = volatility * 100  # パーセントに変換

        results = []

        for timestamp, value in zip(df['timestamp'], estimated_funding_rate):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 4),
                    name="Estimated Funding Rate (%)",
                    parameters={"period": period, "method": "volatility_based"}
                ))

        return results
