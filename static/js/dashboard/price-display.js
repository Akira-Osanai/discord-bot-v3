// 価格表示に関する機能

// 現在価格表示の更新
function updateCurrentPriceDisplay(data) {
    document.getElementById('current-price').textContent = Utils.formatCurrency(data.price);
    document.getElementById('current-timestamp').textContent = Utils.formatDateTime(data.timestamp);

    if (data.volume) {
        document.getElementById('volume').textContent = Utils.formatNumber(data.volume);
    }

    if (data.market_cap) {
        document.getElementById('market-cap').textContent = Utils.formatNumber(data.market_cap);
    }

    // 価格変動の計算（24時間）
    // 実際のAPIに24時間変動データがない場合は、履歴データから計算
    calculatePriceChange();
}

// 基本情報表示の更新
function updateInfoDisplay(data) {
    document.getElementById('symbol').textContent = data.symbol || '--';
    document.getElementById('industry').textContent = data.industry || '--';

    if (data.fifty_two_week_high) {
        document.getElementById('fifty-two-week-high').textContent = Utils.formatCurrency(data.fifty_two_week_high);
    }

    if (data.fifty_two_week_low) {
        document.getElementById('fifty-two-week-low').textContent = Utils.formatCurrency(data.fifty_two_week_low);
    }
}

// 価格変動の計算
async function calculatePriceChange() {
    try {
        const historicalData = await DataFetcher.fetchHistoricalData('BTC-USD', '5d', '1d');

        if (historicalData.data && historicalData.data.length >= 2) {
            const currentPrice = historicalData.data[historicalData.data.length - 1].close;
            const previousPrice = historicalData.data[historicalData.data.length - 2].close;

            if (isNaN(currentPrice) || isNaN(previousPrice)) {
                console.error('価格データがNaNです');
                return;
            }

            const change = currentPrice - previousPrice;
            const changePercent = (change / previousPrice) * 100;

            const changeElement = document.getElementById('price-change');
            changeElement.textContent = Utils.formatCurrency(change);

            // 色を変更
            if (change >= 0) {
                changeElement.className = 'text-success mb-1';
            } else {
                changeElement.className = 'text-danger mb-1';
            }
        }
    } catch (error) {
        console.error('価格変動計算エラー:', error);
    }
}

// 履歴データの読み込み（チャート機能は削除されました）
async function loadHistoricalData() {
    try {
        // 固定の期間・間隔でデータを取得
        await DataFetcher.fetchHistoricalData('BTC-USD', '1mo', '1d');

    } catch (error) {
        console.error('履歴データ読み込みエラー:', error);
        Utils.showError('履歴データの取得に失敗いたしました');
    }
}

// グローバルに公開
window.PriceDisplay = {
    updateCurrentPriceDisplay,
    updateInfoDisplay,
    calculatePriceChange,
    loadHistoricalData
};
