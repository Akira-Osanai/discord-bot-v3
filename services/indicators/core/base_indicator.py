"""
インジケータの基底クラス
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

logger = logging.getLogger(__name__)


class BaseIndicator(ABC):
    """インジケータの基底クラス"""

    def __init__(self, indicator_type: IndicatorType):
        self.indicator_type = indicator_type
        self.name = ""

    @abstractmethod
    def calculate(
        self,
        data: List[MarketDataPoint],
        **kwargs
    ) -> List[IndicatorValue]:
        """インジケータを計算する抽象メソッド"""
        pass

    def _to_dataframe(self, data: List[MarketDataPoint]) -> pd.DataFrame:
        """MarketDataPointのリストをDataFrameに変換"""
        records = []
        for point in data:
            records.append({
                'timestamp': point.timestamp,
                'open': point.open,
                'high': point.high,
                'low': point.low,
                'price': point.price,  # price属性を使用
                'volume': point.volume
            })

        return pd.DataFrame(records)

    def _create_indicator_value(
        self,
        timestamp: Any,
        value: float,
        name: str,
        parameters: Dict[str, Any]
    ) -> IndicatorValue:
        """IndicatorValueオブジェクトを作成"""
        return IndicatorValue(
            name=name,
            type=self.indicator_type.value,
            timestamp=timestamp,
            value=value,
            parameters=parameters
        )
