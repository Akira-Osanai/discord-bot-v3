# インジケータモジュール

このディレクトリには、テクニカルインジケータの計算を行う各クラスが含まれています。

## 構造

```
services/indicators/
├── __init__.py                    # モジュール初期化ファイル
├── base_indicator.py              # 基底クラス
├── sma_indicator.py               # 単純移動平均（SMA）
├── ema_indicator.py               # 指数移動平均（EMA）
├── rsi_indicator.py               # 相対力指数（RSI）
├── macd_indicator.py              # MACD（移動平均収束発散）
├── bollinger_bands_indicator.py   # ボリンジャーバンド
├── stochastic_indicator.py         # ストキャスティクス
├── atr_indicator.py               # 平均真の範囲（ATR）
├── indicator_factory.py           # インジケータファクトリー
└── README.md                      # このファイル
```

## 設計パターン

### 1. 基底クラス（BaseIndicator）

全てのインジケータクラスの基底クラスです。以下の機能を提供します：

- `calculate()`: 抽象メソッド（各インジケータで実装必須）
- `_to_dataframe()`: MarketDataPointのリストをDataFrameに変換
- `_create_indicator_value()`: IndicatorValueオブジェクトを作成

### 2. ファクトリーパターン（IndicatorFactory）

各インジケータのインスタンスを作成・管理します：

```python
from services.indicators.indicator_factory import indicator_factory

# 特定のインジケータを取得
sma_indicator = indicator_factory.get_indicator(IndicatorType.SMA)

# インジケータを計算
results = sma_indicator.calculate(data, period=20)
```

### 3. 個別インジケータクラス

各インジケータは独立したクラスとして実装されており、以下の特徴があります：

- 単一責任の原則に従い、1つのインジケータのみを計算
- 基底クラスを継承し、共通機能を利用
- パラメータは柔軟に設定可能

## 使用方法

### 基本的な使用方法

```python
from services.indicator_service import indicator_service

# 単一インジケータの計算
sma_results = indicator_service.calculate_sma(data, period=20)
rsi_results = indicator_service.calculate_rsi(data, period=14)

# 複数インジケータの同時計算
configs = [
    IndicatorConfig(type=IndicatorType.SMA, parameters={"period": 20}),
    IndicatorConfig(type=IndicatorType.RSI, parameters={"period": 14})
]
multi_results = indicator_service.calculate_multiple_indicators(data, configs)
```

### 新しいインジケータの追加

1. 新しいインジケータクラスを作成（`base_indicator.py`を継承）
2. `indicator_factory.py`に登録
3. `__init__.py`にインポートを追加

```python
# 例：新しいインジケータクラス
class NewIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(IndicatorType.NEW_INDICATOR)
        self.name = "New Indicator"
    
    def calculate(self, data, **kwargs):
        # インジケータの計算ロジック
        pass
```

## 利点

1. **保守性**: 各インジケータが独立しているため、修正が容易
2. **拡張性**: 新しいインジケータの追加が簡単
3. **テスタビリティ**: 個別のインジケータを独立してテスト可能
4. **再利用性**: 各インジケータクラスを他の場所でも使用可能
5. **責任の分離**: 各クラスが明確な責任を持つ

## 注意事項

- 全てのインジケータクラスは`BaseIndicator`を継承する必要があります
- `calculate()`メソッドは必ず実装してください
- パラメータの型チェックは各インジケータクラスで行ってください
- エラーハンドリングは適切に行い、ログ出力してください

