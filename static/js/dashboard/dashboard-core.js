// メインのダッシュボード機能

// 既存のUtilsオブジェクトにshowInfo関数を追加
if (window.Utils && !window.Utils.showInfo) {
    window.Utils.showInfo = function (message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);

        // Bootstrapトーストの作成
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${window.Utils.getBootstrapColor(type)} border-0" 
                 id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        // トーストコンテナの作成（存在しない場合）
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // トーストを追加
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        // Bootstrapトーストを表示
        const toastElement = document.getElementById(toastId);
        if (toastElement && typeof bootstrap !== 'undefined') {
            const toast = new bootstrap.Toast(toastElement, {
                autohide: true,
                delay: type === 'error' ? 5000 : 3000
            });
            toast.show();

            // 自動削除
            setTimeout(() => {
                if (toastElement.parentNode) {
                    toastElement.parentNode.removeChild(toastElement);
                }
            }, 6000);
        } else {
            // フォールバック: シンプルなアラート
            alert(`${type.toUpperCase()}: ${message}`);
        }
    };

    window.Utils.getBootstrapColor = function (type) {
        switch (type) {
            case 'success': return 'success';
            case 'error': return 'danger';
            case 'warning': return 'warning';
            case 'info':
            default: return 'info';
        }
    };
}

// イベントリスナーの設定
function setupEventListeners() {
    // 期間変更のイベントリスナー
    const periodSelect = document.getElementById('period-select');
    if (periodSelect) {
        periodSelect.addEventListener('change', function () {
            const selectedPeriod = this.value;
            console.log('期間変更:', selectedPeriod);
            loadDashboardData(selectedPeriod);
        });
    }

    // 間隔変更のイベントリスナー
    const intervalSelect = document.getElementById('interval-select');
    if (intervalSelect) {
        intervalSelect.addEventListener('change', function () {
            const selectedInterval = this.value;
            console.log('間隔変更:', selectedInterval);
            loadDashboardData(null, selectedInterval);
        });
    }

    // データ更新ボタンのイベントリスナー
    const refreshButton = document.getElementById('refresh-data');
    if (refreshButton) {
        refreshButton.addEventListener('click', function () {
            console.log('データ更新ボタンがクリックされました');
            loadDashboardData();
        });
    }

    // 一年分データ取得ボタンのイベントリスナー
    const yearlyDataButton = document.getElementById('fetch-yearly-data');
    if (yearlyDataButton) {
        yearlyDataButton.addEventListener('click', function () {
            console.log('一年分データ取得ボタンがクリックされました');
            DataFetcher.fetchYearlyData();
        });
    }
}

// ダッシュボードデータの読み込み
async function loadDashboardData(period = null, interval = null) {
    try {
        // ローディング状態の設定
        Utils.showInfo('データを更新中です...', 'info');

        // データの取得
        const [
            currentData,
            infoData,
            historicalData,
            indicatorsData
        ] = await Promise.all([
            fetch('/btc/current'),
            fetch('/btc/info'),
            PriceDisplay.loadHistoricalData(),
            DataFetcher.fetchIndicators(period || '30d', interval || '1d')
        ]);

        // UIの更新
        updateDashboardUI(indicatorsData);

    } catch (error) {
        console.error('ダッシュボードデータ読み込みエラー:', error);
        Utils.showError('データの読み込みに失敗いたしました');
    }
}

// ダッシュボードUIの更新
function updateDashboardUI(indicatorsData) {
    // インジケータテーブルの更新
    IndicatorTable.updateIndicatorTable(indicatorsData);

    // サマリー情報を更新（シンプルなカウント計算）
    SummaryCalculator.updateSummarySimple(indicatorsData);

    // 新しく追加したインジケータの表示
    IndicatorCards.updateNewIndicators(indicatorsData);
}

// ローソク足チャートの更新
function updateChart(data) {
    try {
        // チャート機能は削除されました

    } catch (error) {
        console.error('Error in updateChart:', error);
        showChartError('チャートの更新中にエラーが発生いたしました');
    }
}

// チャートエラーの表示
function showChartError(message) {
    const chartContainer = document.getElementById('chart-container');
    if (chartContainer) {
        chartContainer.innerHTML = `
            <div class="alert alert-warning text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}

// グローバルに公開
window.DashboardCore = {
    setupEventListeners,
    loadDashboardData,
    updateDashboardUI,
    updateChart,
    showChartError
};
