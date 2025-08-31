"""
データ蓄積用ストレージサービス
データベースまたはCSVファイルにデータを保存いたします
"""

import csv
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StorageService:
    """データ蓄積用ストレージサービス"""

    def __init__(self, storage_type: str = "csv", data_dir: str = "data"):
        """
        初期化

        Args:
            storage_type: ストレージタイプ ("csv" または "json")
            data_dir: データ保存ディレクトリ
        """
        self.storage_type = storage_type
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        logger.info(f"ストレージサービス初期化完了: {storage_type}, ディレクトリ: {data_dir}")

    def save_market_data(self, symbol: str, data: Dict, data_type: str = "market") -> bool:
        """
        市場データを保存

        Args:
            symbol: 通貨ペアシンボル
            data_type: データタイプ ("market", "historical", "indicators")
            data: 保存するデータ

        Returns:
            保存成功時True
        """
        try:
            if self.storage_type == "csv":
                return self._save_to_csv(symbol, data, data_type)
            elif self.storage_type == "json":
                return self._save_to_json(symbol, data, data_type)
            else:
                logger.error(f"サポートされていないストレージタイプ: {self.storage_type}")
                return False

        except Exception as e:
            logger.error(f"データ保存エラー: {str(e)}")
            return False

    def _save_to_csv(self, symbol: str, data: Dict, data_type: str) -> bool:
        """CSVファイルにデータを保存"""
        try:
            # ファイル名を生成
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
            filename = f"{symbol}_{data_type}_{timestamp}.csv"
            filepath = self.data_dir / filename

            # データをCSV形式に変換
            if data_type == "market":
                csv_data = self._convert_market_data_to_csv(data)
            elif data_type == "historical" or data_type.startswith("historical_"):
                csv_data = self._convert_historical_data_to_csv(data)
            elif data_type == "indicators" or data_type.startswith("indicators_"):
                csv_data = self._convert_indicators_data_to_csv(data)
            else:
                logger.error(f"サポートされていないデータタイプ: {data_type}")
                return False

            # CSVファイルに書き込み
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_data)

            logger.info(f"CSVファイルに保存完了: {filepath}")
            return True

        except Exception as e:
            logger.error(f"CSV保存エラー: {str(e)}")
            return False

    def _save_to_json(self, symbol: str, data: Dict, data_type: str) -> bool:
        """JSONファイルにデータを保存"""
        try:
            # ファイル名を生成
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{data_type}_{timestamp}.json"
            filepath = self.data_dir / filename

            # データにメタデータを追加
            data_with_meta = {
                "symbol": symbol,
                "data_type": data_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data
            }

            # JSONファイルに書き込み
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data_with_meta, jsonfile,
                          ensure_ascii=False, indent=2)

            logger.info(f"JSONファイルに保存完了: {filepath}")
            return True

        except Exception as e:
            logger.error(f"JSON保存エラー: {str(e)}")
            return False

    def _convert_market_data_to_csv(self, data: Dict) -> List[List]:
        """市場データをCSV形式に変換"""
        csv_data = [
            ["timestamp", "symbol", "price", "currency", "volume",
                "market_cap", "change_24h", "change_24h_percent"]
        ]

        # 単一データの場合
        if "timestamp" in data:
            row = [
                data.get("timestamp", ""),
                data.get("symbol", ""),
                data.get("price", ""),
                data.get("currency", ""),
                data.get("volume", ""),
                data.get("market_cap", ""),
                data.get("change_24h", ""),
                data.get("change_24h_percent", "")
            ]
            csv_data.append(row)

        return csv_data

    def _convert_historical_data_to_csv(self, data: Dict) -> List[List]:
        """履歴データをCSV形式に変換"""
        csv_data = [
            ["timestamp", "open", "high", "low", "close", "volume"]
        ]

        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                row = [
                    item.get("timestamp", ""),
                    item.get("open", ""),
                    item.get("high", ""),
                    item.get("low", ""),
                    item.get("close", ""),
                    item.get("volume", "")
                ]
                csv_data.append(row)

        return csv_data

    def _convert_indicators_data_to_csv(self, data: Dict) -> List[List]:
        """インジケータデータをCSV形式に変換"""
        csv_data = [
            ["timestamp", "indicator_name", "value", "parameters"]
        ]

        if "indicators" in data and isinstance(data["indicators"], list):
            for indicator in data["indicators"]:
                timestamp = indicator.get("timestamp", "")
                values = indicator.get("values", {})

                for name, value in values.items():
                    row = [
                        timestamp,
                        name,
                        value,
                        json.dumps(indicator.get("parameters", {}),
                                   ensure_ascii=False)
                    ]
                    csv_data.append(row)

        return csv_data

    def get_stored_data(self, symbol: str, data_type: str, date: Optional[str] = None) -> List[Dict]:
        """
        保存されたデータを取得

        Args:
            symbol: 通貨ペアシンボル
            data_type: データタイプ
            date: 日付（YYYYMMDD形式、未指定の場合は最新）

        Returns:
            保存されたデータのリスト
        """
        try:
            if self.storage_type == "csv":
                return self._get_from_csv(symbol, data_type, date)
            elif self.storage_type == "json":
                return self._get_from_json(symbol, data_type, date)
            else:
                logger.error(f"サポートされていないストレージタイプ: {self.storage_type}")
                return []

        except Exception as e:
            logger.error(f"データ取得エラー: {str(e)}")
            return []

    def _get_from_csv(self, symbol: str, data_type: str, date: Optional[str] = None) -> List[Dict]:
        """CSVファイルからデータを取得"""
        try:
            data_list = []

            # ファイルを検索
            if date:
                filename = f"{symbol}_{data_type}_{date}.csv"
                filepath = self.data_dir / filename
                if filepath.exists():
                    data_list.extend(self._read_csv_file(filepath))
            else:
                # 最新のファイルを検索
                pattern = f"{symbol}_{data_type}_*.csv"
                files = sorted(self.data_dir.glob(pattern), reverse=True)
                if files:
                    data_list.extend(self._read_csv_file(files[0]))

            return data_list

        except Exception as e:
            logger.error(f"CSV読み込みエラー: {str(e)}")
            return []

    def _get_from_json(self, symbol: str, data_type: str, date: Optional[str] = None) -> List[Dict]:
        """JSONファイルからデータを取得"""
        try:
            data_list = []

            # ファイルを検索
            if date:
                filename = f"{symbol}_{data_type}_{date}.json"
                filepath = self.data_dir / filename
                if filepath.exists():
                    data_list.append(self._read_json_file(filepath))
            else:
                # 最新のファイルを検索
                pattern = f"{symbol}_{data_type}_*.json"
                files = sorted(self.data_dir.glob(pattern), reverse=True)
                if files:
                    data_list.append(self._read_json_file(files[0]))

            return data_list

        except Exception as e:
            logger.error(f"JSON読み込みエラー: {str(e)}")
            return []

    def _read_csv_file(self, filepath: Path) -> List[Dict]:
        """CSVファイルを読み込み"""
        data_list = []

        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data_list.append(dict(row))

        return data_list

    def _read_json_file(self, filepath: Path) -> Dict:
        """JSONファイルを読み込み"""
        with open(filepath, 'r', encoding='utf-8') as jsonfile:
            return json.load(jsonfile)

    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        古いデータファイルを削除

        Args:
            days_to_keep: 保持する日数

        Returns:
            削除されたファイル数
        """
        try:
            deleted_count = 0
            cutoff_date = datetime.now(
                timezone.utc).timestamp() - (days_to_keep * 24 * 60 * 60)

            for filepath in self.data_dir.iterdir():
                if filepath.is_file():
                    file_age = filepath.stat().st_mtime
                    if file_age < cutoff_date:
                        filepath.unlink()
                        deleted_count += 1
                        logger.info(f"古いファイルを削除: {filepath}")

            logger.info(f"古いデータファイルのクリーンアップ完了: {deleted_count}件削除")
            return deleted_count

        except Exception as e:
            logger.error(f"データクリーンアップエラー: {str(e)}")
            return 0


# グローバルインスタンス
storage_service = StorageService()
