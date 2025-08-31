#!/usr/bin/env python3
"""
BTC/USD APIのテストスクリプト
"""

import requests


def test_api_endpoints():
    """APIの各エンドポイントをテスト"""
    base_url = "http://localhost:8000"

    print("🌙✨ BTC/USD API テストを開始いたしますわ✨🌙")
    print("=" * 50)

    # ヘルスチェック
    try:
        print("\n1. ヘルスチェック...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ ヘルスチェック成功")
            print(f"   ステータス: {response.json()['status']}")
        else:
            print("❌ ヘルスチェック失敗")
    except requests.exceptions.ConnectionError:
        print("❌ APIサーバーに接続できません。サーバーが起動しているかご確認ください。")
        return

    # ルートエンドポイント
    try:
        print("\n2. ルートエンドポイント...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ ルートエンドポイント成功")
            data = response.json()
            print(f"   メッセージ: {data['message']}")
            print(f"   利用可能エンドポイント: {list(data['endpoints'].keys())}")
        else:
            print("❌ ルートエンドポイント失敗")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 現在価格取得
    try:
        print("\n3. 現在価格取得...")
        response = requests.get(f"{base_url}/btc/current")
        if response.status_code == 200:
            print("✅ 現在価格取得成功")
            data = response.json()
            print(f"   シンボル: {data['symbol']}")
            print(f"   価格: ${data['price']:,.2f}")
            print(f"   通貨: {data['currency']}")
            print(f"   タイムスタンプ: {data['timestamp']}")
            if data.get('volume'):
                print(f"   出来高: {data['volume']:,.0f}")
            if data.get('market_cap'):
                print(f"   時価総額: ${data['market_cap']:,.0f}")
        else:
            print(f"❌ 現在価格取得失敗: {response.status_code}")
            print(f"   エラー: {response.text}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 履歴データ取得
    try:
        print("\n4. 履歴データ取得（5日間、日次）...")
        url = f"{base_url}/btc/historical?period=5d&interval=1d"
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ 履歴データ取得成功")
            data = response.json()
            print(f"   シンボル: {data['symbol']}")
            print(f"   期間: {data['period']}")
            print(f"   間隔: {data['interval']}")
            print(f"   データ件数: {data['data_count']}")

            # 最新の3件を表示
            print("   最新データ:")
            for i, item in enumerate(data['data'][-3:], 1):
                date_str = item['timestamp'][:10]
                open_price = item['open']
                close_price = item['close']
                print(f"     {i}. {date_str}: "
                      f"Open: ${open_price}, Close: ${close_price}")
        else:
            print(f"❌ 履歴データ取得失敗: {response.status_code}")
            print(f"   エラー: {response.text}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 基本情報取得
    try:
        print("\n5. 基本情報取得...")
        response = requests.get(f"{base_url}/btc/info")
        if response.status_code == 200:
            print("✅ 基本情報取得成功")
            data = response.json()
            print(f"   名前: {data['name']}")
            print(f"   セクター: {data['sector']}")
            print(f"   業界: {data['industry']}")
            print(f"   通貨: {data['currency']}")
            print(f"   取引所: {data['exchange']}")
            if data.get('market_cap'):
                print(f"   時価総額: ${data['market_cap']:,.0f}")
        else:
            print(f"❌ 基本情報取得失敗: {response.status_code}")
            print(f"   エラー: {response.text}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    print("\n" + "=" * 50)
    print("🌿✨ テスト完了いたしましたわ✨🌿")


if __name__ == "__main__":
    test_api_endpoints()
