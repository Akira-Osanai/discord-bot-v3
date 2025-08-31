"""
インジケータシグナル生成処理
インジケータ値からシグナルと強度を生成します
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class IndicatorSignalGenerator:
    """インジケータシグナル生成クラス"""

    def calculate_trading_scores(
            self, indicator_states: Dict) -> Tuple[float, float]:
        """重み付けによる売買スコアを計算"""
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0

        for name, state in indicator_states.items():
            weight = state["weight"]
            total_weight += weight

            bullish_signals = ["bullish", "oversold"]
            bearish_signals = ["bearish", "overbought"]
            
            if state["signal"] in bullish_signals:
                buy_score += weight * state["strength"]
            elif state["signal"] in bearish_signals:
                sell_score += weight * state["strength"]

        # 正規化（0-100の範囲）
        if total_weight > 0:
            buy_score = (buy_score / total_weight) * 100
            sell_score = (sell_score / total_weight) * 100

        return round(buy_score, 2), round(sell_score, 2)

    def generate_signal_from_value(self, indicator: str, value: float) -> str:
        """実際の値からシグナルを生成"""
        signal_rules = {
            'rsi': self._get_rsi_signal,
            'macd': self._get_macd_signal,
            'bollinger_bands': self._get_bollinger_signal,
            'stochastic': self._get_stochastic_signal,
            'atr': self._get_atr_signal,
            'williams_r': self._get_williams_r_signal,
            'cci': self._get_cci_signal,
            'adx': self._get_adx_signal,
            'obv': self._get_obv_signal,
            'vwap': self._get_vwap_signal
        }

        indicator_lower = indicator.lower()
        if indicator_lower in signal_rules:
            return signal_rules[indicator_lower](value)
        
        return 'neutral'

    def calculate_strength_from_value(self, indicator: str, value: float) -> float:
        """実際の値から強度を計算"""
        strength_rules = {
            'rsi': self._get_rsi_strength,
            'macd': self._get_macd_strength,
            'bollinger_bands': self._get_bollinger_strength,
            'stochastic': self._get_stochastic_strength,
            'atr': self._get_atr_strength,
            'williams_r': self._get_williams_r_strength,
            'cci': self._get_cci_strength,
            'adx': self._get_adx_strength,
            'obv': self._get_obv_strength,
            'vwap': self._get_vwap_strength
        }

        indicator_lower = indicator.lower()
        if indicator_lower in strength_rules:
            return strength_rules[indicator_lower](value)
        
        return 0.5

    def _get_rsi_signal(self, value: float) -> str:
        """RSIのシグナル"""
        if value > 70:
            return 'bearish'  # オーバーブought
        elif value < 30:
            return 'bullish'   # オーバーソールド
        else:
            return 'neutral'

    def _get_macd_signal(self, value: float) -> str:
        """MACDのシグナル"""
        if value > 0:
            return 'bullish'
        elif value < 0:
            return 'bearish'
        else:
            return 'neutral'

    def _get_bollinger_signal(self, value: float) -> str:
        """ボリンジャーバンドのシグナル"""
        if value > 1.5:  # 上バンドに近い
            return 'bearish'  # オーバーブought
        elif value < -1.5:  # 下バンドに近い
            return 'bullish'  # オーバーソールド
        else:
            return 'neutral'

    def _get_stochastic_signal(self, value: float) -> str:
        """ストキャスティクスのシグナル"""
        if value > 80:  # オーバーブought
            return 'bearish'
        elif value < 20:  # オーバーソールド
            return 'bullish'
        else:
            return 'neutral'

    def _get_atr_signal(self, value: float) -> str:
        """ATRのシグナル"""
        if value > 0.05:  # 高いボラティリティ
            return 'bearish'
        elif value < 0.01:  # 低いボラティリティ
            return 'bullish'
        else:
            return 'neutral'

    def _get_williams_r_signal(self, value: float) -> str:
        """Williams %Rのシグナル"""
        if value > -20:  # オーバーブought
            return 'bearish'
        elif value < -80:  # オーバーソールド
            return 'bullish'
        else:
            return 'neutral'

    def _get_cci_signal(self, value: float) -> str:
        """CCIのシグナル"""
        if value > 100:  # オーバーブought
            return 'bearish'
        elif value < -100:  # オーバーソールド
            return 'bullish'
        else:
            return 'neutral'

    def _get_adx_signal(self, value: float) -> str:
        """ADXのシグナル"""
        if value > 70:  # 強いトレンド
            return 'bullish'
        elif value < 30:  # 弱いトレンド
            return 'bearish'
        else:
            return 'neutral'

    def _get_obv_signal(self, value: float) -> str:
        """OBVのシグナル"""
        if value > 20:  # 強い買い圧力
            return 'bullish'
        elif value < -20:  # 強い売り圧力
            return 'bearish'
        else:
            return 'neutral'

    def _get_vwap_signal(self, value: float) -> str:
        """VWAPのシグナル"""
        if value > 0.05:  # VWAPより5%以上高い
            return 'bullish'
        elif value < -0.05:  # VWAPより5%以上低い
            return 'bearish'
        else:
            return 'neutral'

    def _get_rsi_strength(self, value: float) -> float:
        """RSIの強度"""
        if value <= 30 or value >= 70:
            return 0.9
        elif value <= 40 or value >= 60:
            return 0.7
        else:
            return 0.5

    def _get_macd_strength(self, value: float) -> float:
        """MACDの強度"""
        abs_value = abs(value)
        if abs_value > 1000:  # BTCの価格範囲を考慮
            return 0.9
        elif abs_value > 500:
            return 0.7
        else:
            return 0.5

    def _get_bollinger_strength(self, value: float) -> float:
        """ボリンジャーバンドの強度"""
        abs_value = abs(value)
        if abs_value > 2.0:
            return 0.9
        elif abs_value > 1.5:
            return 0.7
        else:
            return 0.5

    def _get_stochastic_strength(self, value: float) -> float:
        """ストキャスティクスの強度"""
        if value >= 90 or value <= 10:
            return 0.9
        elif value >= 80 or value <= 20:
            return 0.7
        else:
            return 0.5

    def _get_atr_strength(self, value: float) -> float:
        """ATRの強度"""
        if value >= 0.05:
            return 0.9
        elif value >= 0.03:
            return 0.7
        else:
            return 0.5

    def _get_williams_r_strength(self, value: float) -> float:
        """Williams %Rの強度"""
        if value >= -10 or value <= -90:
            return 0.9
        elif value >= -20 or value <= -80:
            return 0.7
        else:
            return 0.5

    def _get_cci_strength(self, value: float) -> float:
        """CCIの強度"""
        if value >= 200 or value <= -200:
            return 0.9
        elif value >= 100 or value <= -100:
            return 0.7
        else:
            return 0.5

    def _get_adx_strength(self, value: float) -> float:
        """ADXの強度"""
        if value >= 70:
            return 0.9
        elif value >= 50:
            return 0.7
        else:
            return 0.5

    def _get_obv_strength(self, value: float) -> float:
        """OBVの強度"""
        abs_value = abs(value)
        if abs_value >= 50:
            return 0.9
        elif abs_value >= 30:
            return 0.7
        else:
            return 0.5

    def _get_vwap_strength(self, value: float) -> float:
        """VWAPの強度"""
        abs_value = abs(value)
        if abs_value >= 0.1:  # 10%以上の乖離
            return 0.9
        elif abs_value >= 0.05:  # 5%以上の乖離
            return 0.7
        else:
            return 0.5
