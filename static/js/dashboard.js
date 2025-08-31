// ダッシュボード専用JavaScript



// 既存のUtilsオブジェクトにshowInfo関数を追加
if (window.Utils && !window.Utils.showInfo) {
    window.Utils.showInfo = function (message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);

        // Bootstrapトーストの作成
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${this.getBootstrapColor(type)} border-0" 
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





document.addEventListener('DOMContentLoaded', function () {
    console.log('ダッシュボードが読み込まれました✨');

    // Bootstrapの読み込み状況を確認
    console.log('=== Bootstrap Status Check ===');
    console.log('Bootstrap object:', typeof bootstrap);
    console.log('Bootstrap version:', bootstrap?.VERSION);
    console.log('Bootstrap Modal:', typeof bootstrap?.Modal);
    console.log('Bootstrap Modal constructor:', bootstrap?.Modal);
    console.log('================================');

    // シンプルな初期化確認
    console.log('=== Dashboard Initialization ===');
    console.log('Dashboard loaded successfully');
    console.log('================================');

    // チャート機能は削除されました
    console.log('=== Chart Functionality Removed ===');
    console.log('Chart functionality has been removed from this dashboard');
    console.log('================================');

    // イベントリスナーの設定
    setupEventListeners();

    // DOMの準備が完了してから初期データ読み込み
    setTimeout(() => {
        console.log('Starting initial data load after DOM preparation...');

        // チャート機能は削除されました
        console.log('Chart functionality has been removed, loading dashboard data directly...');
        loadDashboardData();

    }, 1000); // より長めに待機

    // 自動更新の設定（5分ごと）
    setInterval(loadDashboardData, 5 * 60 * 1000);
});

// イベントリスナーの設定
function setupEventListeners() {
    // 一年分データ取得ボタン
    document.getElementById('fetch-yearly-data').addEventListener('click', function () {
        fetchYearlyData();
    });
}

// ダッシュボードデータの読み込み
async function loadDashboardData() {
    try {
        console.log('loadDashboardData started');

        // シンプルなトースト通知でローディング開始
        console.log('Starting data update...');
        Utils.showInfo('データを更新中です...', 'info');

        // 現在価格、履歴データ、インジケータを並行して取得
        console.log('Fetching data...');
        const [currentData, historicalData, indicatorsData] = await Promise.all([
            DataFetcher.fetchCurrentPrice(),
            DataFetcher.fetchHistoricalData(),
            DataFetcher.fetchIndicators()
        ]);

        console.log('Data fetched successfully:', {
            currentData: !!currentData,
            historicalData: !!historicalData,
            indicatorsData: !!indicatorsData
        });

        // UIを更新
        console.log('Updating UI...');
        updateCurrentPriceDisplay(currentData);
        updateIndicatorTable(indicatorsData);

        // サマリー情報を更新（シンプルなカウント計算）
        updateSummarySimple(indicatorsData);

        // 新しく追加したインジケータの表示
        updateNewIndicators(indicatorsData);

        console.log('UI update completed');

        // ローディング状態の解除（トースト通知のみ）
        console.log('Data update completed successfully');
        Utils.showSuccess('データが正常に更新されました✨');

    } catch (error) {
        console.error('ダッシュボードデータ読み込みエラー:', error);

        // エラー時の処理（トースト通知のみ）
        console.log('Data update failed');
        Utils.showError('データの取得に失敗いたしました。もう一度お試しください。');
    }
}

// インジケータデータの取得（日足のみ）
async function fetchIndicators(period = '30d', interval = '1d') {
    // 日足以降の間隔のみ許可
    const validIntervals = ['1d', '3d', '7d', '1mo'];
    if (!validIntervals.includes(interval)) {
        console.warn(`無効な間隔: ${interval}. 日足に変更します。`);
        interval = '1d';
    }

    console.log(`インジケータ取得開始: period=${period}, interval=${interval}`);
    const response = await fetch(`/BTC-USD/indicators?period=${period}&interval=${interval}`);
    if (!response.ok) {
        throw new Error('インジケータデータの取得に失敗いたしました');
    }

    const data = await response.json();
    console.log('インジケータデータ取得完了:', data);
    console.log('インジケータ数:', data.indicators ? data.indicators.length : 0);
    if (data.indicators && data.indicators.length > 0) {
        console.log('最初のインジケータデータ:', data.indicators[0]);
        console.log('利用可能なインジケータ:', Object.keys(data.indicators[0].values || {}));
    }

    return data;
}

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
        console.log('価格変動計算開始');
        const historicalData = await fetchHistoricalData('5d', '1d');
        console.log('履歴データ取得結果:', historicalData);

        if (historicalData.data && historicalData.data.length >= 2) {
            console.log('履歴データ配列:', historicalData.data);
            console.log('最新データ:', historicalData.data[historicalData.data.length - 1]);
            console.log('前回データ:', historicalData.data[historicalData.data.length - 2]);

            const currentPrice = historicalData.data[historicalData.data.length - 1].close;
            const previousPrice = historicalData.data[historicalData.data.length - 2].close;

            console.log('現在価格:', currentPrice);
            console.log('前回価格:', previousPrice);

            if (isNaN(currentPrice) || isNaN(previousPrice)) {
                console.error('価格データがNaNです:', { currentPrice, previousPrice });
                return;
            }

            const change = currentPrice - previousPrice;
            const changePercent = (change / previousPrice) * 100;

            console.log('価格変動:', change);
            console.log('変動率:', changePercent);

            const changeElement = document.getElementById('price-change');
            changeElement.textContent = Utils.formatCurrency(change);

            // 色を変更
            if (change >= 0) {
                changeElement.className = 'text-success mb-1';
            } else {
                changeElement.className = 'text-danger mb-1';
            }
        } else {
            console.warn('履歴データが不足しています:', historicalData);
        }
    } catch (error) {
        console.error('価格変動計算エラー:', error);
    }
}

// 履歴データの読み込み（チャート機能は削除されました）
async function loadHistoricalData() {
    try {
        // 固定の期間・間隔でデータを取得
        const data = await fetchHistoricalData('30d', '1d');
        console.log('Historical data loaded:', data);

    } catch (error) {
        console.error('履歴データ読み込みエラー:', error);
        Utils.showError('履歴データの取得に失敗いたしました');
    }
}

// ローソク足チャートの更新
function updateChart(data) {
    console.log('updateChart called with data:', data);

    try {
        // チャート機能は削除されました
        console.log('Chart functionality has been removed');

    } catch (error) {
        console.error('Error in updateChart:', error);
        showChartError('チャートの更新中にエラーが発生いたしました');
    }
}





// インジケータテーブルの更新
function updateIndicatorTable(data) {
    console.log('インジケータテーブル更新開始:', data);

    if (!data || !data.indicators || data.indicators.length === 0) {
        console.warn('インジケータデータが不足しています');
        return;
    }

    const tbody = document.getElementById('indicator-table-body');
    const latestData = data.indicators[data.indicators.length - 1];
    const previousData = data.indicators[data.indicators.length - 2];

    console.log('最新データ:', latestData);
    console.log('前回データ:', previousData);
    console.log('利用可能なインジケータ:', Object.keys(latestData.values || {}));

    let tableHTML = '';

    // 既存のインジケータを表に追加（data.analysis_summary.indicator_statesから取得）
    if (data.analysis_summary && data.analysis_summary.indicator_states) {
        const existingIndicators = [
            'EMA', 'MACD', 'ATR', 'OBV', 'Parabolic SAR', 'Ichimoku Cloud',
            'RSI', 'Williams %R', 'Money Flow Index', 'Stochastic', 'SMA',
            'BollingerBands', 'CCI', 'VWAP', 'Keltner Channel', 'Donchian Channel',
            'Rate of Change', 'ADX'
        ];

        existingIndicators.forEach(indicatorName => {
            const state = data.analysis_summary.indicator_states[indicatorName];
            if (state) {
                let status = '';
                let statusClass = '';

                // ステータスに応じた表示
                if (state.status === 'up') {
                    status = '上昇';
                    statusClass = 'text-success';
                } else if (state.status === 'down') {
                    status = '下降';
                    statusClass = 'text-danger';
                } else {
                    status = '中立';
                    statusClass = 'text-warning';
                }

                tableHTML += `
                    <tr>
                        <td><strong>${indicatorName}</strong></td>
                        <td>${formatIndicatorValue(state.value)}</td>
                        <td>--</td>
                        <td class="text-muted">--</td>
                        <td class="${statusClass}">${status}</td>
                    </tr>
                `;
            }
        });
    }

    // 新しく追加したインジケータも表に追加
    if (data.analysis_summary && data.analysis_summary.indicator_states) {
        const newIndicators = [
            'Hash Rate', 'Active Addresses', 'Fear & Greed Index',
            'Correlation', 'Realized Volatility'
        ];

        newIndicators.forEach(indicatorName => {
            const state = data.analysis_summary.indicator_states[indicatorName];
            if (state) {
                let status = '';
                let statusClass = '';

                // ステータスに応じた表示
                if (state.status === 'up') {
                    status = '上昇';
                    statusClass = 'text-success';
                } else if (state.status === 'down') {
                    status = '下降';
                    statusClass = 'text-danger';
                } else {
                    status = '中立';
                    statusClass = 'text-warning';
                }

                tableHTML += `
                    <tr>
                        <td><strong>${indicatorName}</strong></td>
                        <td>${formatIndicatorValue(state.value)}</td>
                        <td>--</td>
                        <td class="text-muted">--</td>
                        <td class="${statusClass}">${status}</td>
                    </tr>
                `;
            }
        });
    }

    tbody.innerHTML = tableHTML;
}

// 新しく追加したインジケータの表示
function updateNewIndicators(data) {
    console.log('新しく追加したインジケータ表示開始:', data);

    if (!data || !data.analysis_summary || !data.analysis_summary.indicator_states) {
        console.warn('分析サマリーデータが不足しています');
        return;
    }

    const indicatorStates = data.analysis_summary.indicator_states;
    console.log('利用可能なインジケータ状態:', Object.keys(indicatorStates));

    // 新しく追加したインジケータのリスト
    const newIndicators = [
        'Hash Rate', 'Active Addresses', 'Fear & Greed Index',
        'Correlation', 'Realized Volatility'
    ];

    // 各新しく追加したインジケータの値を表示
    newIndicators.forEach(indicatorName => {
        if (indicatorStates[indicatorName]) {
            const state = indicatorStates[indicatorName];
            console.log(`${indicatorName}の状態:`, state);

            // インジケータカードに値を表示
            updateIndicatorCard(indicatorName, state);
        } else {
            console.log(`${indicatorName}のデータが見つかりません`);
        }
    });
}

// インジケータカードの値を更新
function updateIndicatorCard(indicatorName, state) {
    console.log(`updateIndicatorCard開始: ${indicatorName}`, state);

    // インジケータカードの要素を探す
    const card = document.querySelector(`[data-indicator="${indicatorName}"]`);
    if (!card) {
        console.log(`${indicatorName}のカードが見つかりません`);
        console.log('利用可能なdata-indicator属性:', Array.from(document.querySelectorAll('[data-indicator]')).map(el => el.getAttribute('data-indicator')));
        return;
    }

    console.log(`${indicatorName}のカードが見つかりました:`, card);

    // 値表示用の要素を探す
    const valueElement = card.querySelector('.indicator-value');
    if (valueElement) {
        valueElement.textContent = formatIndicatorValue(state.value);
        console.log(`${indicatorName}の値を更新:`, formatIndicatorValue(state.value));
    } else {
        console.log(`${indicatorName}の値表示要素が見つかりません`);
        console.log('カード内の要素:', card.innerHTML);
    }

    // ステータス表示用の要素を探す
    const statusElement = card.querySelector('.indicator-status');
    if (statusElement) {
        statusElement.textContent = state.status;
        statusElement.className = `indicator-status badge bg-${getStatusColor(state.status)}`;
        console.log(`${indicatorName}のステータスを更新:`, state.status);
    } else {
        console.log(`${indicatorName}のステータス表示要素が見つかりません`);
    }

    // シグナル表示用の要素を探す
    const signalElement = card.querySelector('.indicator-signal');
    if (signalElement) {
        signalElement.textContent = state.signal;
        signalElement.className = `indicator-signal badge bg-${getSignalColor(state.signal)}`;
        console.log(`${indicatorName}のシグナルを更新:`, state.signal);
    } else {
        console.log(`${indicatorName}のシグナル表示要素が見つかりません`);
    }

    // 更新後のHTMLの状態を確認
    console.log(`${indicatorName}の更新完了。カードのHTML:`, card.innerHTML);

    // 実際のDOMの状態も確認
    const updatedValueElement = card.querySelector('.indicator-value');
    const updatedStatusElement = card.querySelector('.indicator-status');
    const updatedSignalElement = card.querySelector('.indicator-signal');

    console.log(`${indicatorName}の更新後確認:`, {
        value: updatedValueElement ? updatedValueElement.textContent : '要素なし',
        status: updatedStatusElement ? updatedStatusElement.textContent : '要素なし',
        signal: updatedSignalElement ? updatedSignalElement.textContent : '要素なし'
    });
}

// インジケータ値のフォーマット
function formatIndicatorValue(value) {
    if (typeof value === 'number') {
        if (Math.abs(value) >= 1000000) {
            return (value / 1000000).toFixed(2) + 'M';
        } else if (Math.abs(value) >= 1000) {
            return (value / 1000).toFixed(2) + 'K';
        } else if (Math.abs(value) < 0.01) {
            return value.toFixed(6);
        } else {
            return value.toFixed(2);
        }
    }
    return value;
}

// ステータスに応じた色を取得
function getStatusColor(status) {
    switch (status) {
        case 'up': return 'success';
        case 'down': return 'danger';
        case 'neutral': return 'secondary';
        default: return 'info';
    }
}

// シグナルに応じた色を取得
function getSignalColor(signal) {
    switch (signal) {
        case 'bullish': return 'success';
        case 'bearish': return 'danger';
        case 'neutral': return 'secondary';
        default: return 'info';
    }
}

// サマリー情報を更新（シンプルなカウント計算）
function updateSummarySimple(indicatorsData) {
    if (!window.IndicatorSummaryCalculator) {
        console.error('IndicatorSummaryCalculatorが読み込まれていません');
        return;
    }

    // インジケータサマリー計算器を使用
    const calculator = new window.IndicatorSummaryCalculator();
    const counts = calculator.calculateSummary(indicatorsData);

    // 詳細なサマリー表示を更新
    updateDetailedSummary(counts.upCount, counts.downCount, counts.neutralCount, counts.totalCount);

    // デバッグ情報
    console.log('サマリー更新完了:', counts);
}

// 詳細なサマリー表示を更新
function updateDetailedSummary(upCount, downCount, neutralCount, totalCount) {
    // カウント更新
    const upCountEl = document.getElementById('upCount');
    const downCountEl = document.getElementById('downCount');
    const neutralCountEl = document.getElementById('neutralCount');
    const totalCountEl = document.getElementById('totalCount');

    if (upCountEl) upCountEl.textContent = upCount;
    if (downCountEl) downCountEl.textContent = downCount;
    if (neutralCountEl) neutralCountEl.textContent = neutralCount;
    if (totalCountEl) totalCountEl.textContent = totalCount;

    // パーセンテージ計算
    const upPercent = totalCount > 0 ? Math.round((upCount / totalCount) * 100) : 0;
    const downPercent = totalCount > 0 ? Math.round((downCount / totalCount) * 100) : 0;
    const neutralPercent = totalCount > 0 ? Math.round((neutralCount / totalCount) * 100) : 0;

    // 売買スコア更新
    const buyScoreEl = document.getElementById('buyScore');
    const sellScoreEl = document.getElementById('sellScore');

    if (buyScoreEl) buyScoreEl.textContent = upPercent;
    if (sellScoreEl) sellScoreEl.textContent = downPercent;

    // 推奨アクション更新
    const recommendationEl = document.getElementById('recommendation');
    if (recommendationEl) {
        let recommendation = 'データ不足';
        let alertClass = 'alert-info';
        let icon = 'fas fa-info-circle';

        if (upCount > downCount && upCount > neutralCount) {
            recommendation = '買い推奨';
            alertClass = 'alert-success';
            icon = 'fas fa-arrow-up';
        } else if (downCount > upCount && downCount > neutralCount) {
            recommendation = '売り推奨';
            alertClass = 'alert-danger';
            icon = 'fas fa-arrow-down';
        } else if (neutralCount > upCount && neutralCount > downCount) {
            recommendation = 'ホールド推奨';
            alertClass = 'alert-warning';
            icon = 'fas fa-pause';
        } else if (upCount === downCount) {
            recommendation = '中立';
            alertClass = 'alert-info';
            icon = 'fas fa-minus';
        }

        recommendationEl.className = `alert ${alertClass} text-center`;
        recommendationEl.innerHTML = `
            <i class="${icon} me-2"></i>
            <strong>${recommendation}</strong>
        `;
    }

    // 詳細なサマリー情報を表示
    updateSummaryDetails(upCount, downCount, neutralCount, totalCount, upPercent, downPercent, neutralPercent);
}

// サマリー詳細情報を更新
function updateSummaryDetails(upCount, downCount, neutralCount, totalCount, upPercent, downPercent, neutralPercent) {
    // サマリーカードの詳細表示を更新
    const summaryCards = document.querySelectorAll('.summary-card');

    summaryCards.forEach(card => {
        const countEl = card.querySelector('.count-value');
        const percentEl = card.querySelector('.percent-value');

        if (countEl && percentEl) {
            if (card.classList.contains('up-card')) {
                countEl.textContent = upCount;
                percentEl.textContent = `${upPercent}%`;
            } else if (card.classList.contains('down-card')) {
                countEl.textContent = downCount;
                percentEl.textContent = `${downPercent}%`;
            } else if (card.classList.contains('neutral-card')) {
                countEl.textContent = neutralCount;
                percentEl.textContent = `${neutralPercent}%`;
            }
        }
    });

    // 総合的な市場センチメントを表示
    const sentimentEl = document.getElementById('market-sentiment');
    if (sentimentEl) {
        let sentiment = '中立';
        let sentimentClass = 'text-muted';
        let sentimentIcon = 'fas fa-minus';

        if (upPercent > 60) {
            sentiment = '強気';
            sentimentClass = 'text-success';
            sentimentIcon = 'fas fa-arrow-up';
        } else if (downPercent > 60) {
            sentiment = '弱気';
            sentimentClass = 'text-danger';
            sentimentIcon = 'fas fa-arrow-down';
        } else if (upPercent > downPercent) {
            sentiment = 'やや強気';
            sentimentClass = 'text-success';
            sentimentIcon = 'fas fa-arrow-up';
        } else if (downPercent > upPercent) {
            sentiment = 'やや弱気';
            sentimentClass = 'text-danger';
            sentimentIcon = 'fas fa-arrow-down';
        }

        sentimentEl.className = `h5 ${sentimentClass} text-center`;
        sentimentEl.innerHTML = `
            <i class="${sentimentIcon} me-2"></i>
            <strong>${sentiment}</strong>
        `;
    }
}

// グローバルに公開
window.updateSummarySimple = updateSummarySimple;
window.updateDetailedSummary = updateDetailedSummary;
window.updateSummaryDetails = updateSummaryDetails;

// 一年分データ取得
async function fetchYearlyData() {
    try {
        const button = document.getElementById('fetch-yearly-data');
        const progressDiv = document.getElementById('fetch-progress');
        const progressBar = progressDiv.querySelector('.progress-bar');

        // ボタンを無効化
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>取得中...';

        // プログレスバーを表示
        progressDiv.style.display = 'block';
        progressBar.style.width = '0%';

        console.log('一年分データ取得開始...');

        // APIを呼び出し
        const response = await fetch('/data/fetch-yearly', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol: 'BTC-USD' })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('一年分データ取得完了:', result);

        // プログレスバーを100%に
        progressBar.style.width = '100%';

        // 成功メッセージを表示
        Utils.showSuccess(`一年分データ取得完了！${result.successful}/${result.total_intervals}件のデータを保存いたしました✨`);

        // 3秒後にプログレスバーを非表示
        setTimeout(() => {
            progressDiv.style.display = 'none';
            progressBar.style.width = '0%';
        }, 3000);

    } catch (error) {
        console.error('一年分データ取得エラー:', error);
        Utils.showError(`一年分データ取得に失敗いたしました: ${error.message}`);

        // プログレスバーを非表示
        document.getElementById('fetch-progress').style.display = 'none';
    } finally {
        // ボタンを有効化
        const button = document.getElementById('fetch-yearly-data');
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-download me-2"></i>一年分データ取得開始';
    }
}

// エラーハンドリング
window.addEventListener('error', function (e) {
    console.error('JavaScriptエラー詳細:', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error,
        stack: e.error?.stack
    });
    Utils.showError('予期しないエラーが発生いたしました');
});

// ネットワークエラーのハンドリング
window.addEventListener('unhandledrejection', function (e) {
    console.error('未処理のPromise拒否:', e.reason);
    Utils.showError('ネットワークエラーが発生いたしました');
});
