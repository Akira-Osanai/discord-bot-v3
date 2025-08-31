"""
インジケータ分析サービス
分割されたクラスを使用して分析処理を行います
"""

import logging
from datetime import datetime
from typing import Dict, List

import pytz

from src.core.config import AppConfig, IndicatorType
from src.models.schemas import MultiIndicatorData

from .indicator_aggregator import IndicatorAggregator
from .indicator_analyzer import IndicatorAnalyzer
from .indicator_factory import indicator_factory
from .indicator_signal_generator import IndicatorSignalGenerator
from .indicator_summary_generator import IndicatorSummaryGenerator

logger = logging.getLogger(__name__)


class IndicatorAnalysisService:
    """インジケータ分析サービス"""

    def __init__(self):
        self.weights = AppConfig.INDICATOR_WEIGHTS
        self.aggregator = IndicatorAggregator()
        self.analyzer = IndicatorAnalyzer()
        self.signal_generator = IndicatorSignalGenerator()
        self.summary_generator = IndicatorSummaryGenerator()

    def analyze_indicators(
        self,
        indicators_data: List[MultiIndicatorData],
        current_price: float
    ) -> Dict:
        """インジケータを分析して売買判断とサマリーを生成"""
        logger.info(f"インジケータ分析開始: {len(indicators_data)}件のデータ")

        if not indicators_data:
            logger.warning("インジケータデータが空です")
            return {}

        # 各インジケータの最新値を集約
        aggregated_latest = self.aggregator.aggregate_latest_values(
            indicators_data)
        if len(indicators_data) > 1:
            aggregated_previous = self.aggregator.aggregate_previous_values(
                indicators_data)
        else:
            aggregated_previous = None

        logger.info(
            f"集約された最新データのインジケータ: {list(aggregated_latest.values.keys())}")
        if aggregated_previous:
            prev_indicators = list(aggregated_previous.values.keys())
            logger.info(f"集約された前回データのインジケータ: {prev_indicators}")

        # 新しいインジケータタイプの分析を先に実行
        logger.info("新しいインジケータ分析開始")
        indicator_states = {}
        self.analyzer.analyze_new_indicator_types(
            indicator_states, aggregated_latest,
            aggregated_previous, current_price)
        logger.info(f"新しいインジケータ分析完了: {list(indicator_states.keys())}")

        # 既存のインジケータの状態を分析（重複を避ける）
        existing_states = self.analyzer.analyze_indicator_states(
            aggregated_latest, aggregated_previous, current_price
        )

        # 既存のインジケータを追加（重複しない場合のみ）
        for name, state in existing_states.items():
            if name not in indicator_states:
                indicator_states[name] = state

        logger.info(f"最終的なインジケータ数: {len(indicator_states)}")
        logger.info(f"最終的なインジケータ: {list(indicator_states.keys())}")

        logger.info(f"分析されたインジケータ: {list(indicator_states.keys())}")

        # 重み付けによる売買スコア計算
        buy_score, sell_score = self.signal_generator.calculate_trading_scores(
            indicator_states)

        logger.info(f"売買スコア: 買い={buy_score}, 売り={sell_score}")

        # サマリー生成
        summary = self.summary_generator.generate_summary(
            indicator_states, buy_score, sell_score)

        return {
            "summary": summary,
            "indicator_states": indicator_states,
            "trading_scores": {
                "buy_score": buy_score,
                "sell_score": sell_score,
                "recommendation": self.summary_generator.get_recommendation(
                    buy_score, sell_score)
            },
            "timestamp": datetime.now(pytz.UTC)
        }

    async def analyze(
            self, pair: str, indicator: str,
            period: str = "1d", interval: str = "1d"):
        """特定のインジケータの分析を実行"""
        try:
            logger.info(
                f"インジケータ分析開始: {pair} - {indicator} ({period}, {interval})")

            # 実際のインジケータ分析を実行
            logger.info(f"インジケータ分析実行中: {indicator}")

            # 実際のデータを使って計算を試行
            actual_value = await self._calculate_actual_value(
                pair, indicator, period, interval)

            if actual_value is not None:
                # 実際の値が計算できた場合
                analysis_result = {
                    "symbol": pair,
                    "indicator": indicator,
                    "period": period,
                    "interval": interval,
                    "value": actual_value,
                    "signal": self._generate_signal_from_value(
                        indicator, actual_value),
                    "strength": self._calculate_strength_from_value(
                        indicator, actual_value),
                    "parameters": {},
                    "timestamp": datetime.now(pytz.UTC),
                    "metadata": {
                        "note": "実際のデータから計算された値です"
                    }
                }
            else:
                # 実際の値が計算できない場合、エラーを返す
                raise ValueError(
                    f"インジケータ '{indicator}' の計算に失敗しました。実装されていないか、データが不足しています。")

            logger.info(
                f"インジケータ分析完了: {indicator} - シグナル: {analysis_result['signal']}")
            return analysis_result

        except Exception as e:
            logger.error(f"インジケータ分析エラー: {e}")
            import traceback
            logger.error(f"詳細エラー: {traceback.format_exc()}")
            return None

    def _generate_test_value(self, indicator: str) -> float:
        """テスト用のインジケータ値を生成"""
        import hashlib
        import random

        # インジケータ名から一貫した値を生成
        hash_obj = hashlib.md5(indicator.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        random.seed(seed)

        # インジケータの種類に応じて適切な範囲の値を生成
        if 'rsi' in indicator.lower():
            return random.uniform(30, 70)  # RSIは0-100の範囲
        elif 'macd' in indicator.lower():
            return random.uniform(-2, 2)   # MACDは通常-2から2の範囲
        elif 'bollinger' in indicator.lower():
            return random.uniform(0.8, 1.2)  # ボリンジャーバンドの位置
        elif 'stochastic' in indicator.lower():
            return random.uniform(20, 80)  # ストキャスティクスは0-100の範囲
        elif 'volume' in indicator.lower():
            return random.uniform(1000000, 10000000)  # ボリューム
        elif 'sma' in indicator.lower() or 'ema' in indicator.lower():
            # SMA/EMAは価格ベースのインジケータなので、BTCの価格範囲に合わせる
            return random.uniform(105000, 115000)  # BTC-USDの1ヶ月間の価格範囲
        else:
            return random.uniform(0.1, 100.0)  # その他のインジケータ

    def _generate_test_signal(self, indicator: str) -> str:
        """テスト用のシグナルを生成"""
        import hashlib
        import random

        # インジケータ名から一貫したシグナルを生成
        hash_obj = hashlib.md5(indicator.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        random.seed(seed)

        signals = ['bullish', 'bearish', 'neutral']
        weights = [0.4, 0.3, 0.3]  # 強気、弱気、中立の重み
        return random.choices(signals, weights=weights)[0]

    def _generate_test_strength(self, indicator: str) -> float:
        """テスト用の強度を生成"""
        import hashlib
        import random

        # インジケータ名から一貫した強度を生成
        hash_obj = hashlib.md5(indicator.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        random.seed(seed)

        return random.uniform(0.1, 0.9)

    async def _calculate_actual_value(
            self, pair: str, indicator: str,
            period: str, interval: str) -> float:
        """実際のデータを使ってインジケータ値を計算"""
        try:
            # 履歴データを取得
            from services.data.data_service import data_service
            historical_data = await data_service.get_historical_data(
                pair, period, interval)

            if not historical_data or not historical_data.data:
                logger.warning(f"履歴データが取得できませんでした: {pair}")
                return None

            # インジケータ名をIndicatorTypeにマッピング
            indicator_mapping = {
                'sma': IndicatorType.SMA,
                'ema': IndicatorType.EMA,
                'rsi': IndicatorType.RSI,
                'macd': IndicatorType.MACD,
                'bollinger_bands': IndicatorType.BOLLINGER_BANDS,
                'stochastic': IndicatorType.STOCHASTIC,
                'atr': IndicatorType.ATR,
                'williams_r': IndicatorType.WILLIAMS_R,
                'cci': IndicatorType.CCI,
                'adx': IndicatorType.ADX,
                'obv': IndicatorType.OBV,
                'vwap': IndicatorType.VWAP,
                'parabolic_sar': IndicatorType.PARABOLIC_SAR,
                'ichimoku': IndicatorType.ICHIMOKU,
                'money_flow_index': IndicatorType.MONEY_FLOW_INDEX,
                'rate_of_change': IndicatorType.RATE_OF_CHANGE,
                'keltner_channel': IndicatorType.KELTNER_CHANNEL,
                'donchian_channel': IndicatorType.DONCHIAN_CHANNEL,
                'etf_flow': IndicatorType.ETF_FLOW,
                'hash_rate': IndicatorType.HASH_RATE,
                'active_addresses': IndicatorType.ACTIVE_ADDRESSES,
                'funding_rate': IndicatorType.FUNDING_RATE,
                'open_interest': IndicatorType.OPEN_INTEREST,
                'fear_greed_index': IndicatorType.FEAR_GREED_INDEX,
                'google_trends': IndicatorType.GOOGLE_TRENDS,
                'correlation': IndicatorType.CORRELATION,
                'beta': IndicatorType.BETA,
                'realized_volatility': IndicatorType.REALIZED_VOLATILITY,
                'implied_volatility': IndicatorType.IMPLIED_VOLATILITY
            }

            indicator_type = indicator_mapping.get(indicator.lower())
            if not indicator_type:
                logger.warning(f"未対応のインジケータ: {indicator}")
                return None

            # インジケータファクトリーからインジケータを取得
            try:
                indicator_instance = indicator_factory.get_indicator(
                    indicator_type)
            except ValueError as e:
                logger.warning(f"インジケータファクトリーエラー: {e}")
                return None

            # インジケータを計算
            try:
                # デフォルトのパラメータを設定
                params = {}
                if indicator.lower() in ['sma', 'ema']:
                    params['period'] = 20
                elif indicator.lower() == 'rsi':
                    params['period'] = 14
                elif indicator.lower() == 'macd':
                    params['fast'] = 12
                    params['slow'] = 26
                    params['signal'] = 9
                elif indicator.lower() == 'bollinger_bands':
                    params['period'] = 20
                    params['std_dev'] = 2.0
                elif indicator.lower() == 'stochastic':
                    params['k_period'] = 14
                    params['d_period'] = 3
                elif indicator.lower() == 'atr':
                    params['period'] = 14
                elif indicator.lower() == 'williams_r':
                    params['period'] = 14
                elif indicator.lower() == 'cci':
                    params['period'] = 14
                elif indicator.lower() == 'adx':
                    params['period'] = 14
                elif indicator.lower() == 'obv':
                    params = {}
                elif indicator.lower() == 'vwap':
                    params = {}
                elif indicator.lower() == 'parabolic_sar':
                    params['acceleration'] = 0.02
                    params['maximum'] = 0.2
                elif indicator.lower() == 'ichimoku':
                    params['tenkan_period'] = 9
                    params['kijun_period'] = 26
                    params['senkou_span_b_period'] = 52
                elif indicator.lower() == 'money_flow_index':
                    params['period'] = 14
                elif indicator.lower() == 'rate_of_change':
                    params['period'] = 14
                elif indicator.lower() == 'keltner_channel':
                    params['period'] = 20
                    params['multiplier'] = 2.0
                elif indicator.lower() == 'donchian_channel':
                    params['period'] = 20
                elif indicator.lower() == 'etf_flow':
                    params = {}
                elif indicator.lower() == 'hash_rate':
                    params = {}
                elif indicator.lower() == 'active_addresses':
                    params = {}
                elif indicator.lower() == 'funding_rate':
                    params = {}
                elif indicator.lower() == 'open_interest':
                    params['period'] = 20
                elif indicator.lower() == 'fear_greed_index':
                    params = {}
                elif indicator.lower() == 'google_trends':
                    params['period'] = 20
                    params['search_terms'] = ['BTC', 'Bitcoin']
                elif indicator.lower() == 'correlation':
                    params = {}
                elif indicator.lower() == 'beta':
                    params['period'] = 20
                elif indicator.lower() == 'realized_volatility':
                    params['period'] = 20
                elif indicator.lower() == 'implied_volatility':
                    params['period'] = 20

                # インジケータを計算
                results = indicator_instance.calculate(
                    historical_data.data, **params)

                if results and len(results) > 0:
                    # 最新の値を返す
                    return results[-1].value
                else:
                    logger.warning(f"インジケータ計算結果が空: {indicator}")
                    return None

            except Exception as e:
                logger.error(f"インジケータ計算エラー: {indicator} - {e}")
                return None

        except Exception as e:
            logger.error(f"実際の値計算エラー: {e}")
            return None

    def _generate_signal_from_value(self, indicator: str, value: float) -> str:
        """実際の値からシグナルを生成"""
        if indicator.lower() == 'rsi':
            if value > 70:
                return 'bearish'  # オーバーブought
            elif value < 30:
                return 'bullish'   # オーバーソールド
            else:
                return 'neutral'
        elif indicator.lower() in ['sma', 'ema']:
            # 価格ベースのインジケータは現在価格と比較
            # ここでは簡易的に中立を返す
            return 'neutral'
        elif indicator.lower() == 'macd':
            # MACDのシグナル（正の値で強気、負の値で弱気）
            if value > 0:
                return 'bullish'
            elif value < 0:
                return 'bearish'
            else:
                return 'neutral'
        elif indicator.lower() == 'bollinger_bands':
            # ボリンジャーバンドのシグナル
            if value > 1.5:  # 上バンドに近い
                return 'bearish'  # オーバーブought
            elif value < -1.5:  # 下バンドに近い
                return 'bullish'  # オーバーソールド
            else:
                return 'neutral'
        elif indicator.lower() == 'stochastic':
            # ストキャスティクスのシグナル
            if value > 80:  # オーバーブought
                return 'bearish'
            elif value < 20:  # オーバーソールド
                return 'bullish'
            else:
                return 'neutral'
        elif indicator.lower() == 'atr':
            # ATRのシグナル（ボラティリティの高さ）
            if value > 0.05:  # 高いボラティリティ
                return 'bearish'
            elif value < 0.01:  # 低いボラティリティ
                return 'bullish'
            else:
                return 'neutral'
        elif indicator.lower() == 'williams_r':
            # Williams %Rのシグナル
            if value > -20:  # オーバーブought
                return 'bearish'
            elif value < -80:  # オーバーソールド
                return 'bullish'
            else:
                return 'neutral'
        elif indicator.lower() == 'cci':
            # CCIのシグナル
            if value > 100:  # オーバーブought
                return 'bearish'
            elif value < -100:  # オーバーソールド
                return 'bullish'
            else:
                return 'neutral'
        elif indicator.lower() == 'adx':
            # ADXのシグナル（トレンドの強度）
            if value > 70:  # 強いトレンド
                return 'bullish'
            elif value < 30:  # 弱いトレンド
                return 'bearish'
            else:
                return 'neutral'
        elif indicator.lower() == 'obv':
            # OBVのシグナル（出来高の方向性）
            if value > 20:  # 強い買い圧力
                return 'bullish'
            elif value < -20:  # 強い売り圧力
                return 'bearish'
            else:
                return 'neutral'
        elif indicator.lower() == 'vwap':
            # VWAPのシグナル（価格の位置）
            if value > 0.05:  # VWAPより5%以上高い
                return 'bullish'
            elif value < -0.05:  # VWAPより5%以上低い
                return 'bearish'
            else:
                return 'neutral'
        else:
            return 'neutral'

    def _calculate_strength_from_value(
            self, indicator: str, value: float) -> float:
        """実際の値から強度を計算"""
        if indicator.lower() == 'rsi':
            # RSIの強度（30-70の範囲で0.5、極端な値で1.0に近づく）
            if value <= 30 or value >= 70:
                return 0.9
            elif value <= 40 or value >= 60:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'macd':
            # MACDの強度（絶対値が大きいほど強い）
            abs_value = abs(value)
            if abs_value > 1000:  # BTCの価格範囲を考慮
                return 0.9
            elif abs_value > 500:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'bollinger bands':
            # ボリンジャーバンドの強度（極端な位置ほど強い）
            abs_value = abs(value)
            if abs_value > 2.0:
                return 0.9
            elif abs_value > 1.5:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'stochastic':
            # ストキャスティクスの強度（極端な値ほど強い）
            if value >= 90 or value <= 10:
                return 0.9
            elif value >= 80 or value <= 20:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'atr':
            # ATRの強度（ボラティリティの高さ）
            if value >= 0.05:
                return 0.9
            elif value >= 0.03:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'williams_r':
            # Williams %Rの強度
            if value >= -10 or value <= -90:
                return 0.9
            elif value >= -20 or value <= -80:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'cci':
            # CCIの強度
            if value >= 200 or value <= -200:
                return 0.9
            elif value >= 100 or value <= -100:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'adx':
            # ADXの強度（トレンドの強さ）
            if value >= 70:
                return 0.9
            elif value >= 50:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'obv':
            # OBVの強度（出来高の方向性の強さ）
            abs_value = abs(value)
            if abs_value >= 50:
                return 0.9
            elif abs_value >= 30:
                return 0.7
            else:
                return 0.5
        elif indicator.lower() == 'vwap':
            # VWAPの強度（価格の乖離度）
            abs_value = abs(value)
            if abs_value >= 0.1:  # 10%以上の乖離
                return 0.9
            elif abs_value >= 0.05:  # 5%以上の乖離
                return 0.7
            else:
                return 0.5
        else:
            return 0.5


# シングルトンインスタンス
indicator_analysis_service = IndicatorAnalysisService()
logger.info("インジケータ分析サービス初期化完了")
