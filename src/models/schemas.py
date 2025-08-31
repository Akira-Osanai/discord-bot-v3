"""
データモデル定義
API レスポンス、データベースモデル等を定義いたします
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, field_serializer


class StatusType(Enum):
    """ステータスの種類"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class MarketDataPoint(BaseModel):
    """市場データのポイント"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def price(self) -> float:
        """価格（終値）を取得"""
        return self.close

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class CurrencyPairData(BaseModel):
    """通貨ペアデータ"""
    symbol: str
    price: float
    currency: str
    timestamp: datetime
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    change_24h: Optional[float] = None
    change_24h_percent: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def close(self) -> float:
        """終値（価格）を取得"""
        return self.price

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class HistoricalData(BaseModel):
    """履歴データ"""
    symbol: str
    period: str
    interval: str
    data_count: int
    data: List[MarketDataPoint]
    indicators: Optional[Dict[str, Any]] = None


class IndicatorValue(BaseModel):
    """インジケータの値"""
    name: str
    type: str
    timestamp: datetime
    value: float
    parameters: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class MultiIndicatorData(BaseModel):
    """複数のインジケータデータ"""
    timestamp: datetime
    values: Dict[str, float]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class IndicatorInfo(BaseModel):
    """インジケータ情報"""
    name: str
    type: str
    description: str
    parameters: Dict[str, Any]
    is_active: bool = True
    category: str = "technical"
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('last_updated')
    def serialize_last_updated(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.isoformat()
        return None


class IndicatorAnalysis(BaseModel):
    """インジケータ分析結果"""
    symbol: str
    indicator: str
    period: str
    interval: str
    timestamp: datetime
    value: float
    signal: str
    strength: float
    parameters: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class HealthCheck(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    services: Optional[Dict[str, str]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    error: str
    status_code: int
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class BasicInfo(BaseModel):
    """基本情報"""
    name: str
    description: str
    version: str
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_created_at(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.isoformat()
        return None

    @field_serializer('updated_at')
    def serialize_updated_at(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.isoformat()
        return None


class DataPoint(BaseModel):
    """データポイント"""
    timestamp: datetime
    value: float
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class TimeSeriesData(BaseModel):
    """時系列データ"""
    symbol: str
    period: str
    interval: str
    data: List[DataPoint]
    summary: Optional[Dict[str, float]] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisResult(BaseModel):
    """分析結果"""
    symbol: str
    analysis_type: str
    timestamp: datetime
    result: Dict[str, Any]
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class CacheInfo(BaseModel):
    """キャッシュ情報"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    ttl: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()

    @field_serializer('expires_at')
    def serialize_expires_at(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.isoformat()
        return None


class StorageStatus(BaseModel):
    """ストレージ状態"""
    total_size: int
    used_size: int
    free_size: int
    file_count: int
    last_cleanup: Optional[datetime] = None
    status: str = "healthy"

    model_config = ConfigDict(from_attributes=True)

    @property
    def usage_percent(self) -> float:
        """使用率を計算"""
        if self.total_size == 0:
            return 0.0
        return (self.used_size / self.total_size) * 100

    @field_serializer('last_cleanup')
    def serialize_last_cleanup(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.isoformat()
        return None
