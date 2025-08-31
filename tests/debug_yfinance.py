#!/usr/bin/env python3
"""
yfinanceの動作をデバッグするスクリプト
"""

import yfinance as yf


def debug_yfinance():
    """yfinanceの動作をデバッグ"""
    print("🌙✨ yfinance デバッグを開始いたしますわ✨🌙")
    print("=" * 50)
    
    try:
        print("1. BTC-USDティッカーの作成...")
        btc_ticker = yf.Ticker("BTC-USD")
        print("✅ ティッカー作成成功")
        
        print("\n2. 基本情報の取得...")
        try:
            info = btc_ticker.info
            print("✅ 基本情報取得成功")
            print(f"   情報の型: {type(info)}")
            length_info = len(info) if hasattr(info, '__len__') else 'N/A'
            print(f"   情報の長さ: {length_info}")
            
            # 最初の数個のキーを表示
            if isinstance(info, dict):
                print("   主要なキー:")
                for i, key in enumerate(list(info.keys())[:10]):
                    print(f"     {i+1}. {key}: {info[key]}")
            else:
                print(f"   情報の内容: {info}")
                
        except Exception as e:
            print(f"❌ 基本情報取得エラー: {e}")
            print(f"   エラーの型: {type(e)}")
        
        print("\n3. 履歴データの取得...")
        try:
            history = btc_ticker.history(period="1d")
            print("✅ 履歴データ取得成功")
            print(f"   データの型: {type(history)}")
            shape_info = history.shape if hasattr(history, 'shape') else 'N/A'
            print(f"   データの形状: {shape_info}")
            length_data = len(history) if hasattr(history, '__len__') else 'N/A'
            print(f"   データの長さ: {length_data}")
            
            if not history.empty:
                print("   最新のデータ:")
                latest = history.iloc[-1]
                print(f"     Close: {latest.get('Close', 'N/A')}")
                print(f"     Volume: {latest.get('Volume', 'N/A')}")
            else:
                print("   ⚠️ 履歴データが空です")
                
        except Exception as e:
            print(f"❌ 履歴データ取得エラー: {e}")
            print(f"   エラーの型: {type(e)}")
        
        print("\n4. 現在価格の取得（別の方法）...")
        try:
            # 別の方法で価格を取得
            current_price = btc_ticker.history(period="1d", interval="1m")
            if not current_price.empty:
                latest_price = current_price['Close'].iloc[-1]
                print(f"✅ 現在価格取得成功: ${latest_price:,.2f}")
            else:
                print("❌ 現在価格データが空です")
                
        except Exception as e:
            print(f"❌ 現在価格取得エラー: {e}")
        
        print("\n5. 利用可能な期間と間隔のテスト...")
        test_periods = ["1d", "5d", "1mo"]
        test_intervals = ["1d", "1h", "1m"]
        
        for period in test_periods:
            for interval in test_intervals:
                try:
                    test_data = btc_ticker.history(
                        period=period, interval=interval
                    )
                    if not test_data.empty:
                        data_count = len(test_data)
                        print(f"✅ {period}/{interval}: {data_count}件のデータ")
                    else:
                        print(f"⚠️ {period}/{interval}: データなし")
                except Exception as e:
                    print(f"❌ {period}/{interval}: エラー - {e}")
        
    except Exception as e:
        print(f"❌ 全体的なエラー: {e}")
        print(f"   エラーの型: {type(e)}")
    
    print("\n" + "=" * 50)
    print("🌿✨ デバッグ完了いたしましたわ✨🌿")


if __name__ == "__main__":
    debug_yfinance()
