"""
ベータ（Beta）インジケータ
市場に対する相対的な価格変動を測定します
"""

import logging
from typing import List

import numpy as np

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class BetaIndicator(BaseIndicator):
    """ベータ（Beta）インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.BETA)
        self.name = "Beta"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 20,
        market_data: List[MarketDataPoint] = None
    ) -> List[IndicatorValue]:
        """ベータを計算"""
        if len(data) < period:
            return []

        try:
            df = self._to_dataframe(data)

            # 価格変化率を計算
            returns = df['price'].pct_change().dropna()

            if market_data:
                # 市場データがある場合、市場との相関を計算
                market_df = self._to_dataframe(market_data)
                market_returns = market_df['price'].pct_change().dropna()

                # 共通の期間でデータを揃える
                min_length = min(len(returns), len(market_returns))
                returns = returns[-min_length:]
                market_returns = market_returns[-min_length:]

                # ベータ計算（共分散 / 市場分散）
                covariance = np.cov(returns, market_returns)[0, 1]
                market_variance = np.var(market_returns)

                if market_variance > 0:
                    beta = covariance / market_variance
                else:
                    beta = 1.0
            else:
                # 市場データがない場合、単純な価格変動性を計算
                beta = returns.std() * np.sqrt(252)

            results = []
            for timestamp in df['timestamp']:
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(beta, 4),
                    name="Beta",
                    parameters={
                        "period": period,
                        "method": ("market_correlation" if market_data
                                   else "volatility_based")
                    }
                ))

            logger.info(f"ベータ計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"ベータ計算エラー: {str(e)}")
            return []
