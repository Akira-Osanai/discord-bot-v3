// ダッシュボードのコア機能

// ダッシュボードの初期化
class DashboardCore {
    constructor() {
        this.isInitialized = false;
        this.updateInterval = null;
        this.init();
    }

    // 初期化
    init() {
        try {
            console.log('DashboardCore: 初期化開始');

            // イベントリスナーの設定
            this.setupEventListeners();

            // 初期データ読み込み
            this.loadInitialData();

            // 自動更新の設定
            this.setupAutoUpdate();

            this.isInitialized = true;
            console.log('DashboardCore: 初期化完了');

        } catch (error) {
            console.error('DashboardCore: 初期化エラー', error);
        }
    }

    // イベントリスナーの設定
    setupEventListeners() {
        // 一年分データ取得ボタン
        const yearlyDataButton = document.getElementById('fetch-yearly-data');
        if (yearlyDataButton) {
            yearlyDataButton.addEventListener('click', () => {
                this.fetchYearlyData();
            });
        }

        // 手動更新ボタン
        const refreshButton = document.getElementById('refresh-data');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshData();
            });
        }
    }

    // 初期データ読み込み
    async loadInitialData() {
        try {
            console.log('DashboardCore: 初期データ読み込み開始');

            // 現在価格、履歴データ、インジケータを並行して取得
            const [currentData, historicalData, indicatorsData] = await Promise.all([
                DataFetcher.fetchCurrentPrice(),
                DataFetcher.fetchHistoricalData(),
                DataFetcher.fetchIndicators()
            ]);

            console.log('DashboardCore: データ取得成功', {
                currentData: !!currentData,
                historicalData: !!historicalData,
                indicatorsData: !!indicatorsData
            });

            // UIを更新
            this.updateUI(currentData, historicalData, indicatorsData);

            console.log('DashboardCore: 初期データ読み込み完了');

        } catch (error) {
            console.error('DashboardCore: 初期データ読み込みエラー', error);
            Utils.showError('初期データの取得に失敗いたしました');
        }
    }

    // UI更新
    updateUI(currentData, historicalData, indicatorsData) {
        try {
            // 現在価格表示の更新
            if (window.PriceDisplay && currentData) {
                window.PriceDisplay.updateCurrentPriceDisplay(currentData);
            }

            // インジケータテーブルの更新
            if (window.IndicatorTable && indicatorsData) {
                window.IndicatorTable.updateIndicatorTable(indicatorsData);
            }

            // サマリー情報の更新
            if (indicatorsData) {
                updateSummarySimple(indicatorsData);
            }

            // 新しく追加したインジケータの表示
            if (window.IndicatorCards && indicatorsData) {
                window.IndicatorCards.updateNewIndicators(indicatorsData);
            }

        } catch (error) {
            console.error('DashboardCore: UI更新エラー', error);
        }
    }

    // データ更新
    async refreshData() {
        try {
            console.log('DashboardCore: データ更新開始');
            Utils.showInfo('データを更新中です...', 'info');

            await this.loadInitialData();

            Utils.showSuccess('データが正常に更新されました✨');
            console.log('DashboardCore: データ更新完了');

        } catch (error) {
            console.error('DashboardCore: データ更新エラー', error);
            Utils.showError('データの更新に失敗いたしました');
        }
    }

    // 一年分データ取得
    async fetchYearlyData() {
        try {
            if (window.DataFetcher) {
                await window.DataFetcher.fetchYearlyData();
            }
        } catch (error) {
            console.error('DashboardCore: 一年分データ取得エラー', error);
        }
    }

    // 自動更新の設定
    setupAutoUpdate() {
        // 既存の自動更新をクリア
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        // 5分ごとに自動更新
        this.updateInterval = setInterval(() => {
            this.refreshData();
        }, 5 * 60 * 1000);

        console.log('DashboardCore: 自動更新設定完了（5分間隔）');
    }

    // クリーンアップ
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        this.isInitialized = false;
        console.log('DashboardCore: クリーンアップ完了');
    }
}

// グローバルに公開
window.DashboardCore = DashboardCore;

// DOM読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', function () {
    console.log('DashboardCore: DOM読み込み完了、初期化開始');
    window.dashboardCore = new DashboardCore();
});
