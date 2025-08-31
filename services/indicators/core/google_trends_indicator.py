"""
Google Trends（グーグルトレンド）インジケータ
検索トレンドから市場の関心度を測定します
"""

import logging
from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class GoogleTrendsIndicator(BaseIndicator):
    """Google Trends（グーグルトレンド）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.GOOGLE_TRENDS)
        self.name = "Google Trends"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20,
        search_terms: List[str] = None
    ) -> List[IndicatorValue]:
        """Google Trendsを計算"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # 実際のGoogle Trends APIがないため、
            # 価格変化から検索関心度を推定
            price_changes = df['price'].pct_change().abs()

            # 価格変動が大きいほど検索関心度が高いと仮定
            # 移動平均で正規化
            rolling_volatility = price_changes.rolling(window=period).mean()

            # 0-100のスケールに正規化
            max_vol = rolling_volatility.max()
            if max_vol > 0:
                normalized_trends = (rolling_volatility / max_vol) * 100
            else:
                normalized_trends = rolling_volatility * 0

            results = []
            for timestamp, value in zip(df['timestamp'], normalized_trends):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 2),
                        name="Google Trends",
                        parameters={
                            "period": period,
                            "method": "price_volatility_based",
                            "search_terms": search_terms or ["BTC", "Bitcoin"]
                        }
                    ))

            logger.info(f"Google Trends計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"Google Trends計算エラー: {str(e)}")
            return []
