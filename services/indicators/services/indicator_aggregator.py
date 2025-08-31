"""
インジケータデータ集約処理
タイムスタンプの正規化とデータの集約を行います
"""

import logging
from datetime import datetime
from typing import List

import pytz

from src.models.schemas import MultiIndicatorData

logger = logging.getLogger(__name__)


class IndicatorAggregator:
    """インジケータデータ集約クラス"""

    def aggregate_latest_values(
        self,
        indicators_data: List[MultiIndicatorData]
    ) -> MultiIndicatorData:
        """各インジケータの最新値を集約"""
        return self._aggregate_values(indicators_data, is_latest=True)

    def aggregate_previous_values(
        self,
        indicators_data: List[MultiIndicatorData]
    ) -> MultiIndicatorData:
        """各インジケータの前回値を集約"""
        if len(indicators_data) < 2:
            return None
        return self._aggregate_values(indicators_data[:-1], is_latest=False)

    def _aggregate_values(
        self,
        indicators_data: List[MultiIndicatorData],
        is_latest: bool = True
    ) -> MultiIndicatorData:
        """インジケータ値を集約する共通処理"""
        aggregated_values = {}
        target_timestamp = None

        for data_point in indicators_data:
            # タイムスタンプのタイムゾーン情報を統一
            current_timestamp = self._normalize_timestamp(data_point.timestamp)

            if target_timestamp is None:
                target_timestamp = current_timestamp
            else:
                # タイムゾーン情報を統一してから比較
                target_timestamp = self._normalize_timestamp(target_timestamp)

                if is_latest and current_timestamp > target_timestamp:
                    target_timestamp = current_timestamp
                elif not is_latest and current_timestamp > target_timestamp:
                    target_timestamp = current_timestamp

            for indicator_name, value in data_point.values.items():
                if indicator_name not in aggregated_values:
                    aggregated_values[indicator_name] = value
                else:
                    # より新しいタイムスタンプの値を優先
                    if current_timestamp >= target_timestamp:
                        aggregated_values[indicator_name] = value

        logger.info(
            f"集約された{'最新' if is_latest else '前回'}値のインジケータ数: {len(aggregated_values)}")
        return MultiIndicatorData(
            timestamp=target_timestamp or datetime.now(pytz.UTC),
            values=aggregated_values
        )

    def _normalize_timestamp(self, timestamp) -> datetime:
        """タイムスタンプの正規化"""
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is None:
            return pytz.UTC.localize(timestamp)
        return timestamp
