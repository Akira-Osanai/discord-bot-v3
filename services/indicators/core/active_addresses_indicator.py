"""
アクティブアドレス数インジケータ
ビットコインネットワークのアクティブアドレス数を計算します
"""

import logging
from typing import List

import pandas as pd
import requests

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class ActiveAddressesIndicator(BaseIndicator):
    """アクティブアドレス数インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.ACTIVE_ADDRESSES)
        self.name = "Active Addresses"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 7
    ) -> List[IndicatorValue]:
        """アクティブアドレス数を計算"""
        if len(data) < period:
            return []

        try:
            # Blockchain.com APIからアクティブアドレス数を取得
            url = "https://api.blockchain.info/charts/n-unique-addresses"
            params = {
                "timespan": f"{period}days",
                "rollingAverage": "24hours",
                "format": "json"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            addresses_data = response.json()

            results = []

            for point in addresses_data.get("values", []):
                timestamp = pd.to_datetime(point["x"], unit="s")
                addresses = point["y"]

                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=addresses,
                    name="Active Addresses",
                    parameters={"period": period}
                ))

            logger.info(f"アクティブアドレス数計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"アクティブアドレス数計算エラー: {str(e)}")
            return []

    def _estimate_from_volume(self, data: List[MarketDataPoint], period: int) -> List[IndicatorValue]:
        """取引量からアクティブアドレス数を推定（フォールバック）"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 取引量の変化率からアクティブアドレス数を推定
        volume_change = df['volume'].pct_change()

        # アクティブアドレス数は取引量と正の相関があると仮定
        base_addresses = 1000000  # ベースライン100万アドレス
        estimated_addresses = base_addresses + (volume_change * 100000)

        results = []

        for timestamp, value in zip(df['timestamp'], estimated_addresses):
            if not pd.isna(value) and value > 0:
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=int(value),
                    name="Estimated Active Addresses",
                    parameters={"period": period, "method": "volume_based"}
                ))

        return results
