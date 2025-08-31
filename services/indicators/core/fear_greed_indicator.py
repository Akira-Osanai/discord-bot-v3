"""
Fear & Greed Indexインジケータ
市場のFear & Greed Indexを取得します
"""

import logging
from typing import List

import pandas as pd
import requests

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class FearGreedIndicator(BaseIndicator):
    """Fear & Greed Indexインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.FEAR_GREED_INDEX)
        self.name = "Fear & Greed Index"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 7
    ) -> List[IndicatorValue]:
        """Fear & Greed Indexを取得"""
        if len(data) < period:
            return []

        try:
            # Alternative.me APIからFear & Greed Indexを取得
            url = "https://api.alternative.me/fng/"
            params = {
                "limit": period
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            fng_data = response.json()

            results = []

            for item in fng_data.get("data", []):
                # タイムスタンプの処理を修正
                if "timestamp" in item:
                    try:
                        timestamp = pd.to_datetime(item["timestamp"])
                    except:
                        # Unix timestampの場合
                        timestamp = pd.to_datetime(int(item["timestamp"]), unit='s')
                else:
                    continue
                
                value = int(item["value"])
                classification = item["value_classification"]

                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=value,
                    name=f"Fear & Greed ({classification})",
                    parameters={"period": period,
                                "classification": classification}
                ))

            logger.info(f"Fear & Greed Index計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"Fear & Greed Index計算エラー: {str(e)}")
            return []

    def _estimate_from_price_momentum(self, data: List[MarketDataPoint], period: int) -> List[IndicatorValue]:
        """価格モメンタムからFear & Greed Indexを推定（フォールバック）"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 価格の変化率とボラティリティを計算
        price_returns = df['price'].pct_change()
        momentum = price_returns.rolling(window=period).mean()
        volatility = price_returns.rolling(window=period).std()

        # モメンタムが高く、ボラティリティが低いとGreed
        # モメンタムが低く、ボラティリティが高いとFear
        estimated_index = 50 + (momentum * 1000) - (volatility * 500)
        estimated_index = estimated_index.clip(0, 100)  # 0-100の範囲に制限

        results = []

        for timestamp, value in zip(df['timestamp'], estimated_index):
            if not pd.isna(value):
                # 分類を決定
                if value >= 80:
                    classification = "Extreme Greed"
                elif value >= 60:
                    classification = "Greed"
                elif value >= 40:
                    classification = "Neutral"
                elif value >= 20:
                    classification = "Fear"
                else:
                    classification = "Extreme Fear"

                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=int(value),
                    name=f"Estimated Fear & Greed ({classification})",
                    parameters={
                        "period": period, "method": "momentum_based", "classification": classification}
                ))

        return results
