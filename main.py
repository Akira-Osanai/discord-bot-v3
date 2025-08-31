"""
リファクタリングされたFastAPI アプリケーション
複数通貨ペアとテクニカルインジケータに対応いたします
"""

import logging
import time
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# サービスインポート（パス設定後に実行）
from services import data_service, indicator_service, storage_service
from services.indicators.services.indicator_analysis_service import (
    indicator_analysis_service,
)
from src.core.config import AppConfig
from src.models.schemas import (
    CurrencyPairData,
    HealthCheck,
    HistoricalData,
    IndicatorAnalysis,
    IndicatorInfo,
)

# ログ設定
logging.basicConfig(
    level=getattr(logging, AppConfig.LOG_LEVEL),
    format=AppConfig.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# アプリ起動時刻
start_time = time.time()

app = FastAPI(
    title=AppConfig.API_TITLE,
    description=AppConfig.API_DESCRIPTION,
    version=AppConfig.API_VERSION
)

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ========================================
# HTMLページエンドポイント
# ========================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """ホームページを表示"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """ダッシュボードページを表示"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api-docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    """API仕様ページを表示"""
    return templates.TemplateResponse("api_docs.html", {"request": request})


@app.get("/chart-test", response_class=HTMLResponse)
async def chart_test(request: Request):
    """チャートテストページを表示"""
    return templates.TemplateResponse("chart_test.html", {"request": request})


# ========================================
# システム情報エンドポイント
# ========================================

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """ヘルスチェックエンドポイント"""
    uptime = time.time() - start_time
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=AppConfig.API_VERSION,
        uptime=round(uptime, 2)
    )


@app.get("/debug/config")
async def debug_config():
    """設定値のデバッグ用エンドポイント"""
    return {
        "valid_periods": AppConfig.VALID_PERIODS,
        "valid_intervals": AppConfig.VALID_INTERVALS,
        "valid_currencies": AppConfig.VALID_CURRENCIES,
        "log_level": AppConfig.LOG_LEVEL,
        "log_format": AppConfig.LOG_FORMAT
    }


# ========================================
# 価格データエンドポイント
# ========================================

@app.get("/api/price/{pair}", response_model=CurrencyPairData)
async def get_current_price(
    pair: str,
    period: str = Query("1d", description="期間"),
    interval: str = Query("1m", description="間隔")
):
    """現在価格と基本情報を取得"""
    try:
        # パラメータ検証
        if period not in AppConfig.VALID_PERIODS:
            raise HTTPException(status_code=400, detail=f"無効な期間: {period}")
        if interval not in AppConfig.VALID_INTERVALS:
            raise HTTPException(status_code=400, detail=f"無効な間隔: {interval}")

        data = await data_service.get_current_price(pair)
        if not data:
            raise HTTPException(
                status_code=404, detail=f"通貨ペア '{pair}' のデータが見つかりません")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"価格データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail="価格データの取得に失敗しました")


@app.get("/api/historical/{pair}", response_model=HistoricalData)
async def get_historical_data(
    pair: str,
    period: str = Query("1d", description="期間"),
    interval: str = Query("1m", description="間隔")
):
    """履歴データを取得"""
    try:
        # パラメータ検証
        if period not in AppConfig.VALID_PERIODS:
            raise HTTPException(status_code=400, detail=f"無効な期間: {period}")
        if interval not in AppConfig.VALID_INTERVALS:
            raise HTTPException(status_code=400, detail=f"無効な間隔: {interval}")

        data = await data_service.get_historical_data(pair, period, interval)
        if not data:
            raise HTTPException(
                status_code=404, detail=f"通貨ペア '{pair}' の履歴データが見つかりません")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"履歴データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail="履歴データの取得に失敗しました")


# ========================================
# インジケーターエンドポイント
# ========================================

@app.get("/api/indicators", response_model=List[IndicatorInfo])
async def get_indicators():
    """利用可能なインジケーター一覧を取得"""
    try:
        indicators = await indicator_service.get_indicators()
        return indicators
    except Exception as e:
        logger.error(f"インジケーター一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail="インジケーター一覧の取得に失敗しました")


@app.get("/api/indicators/{indicator}", response_model=IndicatorInfo)
async def get_indicator_info(indicator: str):
    """特定のインジケーター情報を取得"""
    try:
        info = await indicator_service.get_indicator_info(indicator)
        if not info:
            raise HTTPException(
                status_code=404, detail=f"インジケーター '{indicator}' が見つかりません")
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"インジケーター情報取得エラー: {e}")
        raise HTTPException(status_code=500, detail="インジケーター情報の取得に失敗しました")


@app.get("/api/analysis/{pair}/{indicator}", response_model=IndicatorAnalysis)
async def analyze_indicator(
    pair: str,
    indicator: str,
    period: str = Query("1d", description="期間"),
    interval: str = Query("1m", description="間隔")
):
    """インジケーター分析を実行"""
    try:
        # パラメータ検証
        if period not in AppConfig.VALID_PERIODS:
            raise HTTPException(status_code=400, detail=f"無効な期間: {period}")
        if interval not in AppConfig.VALID_INTERVALS:
            raise HTTPException(status_code=400, detail=f"無効な間隔: {interval}")

        analysis = await indicator_analysis_service.analyze(pair, indicator, period, interval)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"分析データが見つかりません")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"インジケーター分析エラー: {e}")
        raise HTTPException(status_code=500, detail="インジケーター分析に失敗しました")


# ========================================
# ストレージエンドポイント
# ========================================

@app.get("/api/storage/status")
async def get_storage_status():
    """ストレージの状態を取得"""
    try:
        status = await storage_service.get_status()
        return status
    except Exception as e:
        logger.error(f"ストレージ状態取得エラー: {e}")
        raise HTTPException(status_code=500, detail="ストレージ状態の取得に失敗しました")


@app.post("/api/storage/cleanup")
async def cleanup_storage():
    """ストレージのクリーンアップを実行"""
    try:
        result = await storage_service.cleanup()
        return {"message": "クリーンアップが完了しました", "details": result}
    except Exception as e:
        logger.error(f"ストレージクリーンアップエラー: {e}")
        raise HTTPException(status_code=500, detail="ストレージクリーンアップに失敗しました")


# ========================================
# エラーハンドリング
# ========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP例外のハンドリング"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """一般的な例外のハンドリング"""
    logger.error(f"予期しないエラー: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部サーバーエラーが発生しました",
            "status_code": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ========================================
# アプリケーション起動
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        log_level=AppConfig.LOG_LEVEL.lower()
    )
