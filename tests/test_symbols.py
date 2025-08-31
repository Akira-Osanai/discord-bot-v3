#!/usr/bin/env python3
"""
異なる暗号通貨シンボルをテストするスクリプト
"""

import yfinance as yf
import time


def test_crypto_symbols():
    """異なる暗号通貨シンボルをテスト"""
    print("🌙✨ 暗号通貨シンボルテストを開始いたしますわ✨🌙")
    print("=" * 50)
    
    # テストするシンボル
    symbols = [
        "BTC-USD",
        "BTCUSD=X",
        "BTC=X",
        "BTCUSD",
        "ETH-USD",
        "ETHUSD=X",
        "ETH=X",
        "ETHUSD"
    ]
    
    for symbol in symbols:
        print(f"\n🔍 シンボル '{symbol}' をテスト中...")
        
        try:
            # ティッカーを作成
            ticker = yf.Ticker(symbol)
            
            # 履歴データを取得（短い期間で）
            history = ticker.history(period="1d", interval="1h")
            
            if not history.empty:
                print(f"✅ 成功: {symbol}")
                print(f"   データ件数: {len(history)}")
                latest = history.iloc[-1]
                print(f"   最新価格: ${latest.get('Close', 'N/A'):,.2f}")
                print(f"   出来高: {latest.get('Volume', 'N/A'):,.0f}")
                
                # このシンボルで基本情報も取得してみる
                try:
                    info = ticker.info
                    if isinstance(info, dict) and info:
                        info_count = len(info)
                        print(f"   基本情報: 利用可能 ({info_count}件)")
                    else:
                        print("   基本情報: 利用不可")
                except Exception as e:
                    print(f"   基本情報: エラー - {e}")
                
                break  # 成功したらループを抜ける
                
            else:
                print(f"⚠️ データなし: {symbol}")
                
        except Exception as e:
            print(f"❌ エラー: {symbol} - {e}")
        
        # レート制限を避けるため少し待機
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🌿✨ テスト完了いたしましたわ✨🌿")


if __name__ == "__main__":
    test_crypto_symbols()
