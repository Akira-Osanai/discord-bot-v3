"""
ハッシュレートインジケータ
ビットコインネットワークのハッシュレートを計算します
"""

import logging
from typing import List

import pandas as pd
import requests

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class HashRateIndicator(BaseIndicator):
    """ハッシュレートインジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.HASH_RATE)
        self.name = "Hash Rate"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """ハッシュレートを計算"""
        if len(data) < period:
            return []

        try:
            # Blockchain.com APIからハッシュレートデータを取得
            url = "https://api.blockchain.info/charts/hash-rate"
            params = {
                "timespan": f"{period}days",
                "rollingAverage": "24hours",
                "format": "json"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            hash_rate_data = response.json()

            results = []

            for point in hash_rate_data.get("values", []):
                timestamp = pd.to_datetime(point["x"], unit="s")
                hash_rate_th = point["y"] / 1e12  # TH/sに変換

                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(hash_rate_th, 2),
                    name="Hash Rate (TH/s)",
                    parameters={"period": period}
                ))

            logger.info(f"ハッシュレート計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"ハッシュレート計算エラー: {str(e)}")
            return []

    def _get_hash_rate_from_price(self, data: List[MarketDataPoint], period: int) -> List[IndicatorValue]:
        """価格データからハッシュレートを推定（フォールバック）"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 価格の変化率からハッシュレートの変化を推定
        price_change = df['price'].pct_change()

        # ハッシュレートは価格と正の相関があると仮定
        estimated_hash_rate = 100 + (price_change * 50)  # ベースライン100 TH/s

        results = []

        for timestamp, value in zip(df['timestamp'], estimated_hash_rate):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 2),
                    name="Estimated Hash Rate (TH/s)",
                    parameters={"period": period, "method": "price_based"}
                ))

        return results
