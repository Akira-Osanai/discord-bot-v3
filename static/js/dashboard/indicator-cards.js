// インジケータカードに関する機能

// 新しく追加したインジケータの表示
function updateNewIndicators(data) {
    if (!data || !data.analysis) {
        console.warn('分析データが不足しています');
        return;
    }

    // 新しく追加したインジケータのリスト
    const newIndicators = [
        'Hash Rate', 'Active Addresses', 'Fear & Greed Index',
        'Correlation', 'Realized Volatility'
    ];

    // 各新しく追加したインジケータの値を表示
    newIndicators.forEach(indicatorName => {
        const analysis = data.analysis[indicatorName];
        if (analysis) {
            // インジケータカードに値を表示
            updateIndicatorCard(indicatorName, analysis);
        }
    });
}

// インジケータカードの値を更新
function updateIndicatorCard(indicatorName, analysis) {
    // インジケータカードの要素を探す
    const card = document.querySelector(`[data-indicator="${indicatorName}"]`);
    if (!card) {
        console.warn(`${indicatorName}のカードが見つかりません`);
        return;
    }

    // 値表示用の要素を探す
    const valueElement = card.querySelector('.indicator-value');
    if (valueElement) {
        valueElement.textContent = formatIndicatorValue(analysis.value);
    }

    // ステータス表示用の要素を探す
    const statusElement = card.querySelector('.indicator-status');
    if (statusElement) {
        const status = getStatusFromSignal(analysis.signal);
        statusElement.textContent = status;
        statusElement.className = `indicator-status badge bg-${getStatusColor(status)}`;
    }

    // シグナル表示用の要素を探す
    const signalElement = card.querySelector('.indicator-signal');
    if (signalElement) {
        signalElement.textContent = analysis.signal || 'neutral';
        signalElement.className = `indicator-signal badge bg-${getSignalColor(analysis.signal)}`;
    }
}

// シグナルからステータスを取得
function getStatusFromSignal(signal) {
    switch (signal) {
        case 'bullish': return 'up';
        case 'bearish': return 'down';
        default: return 'neutral';
    }
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
    return value || '--';
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

// グローバルに公開
window.IndicatorCards = {
    updateNewIndicators,
    updateIndicatorCard,
    formatIndicatorValue,
    getStatusColor,
    getSignalColor
};
