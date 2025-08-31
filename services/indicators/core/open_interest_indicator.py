"""
Open Interest（オープンインタレスト）インジケータ
先物・オプション市場の未決済契約数を測定します
"""

import logging
from typing import List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class OpenInterestIndicator(BaseIndicator):
    """Open Interest（オープンインタレスト）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.OPEN_INTEREST)
        self.name = "Open Interest"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20
    ) -> List[IndicatorValue]:
        """Open Interestを計算"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # 実際のオープンインタレストデータがないため、
            # 価格とボリュームから推定
            price_changes = df['price'].pct_change().abs()

            # 価格変動とボリュームの組み合わせで
            # オープンインタレストの変化を推定
            # 価格変動が大きく、ボリュームが高いほど
            # オープンインタレストが増加すると仮定

            # 移動平均で正規化
            rolling_price_change = price_changes.rolling(window=period).mean()

            # 0-100のスケールに正規化
            max_change = rolling_price_change.max()
            if max_change > 0:
                normalized_oi = (rolling_price_change / max_change) * 100
            else:
                normalized_oi = rolling_price_change * 0

            results = []
            for timestamp, value in zip(df['timestamp'], normalized_oi):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 2),
                        name="Open Interest",
                        parameters={
                            "period": period,
                            "method": "price_volatility_based",
                            "estimated": True
                        }
                    ))

            logger.info(f"Open Interest計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"Open Interest計算エラー: {str(e)}")
            return []
