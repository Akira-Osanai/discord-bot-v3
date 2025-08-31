"""
アプリケーション設定ファイル
通貨ペア、インジケータ、API設定などを管理いたします
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import List


class StatusType(str, Enum):
    """ステータスタイプ"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class IndicatorType(str, Enum):
    """インジケータタイプ"""
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER_BANDS = "bollinger_bands"
    ATR = "atr"
    STOCHASTIC = "stochastic"
    WILLIAMS_R = "williams_r"
    CCI = "cci"
    ADX = "adx"
    OBV = "obv"
    PARABOLIC_SAR = "parabolic_sar"
    ICHIMOKU = "ichimoku"
    VWAP = "vwap"
    MONEY_FLOW_INDEX = "money_flow_index"
    RATE_OF_CHANGE = "rate_of_change"
    KELTNER_CHANNEL = "keltner_channel"
    DONCHIAN_CHANNEL = "donchian_channel"
    ETF_FLOW = "etf_flow"

    # 新しく追加するインジケータ
    HASH_RATE = "hash_rate"
    ACTIVE_ADDRESSES = "active_addresses"
    FUNDING_RATE = "funding_rate"
    OPEN_INTEREST = "open_interest"
    FEAR_GREED_INDEX = "fear_greed_index"
    GOOGLE_TRENDS = "google_trends"
    CORRELATION = "correlation"
    BETA = "beta"
    REALIZED_VOLATILITY = "realized_volatility"
    IMPLIED_VOLATILITY = "implied_volatility"

    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"


@dataclass
class IndicatorConfig:
    """インジケータ設定"""
    name: str
    type: IndicatorType
    parameters: dict
    description: str
    is_active: bool = True


class AppConfig:
    """アプリケーション設定"""

    # API設定
    API_TITLE = "Cryptocurrency API"
    API_DESCRIPTION = "暗号通貨の価格データとテクニカルインジケータを提供するAPI"
    API_VERSION = "1.0.0"

    # ログ設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # キャッシュ設定
    CACHE_TTL = 300  # 5分

    # デフォルト設定
    DEFAULT_PERIOD = "5d"
    DEFAULT_INTERVAL = "1d"

    # 有効な期間設定
    VALID_PERIODS = [
        "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    ]

    # 有効な間隔設定
    VALID_INTERVALS = [
        "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
    ]

    # 有効な通貨設定
    VALID_CURRENCIES = [
        "BTC", "ETH", "USDT", "USDC", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE",
        "AVAX", "MATIC", "LINK", "UNI", "ATOM", "LTC", "BCH", "XLM", "ALGO", "VET"
    ]

    # サーバー設定
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

    # データベース設定
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crypto_data.db")

    # 外部API設定
    YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com"
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

    # レート制限設定
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))

    # キャッシュ設定
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # セキュリティ設定
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # ログ設定
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10"))  # MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # メトリクス設定
    METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))

    # ヘルスチェック設定
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # 秒
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))  # 秒

    # データ保持設定
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "365"))
    CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))

    # 通知設定
    NOTIFICATION_ENABLED = os.getenv(
        "NOTIFICATION_ENABLED", "false").lower() == "true"
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    # 開発設定
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD = os.getenv("RELOAD", "false").lower() == "true"

    # テスト設定
    TESTING = os.getenv("TESTING", "false").lower() == "true"
    TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///./test_crypto_data.db")

    # インジケータ設定
    INDICATOR_WEIGHTS = {
        "trend": 0.3,
        "momentum": 0.25,
        "volatility": 0.2,
        "volume": 0.15,
        "custom": 0.1
    }

    @classmethod
    def get_database_url(cls) -> str:
        """データベースURLを取得"""
        if cls.TESTING:
            return cls.TEST_DATABASE_URL
        return cls.DATABASE_URL

    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうかを判定"""
        return not cls.DEBUG and not cls.TESTING

    @classmethod
    def get_log_level(cls) -> str:
        """ログレベルを取得"""
        if cls.DEBUG:
            return "DEBUG"
        return cls.LOG_LEVEL

    @classmethod
    def get_cache_ttl(cls) -> int:
        """キャッシュTTLを取得"""
        if cls.DEBUG:
            return 60  # デバッグ時は1分
        return cls.CACHE_TTL

    @classmethod
    def get_rate_limit(cls) -> dict:
        """レート制限設定を取得"""
        return {
            "per_minute": cls.RATE_LIMIT_PER_MINUTE,
            "per_hour": cls.RATE_LIMIT_PER_HOUR
        }

    @classmethod
    def get_notification_config(cls) -> dict:
        """通知設定を取得"""
        return {
            "enabled": cls.NOTIFICATION_ENABLED,
            "slack_webhook": cls.SLACK_WEBHOOK_URL,
            "email": {
                "smtp_server": cls.EMAIL_SMTP_SERVER,
                "smtp_port": cls.EMAIL_SMTP_PORT,
                "username": cls.EMAIL_USERNAME,
                "password": cls.EMAIL_PASSWORD
            }
        }

    @classmethod
    def validate_config(cls) -> bool:
        """設定の妥当性を検証"""
        try:
            # 必須設定の検証
            if not cls.SECRET_KEY or cls.SECRET_KEY == "your-secret-key-here":
                return False

            # ポート番号の検証
            if not (1 <= cls.PORT <= 65535):
                return False

            # ログレベルの検証
            valid_log_levels = ["DEBUG", "INFO",
                                "WARNING", "ERROR", "CRITICAL"]
            if cls.LOG_LEVEL not in valid_log_levels:
                return False

            return True
        except Exception:
            return False

    @classmethod
    def get_config_summary(cls) -> dict:
        """設定の概要を取得"""
        return {
            "api": {
                "title": cls.API_TITLE,
                "version": cls.API_VERSION,
                "host": cls.HOST,
                "port": cls.PORT
            },
            "database": {
                "url": cls.get_database_url(),
                "testing": cls.TESTING
            },
            "cache": {
                "enabled": cls.CACHE_ENABLED,
                "ttl": cls.get_cache_ttl(),
                "redis_url": cls.REDIS_URL
            },
            "logging": {
                "level": cls.get_log_level(),
                "file": cls.LOG_FILE,
                "max_size": cls.LOG_MAX_SIZE
            },
            "security": {
                "secret_key_set": bool(cls.SECRET_KEY and cls.SECRET_KEY != "your-secret-key-here"),
                "access_token_expire_minutes": cls.ACCESS_TOKEN_EXPIRE_MINUTES
            },
            "environment": {
                "debug": cls.DEBUG,
                "production": cls.is_production(),
                "reload": cls.RELOAD
            }
        }
