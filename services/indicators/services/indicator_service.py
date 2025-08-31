"""
テクニカルインジケータ計算サービス
各種テクニカルインジケータの計算を行います
"""

import logging
from typing import List

from src.core.config import IndicatorType
from src.models.schemas import MarketDataPoint

from .indicator_factory import indicator_factory

logger = logging.getLogger(__name__)


class IndicatorService:
    """テクニカルインジケータ計算サービス"""

    def __init__(self):
        self.factory = indicator_factory
        self._excluded_types = ['trend', 'momentum', 'volatility', 'volume']

    async def get_indicators(self) -> List[dict]:
        """利用可能なインジケータ一覧を取得"""
        try:
            indicators = []
            for indicator_type in IndicatorType:
                if indicator_type.value not in self._excluded_types:
                    info = self._create_indicator_info(indicator_type)
                    indicators.append(info)

            count = len(indicators)
            logger.info(f"インジケータ一覧取得完了: {count}件")
            return indicators
        except Exception as e:
            logger.error(f"インジケータ一覧取得エラー: {e}")
            return []

    def _create_indicator_info(self, indicator_type: IndicatorType) -> dict:
        """インジケータ情報を作成"""
        indicator_value = indicator_type.value
        display_name = indicator_value.replace('_', ' ').title()

        return {
            "name": indicator_value,
            "display_name": display_name,
            "type": indicator_value,
            "description": f"{indicator_value} indicator",
            "parameters": {},
            "is_active": True,
            "category": "technical"
        }

    async def get_indicator_info(self, indicator_name: str) -> dict:
        """特定のインジケータ情報を取得"""
        try:
            # インジケータ名を正規化
            normalized_name = indicator_name.lower().replace(' ', '_')

            for indicator_type in IndicatorType:
                if indicator_type.value == normalized_name:
                    return {
                        "name": indicator_name,
                        "type": indicator_type.value,
                        "description": f"{indicator_name} indicator",
                        "parameters": {},
                        "is_active": True,
                        "category": "technical"
                    }

            return None
        except Exception as e:
            logger.error(f"インジケータ情報取得エラー: {e}")
            return None

    async def calculate_indicator(
        self,
        indicator_name: str,
        data: List[MarketDataPoint],
        period: str = "1d",
        interval: str = "1d"
    ) -> dict:
        """特定のインジケータを計算"""
        try:
            logger.info(f"インジケータ計算開始: {indicator_name}")

            # インジケータ名を正規化
            normalized_name = indicator_name.lower().replace(' ', '_')

            # ファクトリーパターンを使用してインジケータを取得
            indicator = self.factory.get_indicator(normalized_name)
            if not indicator:
                raise ValueError(f"インジケータ '{indicator_name}' が見つかりません")

            # インジケータの計算
            result = indicator.calculate(data)

            logger.info(f"インジケータ計算完了: {indicator_name}")
            return result

        except Exception as e:
            logger.error(f"インジケータ計算エラー: {e}")
            raise

    def get_factory_stats(self) -> dict:
        """ファクトリーの統計情報を取得"""
        return {
            "registered_indicators": self.factory.get_registered_count(),
            "cache_size": self.factory.get_cache_size(),
            "excluded_types": len(self._excluded_types),
            "service_status": "active"
        }

    def clear_cache(self):
        """キャッシュをクリア"""
        self.factory.clear_cache()
        logger.info("インジケータキャッシュをクリアしました")


# シングルトンインスタンス
indicator_service = IndicatorService()
logger.info("インジケータサービス初期化完了")
