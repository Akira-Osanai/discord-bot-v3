import logging
from datetime import datetime
from typing import Optional

import yfinance as yf
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BTC/USD API",
    description="Yahoo!ファイナンスからBTC/USDのデータを取得するAPI",
    version="1.0.0"
)

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class BTCData(BaseModel):
    symbol: str
    price: float
    currency: str
    timestamp: datetime
    volume: Optional[float] = None
    market_cap: Optional[float] = None


class ErrorResponse(BaseModel):
    error: str
    message: str


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


@app.get("/btc/current", response_model=BTCData)
async def get_current_price():
    """現在のBTC/USD価格を取得"""
    try:
        logger.info("BTC/USDの現在価格を取得中...")

        # Yahoo!ファイナンスからBTC-USDのティッカー情報を取得
        btc_ticker = yf.Ticker("BTC-USD")
        info = btc_ticker.info

        # 現在価格を取得
        current_price = btc_ticker.history(period="1d")
        if current_price.empty:
            raise HTTPException(
                status_code=500,
                detail="価格データの取得に失敗いたしました"
            )

        latest_price = current_price['Close'].iloc[-1]

        btc_data = BTCData(
            symbol="BTC-USD",
            price=round(latest_price, 2),
            currency="USD",
            timestamp=datetime.now(),
            volume=info.get('volume', None),
            market_cap=info.get('marketCap', None)
        )

        logger.info(f"BTC/USD価格取得成功: ${btc_data.price}")
        return btc_data

    except Exception as e:
        logger.error(f"BTC/USD価格取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"データ取得中にエラーが発生いたしました: {str(e)}"
        )


@app.get("/btc/historical")
async def get_historical_data(period: str = "5d", interval: str = "1d"):
    """履歴データを取得（期間と間隔を指定可能）"""
    try:
        logger.info(
            f"BTC/USDの履歴データを取得中... 期間: {period}, 間隔: {interval}"
        )

        # 有効な期間と間隔をチェック
        valid_periods = [
            "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y",
            "ytd", "max"
        ]
        valid_intervals = [
            "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d",
            "5d", "1wk", "1mo", "3mo"
        ]

        if period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail=f"無効な期間です。有効な値: {valid_periods}"
            )

        if interval not in valid_intervals:
            raise HTTPException(
                status_code=400,
                detail=f"無効な間隔です。有効な値: {valid_intervals}"
            )

        btc_ticker = yf.Ticker("BTC-USD")
        history = btc_ticker.history(period=period, interval=interval)

        if history.empty:
            raise HTTPException(
                status_code=500,
                detail="履歴データの取得に失敗いたしました"
            )

        # データを整形
        formatted_data = []
        for index, row in history.iterrows():
            formatted_data.append({
                "timestamp": index.isoformat(),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": row['Volume']
            })

        logger.info(f"履歴データ取得成功: {len(formatted_data)}件")
        return {
            "symbol": "BTC-USD",
            "period": period,
            "interval": interval,
            "data_count": len(formatted_data),
            "data": formatted_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"履歴データ取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"履歴データ取得中にエラーが発生いたしました: {str(e)}"
        )


@app.get("/btc/info")
async def get_btc_info():
    """BTCの基本情報を取得"""
    try:
        logger.info("BTCの基本情報を取得中...")

        btc_ticker = yf.Ticker("BTC-USD")
        info = btc_ticker.info

        # 重要な情報のみを抽出
        btc_info = {
            "symbol": info.get('symbol', 'BTC-USD'),
            "name": info.get('longName', 'Bitcoin'),
            "sector": info.get('sector', 'Cryptocurrency'),
            "industry": info.get('industry', 'Digital Currency'),
            "market_cap": info.get('marketCap'),
            "volume": info.get('volume'),
            "avg_volume": info.get('averageVolume'),
            "pe_ratio": info.get('trailingPE'),
            "price_to_book": info.get('priceToBook'),
            "fifty_two_week_high": info.get('fiftyTwoWeekHigh'),
            "fifty_two_week_low": info.get('fiftyTwoWeekLow'),
            "fifty_day_average": info.get('fiftyDayAverage'),
            "two_hundred_day_average": info.get('twoHundredDayAverage'),
            "currency": info.get('currency', 'USD'),
            "exchange": info.get('exchange', 'CCY'),
            "quote_type": info.get('quoteType', 'CRYPTOCURRENCY')
        }

        logger.info("BTC基本情報取得成功")
        return btc_info

    except Exception as e:
        logger.error(f"BTC基本情報取得エラー: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"基本情報取得中にエラーが発生いたしました: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
