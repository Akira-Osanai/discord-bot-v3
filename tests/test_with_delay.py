#!/usr/bin/env python3
"""
レート制限を回避するためのテストスクリプト
"""

import yfinance as yf
import time


def test_with_delay():
    """長い待機時間でテスト"""
    print("🌙✨ レート制限回避テストを開始いたしますわ✨🌙")
    print("=" * 50)
    
    # テストするシンボル（より一般的なもの）
    symbols = [
        "AAPL",   # Apple
        "MSFT",   # Microsoft
        "GOOGL",  # Google
        "BTC-USD",  # Bitcoin
        "ETH-USD"   # Ethereum
    ]
    
    for i, symbol in enumerate(symbols):
        print(f"\n🔍 シンボル '{symbol}' をテスト中... ({i+1}/{len(symbols)})")
        
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
                
                # 基本情報も取得してみる
                try:
                    info = ticker.info
                    if isinstance(info, dict) and info:
                        info_count = len(info)
                        print(f"   基本情報: 利用可能 ({info_count}件)")
                        
                        # 最初の数個のキーを表示
                        print("   主要な情報:")
                        for j, key in enumerate(list(info.keys())[:5]):
                            value = info[key]
                            if isinstance(value, (int, float)):
                                print(f"     {j+1}. {key}: {value:,.2f}")
                            else:
                                print(f"     {j+1}. {key}: {value}")
                    else:
                        print("   基本情報: 利用不可")
                except Exception as e:
                    print(f"   基本情報: エラー - {e}")
                
            else:
                print(f"⚠️ データなし: {symbol}")
                
        except Exception as e:
            print(f"❌ エラー: {symbol} - {e}")
        
        # レート制限を避けるため長めに待機
        if i < len(symbols) - 1:  # 最後のシンボル以外
            print("   ⏳ 次のテストまで5秒待機中...")
            time.sleep(5)
    
    print("\n" + "=" * 50)
    print("🌿✨ テスト完了いたしましたわ✨🌿")


if __name__ == "__main__":
    test_with_delay()
