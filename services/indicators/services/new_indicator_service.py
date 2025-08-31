"""
新しいテクニカルインジケータ計算サービス
ファクトリーパターンを使用して各インジケータを計算します
"""

import logging
from typing import List

from src.core.config import IndicatorConfig, IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint, MultiIndicatorData

from .indicator_factory import indicator_factory

logger = logging.getLogger(__name__)


class NewIndicatorService:
    """新しいテクニカルインジケータ計算サービス"""

    def __init__(self):
        self.factory = indicator_factory

    def calculate_sma(
        self,
        data: List[MarketDataPoint],
        period: int
    ) -> List[IndicatorValue]:
        """単純移動平均（SMA）を計算"""
        indicator = self.factory.get_indicator(IndicatorType.SMA)
        return indicator.calculate(data, period=period)

    def calculate_ema(
        self,
        data: List[MarketDataPoint],
        period: int
    ) -> List[IndicatorValue]:
        """指数移動平均（EMA）を計算"""
        indicator = self.factory.get_indicator(IndicatorType.EMA)
        return indicator.calculate(data, period=period)

    def calculate_rsi(
        self,
        data: List[MarketDataPoint],
        period: int = 14
    ) -> List[IndicatorValue]:
        """相対力指数（RSI）を計算"""
        indicator = self.factory.get_indicator(IndicatorType.RSI)
        return indicator.calculate(data, period=period)

    def calculate_macd(
        self,
        data: List[MarketDataPoint],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> List[IndicatorValue]:
        """MACD（移動平均収束発散）を計算"""
        indicator = self.factory.get_indicator(IndicatorType.MACD)
        return indicator.calculate(data, fast=fast, slow=slow, signal=signal)

    def calculate_bollinger_bands(
        self,
        data: List[MarketDataPoint],
        period: int = 20,
        std_dev: float = 2.0
    ) -> List[IndicatorValue]:
        """ボリンジャーバンドを計算"""
        indicator = self.factory.get_indicator(IndicatorType.BOLLINGER_BANDS)
        return indicator.calculate(data, period=period, std_dev=std_dev)

    def calculate_stochastic(
        self,
        data: List[MarketDataPoint],
        k_period: int = 14,
        d_period: int = 3,
        slowing: int = 3
    ) -> List[IndicatorValue]:
        """ストキャスティクスオシレーターを計算"""
        indicator = self.factory.get_indicator(IndicatorType.STOCHASTIC)
        return indicator.calculate(
            data,
            k_period=k_period,
            d_period=d_period,
            slowing=slowing
        )

    def calculate_atr(self, data: List[MarketDataPoint], period: int = 14) -> List[IndicatorValue]:
        """平均真の範囲（ATR）を計算"""
        indicator = self.factory.get_indicator(IndicatorType.ATR)
        return indicator.calculate(data, period=period)

    def calculate_multiple_indicators(
        self,
        data: List[MarketDataPoint],
        indicator_configs: List[IndicatorConfig]
    ) -> List[MultiIndicatorData]:
        """複数のインジケータを一度に計算"""
        if not data:
            return []

        # 各インジケータを計算
        all_indicators = {}

        for config in indicator_configs:
            if not config.is_active:
                continue

            try:
                if config.type == IndicatorType.SMA:
                    indicators = self.calculate_sma(
                        data, config.parameters["period"])
                elif config.type == IndicatorType.EMA:
                    indicators = self.calculate_ema(
                        data, config.parameters["period"])
                elif config.type == IndicatorType.RSI:
                    indicators = self.calculate_rsi(
                        data, config.parameters["period"])
                elif config.type == IndicatorType.MACD:
                    indicators = self.calculate_macd(
                        data,
                        config.parameters["fast"],
                        config.parameters["slow"],
                        config.parameters["signal"]
                    )
                elif config.type == IndicatorType.BOLLINGER_BANDS:
                    indicators = (
                        self.calculate_bollinger_bands(
                            data,
                            config.parameters["period"],
                            config.parameters["std_dev"]
                        )
                    )
                elif config.type == IndicatorType.STOCHASTIC:
                    indicators = (
                        self.calculate_stochastic(
                            data,
                            config.parameters["k_period"],
                            config.parameters["d_period"],
                            config.parameters["slowing"]
                        )
                    )
                elif config.type == IndicatorType.ATR:
                    indicators = self.calculate_atr(
                        data, config.parameters["period"])
                else:
                    logger.warning(f"未対応のインジケータタイプ: {config.type}")
                    continue

                # インジケータ名をキーとして保存
                all_indicators[config.name] = indicators

            except Exception as e:
                logger.error(f"インジケータ計算エラー ({config.name}): {str(e)}")
                continue

        # タイムスタンプごとにデータを整理
        timestamp_data = {}

        for indicator_name, indicators in all_indicators.items():
            for indicator in indicators:
                timestamp_key = indicator.timestamp.isoformat()

                if timestamp_key not in timestamp_data:
                    timestamp_data[timestamp_key] = {
                        "timestamp": indicator.timestamp,
                        "values": {}
                    }

                timestamp_data[timestamp_key]["values"][indicator_name] = (
                    indicator.value
                )

        # MultiIndicatorDataのリストに変換
        results = []
        for timestamp_key in sorted(timestamp_data.keys()):
            data_point = timestamp_data[timestamp_key]
            results.append(MultiIndicatorData(
                timestamp=data_point["timestamp"],
                values=data_point["values"]
            ))

        return results


# シングルトンインスタンス
new_indicator_service = NewIndicatorService()
