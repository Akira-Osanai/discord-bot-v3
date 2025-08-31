"""
相関係数インジケータ
S&P500などのベンチマークとの相関係数を計算します
"""

import logging
from typing import List

import pandas as pd
import yfinance as yf

from src.core.config import IndicatorType
from src.models.schemas import IndicatorValue, MarketDataPoint

from .base_indicator import BaseIndicator

logger = logging.getLogger(__name__)


class CorrelationIndicator(BaseIndicator):
    """相関係数インジケータ"""

    def __init__(self):
        super().__init__(IndicatorType.CORRELATION)
        self.name = "Correlation"

    def calculate(
        self,
        data: List[MarketDataPoint],
        period: int = 30,
        benchmark: str = "SPY"
    ) -> List[IndicatorValue]:
        """相関係数を計算"""
        if len(data) < period:
            return []

        try:
            # ベンチマークデータを取得
            benchmark_data = self._get_benchmark_data(benchmark, period)

            if benchmark_data is None or len(benchmark_data) < period:
                return []

            # 価格データをDataFrameに変換
            df = self._to_dataframe(data)

            # ベンチマークデータをマージ
            if 'close' in benchmark_data.columns:
                df['benchmark'] = benchmark_data['close'].values[:len(df)]
            else:
                # yfinanceの列名が異なる場合
                df['benchmark'] = benchmark_data['Close'].values[:len(df)]

            # 相関係数を計算
            correlation = df['price'].rolling(
                window=period).corr(df['benchmark'])

            results = []

            for timestamp, value in zip(df['timestamp'], correlation):
                if not pd.isna(value):
                    results.append(self._create_indicator_value(
                        timestamp=timestamp,
                        value=round(value, 4),
                        name=f"Correlation vs {benchmark}",
                        parameters={"period": period, "benchmark": benchmark}
                    ))

            logger.info(f"相関係数計算完了: {len(results)}件")
            return results

        except Exception as e:
            logger.error(f"相関係数計算エラー: {str(e)}")
            return []

    def _get_benchmark_data(self, symbol: str, period: int) -> pd.DataFrame:
        """ベンチマークデータを取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{period + 10}d")

            if data.empty:
                return None

            return data

        except Exception as e:
            logger.error(f"ベンチマークデータ取得エラー: {str(e)}")
            return None

    def _estimate_from_price_patterns(self, data: List[MarketDataPoint], period: int) -> List[IndicatorValue]:
        """価格パターンから相関係数を推定（フォールバック）"""
        df = self._to_dataframe(data)

        if len(df) < period:
            return []

        # 価格の変化率の自己相関を計算
        price_returns = df['price'].pct_change()

        # 単純な推定値（実際の相関とは異なる）
        estimated_correlation = 0.5 + \
            (price_returns.rolling(window=period).mean() * 10)
        estimated_correlation = estimated_correlation.clip(-1, 1)

        results = []

        for timestamp, value in zip(df['timestamp'], estimated_correlation):
            if not pd.isna(value):
                results.append(self._create_indicator_value(
                    timestamp=timestamp,
                    value=round(value, 4),
                    name="Estimated Correlation",
                    parameters={"period": period,
                                "method": "price_pattern_based"}
                ))

        return results
