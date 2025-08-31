"""
インジケータファクトリー
各インジケータのインスタンスを作成・管理します
"""

import logging
from typing import Dict

from src.core.config import IndicatorType

from ..core.active_addresses_indicator import ActiveAddressesIndicator
from ..core.adx_indicator import ADXIndicator
from ..core.atr_indicator import ATRIndicator
from ..core.base_indicator import BaseIndicator
from ..core.beta_indicator import BetaIndicator
from ..core.bollinger_bands_indicator import BollingerBandsIndicator
from ..core.cci_indicator import CCIIndicator
from ..core.correlation_indicator import CorrelationIndicator
from ..core.donchian_channel_indicator import DonchianChannelIndicator
from ..core.ema_indicator import EMAIndicator
from ..core.etf_flow_indicator import ETFFlowIndicator
from ..core.fear_greed_indicator import FearGreedIndicator
from ..core.funding_rate_indicator import FundingRateIndicator
from ..core.google_trends_indicator import GoogleTrendsIndicator

# 新しく追加するインジケータ
from ..core.hash_rate_indicator import HashRateIndicator
from ..core.ichimoku_indicator import IchimokuIndicator
from ..core.implied_volatility_indicator import ImpliedVolatilityIndicator
from ..core.keltner_channel_indicator import KeltnerChannelIndicator
from ..core.macd_indicator import MACDIndicator
from ..core.money_flow_index_indicator import MoneyFlowIndexIndicator
from ..core.obv_indicator import OBVIndicator
from ..core.open_interest_indicator import OpenInterestIndicator
from ..core.parabolic_sar_indicator import ParabolicSARIndicator
from ..core.rate_of_change_indicator import RateOfChangeIndicator
from ..core.realized_volatility_indicator import RealizedVolatilityIndicator
from ..core.rsi_indicator import RSIIndicator
from ..core.sma_indicator import SMAIndicator
from ..core.stochastic_indicator import StochasticIndicator
from ..core.vwap_indicator import VWAPIndicator
from ..core.williams_r_indicator import WilliamsRIndicator


class IndicatorFactory:
    """インジケータファクトリークラス"""

    def __init__(self):
        self._indicators: Dict[IndicatorType, BaseIndicator] = {}
        self._cache = {}  # 計算結果のキャッシュ
        self._register_indicators()

    def _register_indicators(self):
        """インジケータを登録"""
        # インジケータマッピングテーブル
        indicator_mappings = {
            # 基本インジケータ
            IndicatorType.SMA: SMAIndicator,
            IndicatorType.EMA: EMAIndicator,
            IndicatorType.RSI: RSIIndicator,
            IndicatorType.MACD: MACDIndicator,
            IndicatorType.BOLLINGER_BANDS: BollingerBandsIndicator,
            IndicatorType.STOCHASTIC: StochasticIndicator,
            IndicatorType.ATR: ATRIndicator,
            IndicatorType.WILLIAMS_R: WilliamsRIndicator,
            IndicatorType.CCI: CCIIndicator,
            IndicatorType.ADX: ADXIndicator,
            IndicatorType.OBV: OBVIndicator,
            IndicatorType.PARABOLIC_SAR: ParabolicSARIndicator,
            IndicatorType.ICHIMOKU: IchimokuIndicator,
            IndicatorType.VWAP: VWAPIndicator,

            # 高度なインジケータ
            IndicatorType.MONEY_FLOW_INDEX: MoneyFlowIndexIndicator,
            IndicatorType.RATE_OF_CHANGE: RateOfChangeIndicator,
            IndicatorType.KELTNER_CHANNEL: KeltnerChannelIndicator,
            IndicatorType.DONCHIAN_CHANNEL: DonchianChannelIndicator,
            IndicatorType.ETF_FLOW: ETFFlowIndicator,

            # 市場データ系
            IndicatorType.HASH_RATE: HashRateIndicator,
            IndicatorType.ACTIVE_ADDRESSES: ActiveAddressesIndicator,
            IndicatorType.FUNDING_RATE: FundingRateIndicator,
            IndicatorType.FEAR_GREED_INDEX: FearGreedIndicator,
            IndicatorType.CORRELATION: CorrelationIndicator,
            IndicatorType.REALIZED_VOLATILITY: RealizedVolatilityIndicator,
            IndicatorType.IMPLIED_VOLATILITY: ImpliedVolatilityIndicator,
            IndicatorType.BETA: BetaIndicator,
            IndicatorType.GOOGLE_TRENDS: GoogleTrendsIndicator,
            IndicatorType.OPEN_INTEREST: OpenInterestIndicator,
        }

        # インスタンス化して登録
        for indicator_type, indicator_class in indicator_mappings.items():
            self._indicators[indicator_type] = indicator_class()

    def get_indicator(self, indicator_type: IndicatorType) -> BaseIndicator:
        """指定されたタイプのインジケータを取得"""
        if indicator_type not in self._indicators:
            raise ValueError(f"未対応のインジケータタイプ: {indicator_type}")

        return self._indicators[indicator_type]

    def get_all_indicators(self) -> Dict[IndicatorType, BaseIndicator]:
        """全てのインジケータを取得"""
        return self._indicators.copy()

    def is_supported(self, indicator_type: IndicatorType) -> bool:
        """指定されたインジケータタイプがサポートされているかチェック"""
        return indicator_type in self._indicators

    def clear_cache(self):
        """キャッシュをクリア"""
        self._cache.clear()

    def get_cache_size(self) -> int:
        """キャッシュサイズを取得"""
        return len(self._cache)

    def get_registered_count(self) -> int:
        """登録されたインジケータ数を取得"""
        return len(self._indicators)


# シングルトンインスタンス
indicator_factory = IndicatorFactory()
logger = logging.getLogger(__name__)
logger.info("インジケータファクトリー初期化完了")
logger.info(f"登録されたインジケータ: {list(indicator_factory._indicators.keys())}")
