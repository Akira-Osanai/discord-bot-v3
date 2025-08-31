// データ取得に関する機能

// 履歴データの取得
async function fetchHistoricalData(symbol = 'BTC-USD', period = '1mo', interval = '1d') {
    const response = await fetch(`/api/historical/${symbol}?period=${period}&interval=${interval}`);
    if (!response.ok) {
        throw new Error('履歴データの取得に失敗いたしました');
    }
    return await response.json();
}

// インジケータデータの取得
async function fetchIndicators(symbol = 'BTC-USD', period = '1mo', interval = '1d') {
    try {
        // インジケータ一覧を取得
        const indicatorsResponse = await fetch('/api/indicators');
        if (!indicatorsResponse.ok) {
            throw new Error('インジケータ一覧の取得に失敗いたしました');
        }
        const indicators = await indicatorsResponse.json();

        // 各インジケータの分析データを取得
        const indicatorData = {};
        for (const indicator of indicators) {
            try {
                const analysisResponse = await fetch(`/api/analysis/${symbol}/${indicator.name}?period=${period}&interval=${interval}`);
                if (analysisResponse.ok) {
                    const analysis = await analysisResponse.json();
                    indicatorData[indicator.name] = analysis;
                }
            } catch (error) {
                console.warn(`${indicator.name}の分析データ取得エラー:`, error);
            }
        }

        return {
            indicators: indicators,
            analysis: indicatorData
        };
    } catch (error) {
        console.error('インジケータデータの取得エラー:', error);
        throw error;
    }
}

// 現在価格データの取得
async function fetchCurrentPrice(symbol = 'BTC-USD', period = '1d', interval = '1m') {
    const response = await fetch(`/api/price/${symbol}?period=${period}&interval=${interval}`);
    if (!response.ok) {
        throw new Error('現在価格の取得に失敗いたしました');
    }
    return await response.json();
}

// 一年分データ取得
async function fetchYearlyData(symbol = 'BTC-USD') {
    try {
        const button = document.getElementById('fetch-yearly-data');
        const progressDiv = document.getElementById('fetch-progress');

        if (button) button.disabled = true;
        if (progressDiv) progressDiv.innerHTML = '<div class="progress"><div class="progress-bar" role="progressbar" style="width: 0%"></div></div>';

        const progressBar = progressDiv?.querySelector('.progress-bar');

        // 各期間のデータを順次取得
        const periods = ['1mo', '3mo', '6mo', '1y'];
        let completed = 0;

        for (const period of periods) {
            try {
                await fetchHistoricalData(symbol, period, '1d');
                completed++;
                if (progressBar) {
                    progressBar.style.width = `${(completed / periods.length) * 100}%`;
                    progressBar.textContent = `${Math.round((completed / periods.length) * 100)}%`;
                }
            } catch (error) {
                console.error(`${period}期間のデータ取得エラー:`, error);
            }
        }

        if (progressDiv) progressDiv.innerHTML = '<div class="alert alert-success">データ取得完了！</div>';
        if (button) button.disabled = false;

        // ダッシュボードを更新
        if (typeof loadDashboardData === 'function') {
            loadDashboardData();
        }

    } catch (error) {
        console.error('一年分データ取得エラー:', error);
        if (progressDiv) progressDiv.innerHTML = '<div class="alert alert-danger">データ取得に失敗いたしました</div>';
        if (button) button.disabled = false;
    }
}

// グローバルに公開
window.DataFetcher = {
    fetchHistoricalData,
    fetchIndicators,
    fetchCurrentPrice,
    fetchYearlyData
};
