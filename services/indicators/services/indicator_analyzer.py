"""
インジケータ分析処理
各インジケータの状態分析とシグナル生成を行います
"""

import logging
from typing import Dict, List

from src.core.config import AppConfig
from src.models.schemas import MultiIndicatorData

logger = logging.getLogger(__name__)


class IndicatorAnalyzer:
    """インジケータ分析クラス"""

    def __init__(self):
        self.weights = AppConfig.INDICATOR_WEIGHTS

    def analyze_indicator_states(
        self,
        latest: MultiIndicatorData,
        previous: MultiIndicatorData,
        current_price: float
    ) -> Dict:
        """各インジケータの状態を分析"""
        states = {}

        for indicator_name, value in latest.values.items():
            weight_info_available = indicator_name in self.weights
            logger.info(
                f"インジケータ分析中: {indicator_name}, "
                f"重み情報: {weight_info_available}")

            if indicator_name not in self.weights:
                logger.warning(f"重み情報が見つからないインジケータ: {indicator_name}")
                continue

            weight_info = self.weights[indicator_name]
            state = self._analyze_single_indicator(
                indicator_name, value, previous, current_price, weight_info
            )
            states[indicator_name] = state

        return states

    def analyze_new_indicator_types(
        self,
        indicator_states: Dict,
        latest: MultiIndicatorData,
        previous: MultiIndicatorData,
        current_price: float
    ):
        """新しいインジケータタイプの分析を追加"""
        logger.info(f"新しいインジケータ分析開始: {list(latest.values.keys())}")

        # 新しいインジケータの存在確認
        new_indicators = [
            "Hash Rate", "Active Addresses", "Funding Rate",
            "Fear & Greed Index", "Correlation", "Realized Volatility"
        ]

        # インジケータマッピングの作成
        indicator_mapping = self._create_indicator_mapping(
            new_indicators, list(latest.values.keys()))

        # マッピングされたインジケータの状態を追加
        self._add_mapped_indicator_states(
            indicator_states, indicator_mapping, latest, previous)

        logger.info(f"新しいインジケータ分析完了: {list(indicator_states.keys())}")

    def _create_indicator_mapping(
        self,
        new_indicators: List[str],
        actual_names: List[str]
    ) -> Dict[str, str]:
        """インジケータ名のマッピングを作成"""
        mapping = {}
        for indicator in new_indicators:
            for actual_name in actual_names:
                if indicator.lower() == actual_name.lower():
                    mapping[indicator] = actual_name
                    break
        return mapping

    def _add_mapped_indicator_states(
        self,
        indicator_states: Dict,
        mapping: Dict[str, str],
        latest: MultiIndicatorData,
        previous: MultiIndicatorData
    ):
        """マッピングされたインジケータの状態を追加"""
        for indicator, actual_name in mapping.items():
            if (actual_name in latest.values and
                    indicator not in indicator_states):

                value = latest.values[actual_name]
                previous_value = previous.values.get(
                    actual_name) if previous else value

                change = value - previous_value
                change_pct = (change / previous_value * 100) if previous_value != 0 else 0

                # インジケータ状態を作成
                state = self._create_indicator_state(
                    indicator, value, change, change_pct)

                if state:
                    indicator_states[indicator] = state
                    logger.info(f"✓ {indicator} の状態を追加しました")

    def _create_indicator_state(
        self,
        indicator: str,
        value: float,
        change: float,
        change_pct: float
    ) -> Dict:
        """インジケータ状態を作成"""
        state_configs = {
            "Hash Rate": {
                "weight": 0.6, "type": "onchain",
                "description": "ネットワーク指標",
                "strength_divisor": 10
            },
            "Active Addresses": {
                "weight": 0.5, "type": "onchain",
                "description": "ネットワーク指標",
                "strength_divisor": 10
            },
            "Fear & Greed Index": {
                "weight": 0.5, "type": "sentiment",
                "description": "市場心理指標",
                "custom_strength": lambda v: abs(50 - v) / 50
            },
            "Correlation": {
                "weight": 0.6, "type": "correlation",
                "description": "伝統市場との相関関係",
                "custom_strength": lambda v: abs(v)
            },
            "Realized Volatility": {
                "weight": 0.7, "type": "volatility",
                "description": "過去の価格変動率",
                "custom_strength": lambda v: min(v / 100, 1.0)
            }
        }

        config = state_configs.get(indicator)
        if not config:
            return None

        custom_strength = config.get("custom_strength")
        if custom_strength:
            strength = custom_strength(value)
        else:
            divisor = config.get("strength_divisor", 10)
            strength = min(abs(change_pct) / divisor, 1.0)

        return {
            "name": indicator,
            "value": value,
            "weight": config["weight"],
            "type": config["type"],
            "description": config["description"],
            "status": "up" if change > 0 else "down",
            "signal": self._determine_signal(indicator, change),
            "strength": strength,
            "change": change,
            "change_pct": change_pct
        }

    def _analyze_single_indicator(
        self,
        name: str,
        value: float,
        previous: MultiIndicatorData,
        current_price: float,
        weight_info: Dict
    ) -> Dict:
        """単一インジケータの状態を分析"""
        state = {
            "name": name,
            "value": value,
            "weight": weight_info["weight"],
            "type": weight_info["type"],
            "description": weight_info["description"],
            "status": "neutral",
            "signal": "neutral",
            "strength": 0.0
        }

        # 前回値との比較
        if previous and name in previous.values:
            prev_value = previous.values[name]
            change = value - prev_value
            change_pct = (change / prev_value * 100) if prev_value != 0 else 0

            state["change"] = change
            state["change_pct"] = change_pct

            # 状態判定
            if change > 0:
                state["status"] = "up"
                state["signal"] = "bullish"
                state["strength"] = min(abs(change_pct) / 10, 1.0)  # 0-1の範囲
            elif change < 0:
                state["status"] = "down"
                state["signal"] = "bearish"
                state["strength"] = min(abs(change_pct) / 10, 1.0)

        # インジケータ固有の判定
        state.update(self._get_indicator_specific_analysis(
            name, value, current_price))

        return state

    def _get_indicator_specific_analysis(
        self,
        name: str,
        value: float,
        current_price: float
    ) -> Dict:
        """インジケータ固有の分析"""
        analysis = {}

        if name == "RSI":
            if value > 70:
                analysis["signal"] = "overbought"
                analysis["strength"] = min((value - 70) / 30, 1.0)
            elif value < 30:
                analysis["signal"] = "oversold"
                analysis["strength"] = min((30 - value) / 30, 1.0)

        elif name == "MACD":
            if value > 0:
                analysis["signal"] = "bullish"
                analysis["strength"] = min(value / 1000, 1.0)
            else:
                analysis["signal"] = "bearish"
                analysis["strength"] = min(abs(value) / 1000, 1.0)

        elif name == "Stochastic":
            if value > 80:
                analysis["signal"] = "overbought"
                analysis["strength"] = min((value - 80) / 20, 1.0)
            elif value < 20:
                analysis["signal"] = "oversold"
                analysis["strength"] = min((20 - value) / 20, 1.0)

        elif name == "Williams %R":
            if value > -20:
                analysis["signal"] = "overbought"
                analysis["strength"] = min((value + 20) / 20, 1.0)
            elif value < -80:
                analysis["signal"] = "oversold"
                analysis["strength"] = min((-80 - value) / 20, 1.0)

        elif name == "CCI":
            if value > 100:
                analysis["signal"] = "overbought"
                analysis["strength"] = min((value - 100) / 100, 1.0)
            elif value < -100:
                analysis["signal"] = "oversold"
                analysis["strength"] = min((-100 - value) / 100, 1.0)

        elif name == "ADX":
            if value > 25:
                analysis["signal"] = "strong_trend"
                analysis["strength"] = min((value - 25) / 25, 1.0)
            else:
                analysis["signal"] = "weak_trend"
                analysis["strength"] = max(1.0 - (25 - value) / 25, 0.0)

        elif name == "Money Flow Index":
            if value > 80:
                analysis["signal"] = "overbought"
                analysis["strength"] = min((value - 80) / 20, 1.0)
            elif value < 20:
                analysis["signal"] = "oversold"
                analysis["strength"] = min((20 - value) / 20, 1.0)

        return analysis

    def _determine_signal(self, indicator: str, change: float) -> str:
        """インジケータのシグナルを決定"""
        neutral_indicators = ["Fear & Greed Index", "Correlation", "Realized Volatility"]
        
        if indicator in neutral_indicators:
            return "neutral"
        elif change > 0:
            return "bullish"
        else:
            return "bearish"
