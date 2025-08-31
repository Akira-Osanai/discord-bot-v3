// インジケータテーブルに関する機能

// インジケータテーブルの更新
function updateIndicatorTable(data) {
    if (!data || !data.indicators || data.indicators.length === 0) {
        console.warn('インジケータデータが不足しています');
        return;
    }

    const tbody = document.getElementById('indicator-table-body');
    let tableHTML = '';

    // 各インジケータの分析データを表示
    data.indicators.forEach(indicator => {
        const analysis = data.analysis[indicator.name];
        if (analysis) {
            let status = '';
            let statusClass = '';

            // ステータスに応じた表示
            if (analysis.signal === 'bullish') {
                status = '強気';
                statusClass = 'text-success';
            } else if (analysis.signal === 'bearish') {
                status = '弱気';
                statusClass = 'text-danger';
            } else {
                status = '中立';
                statusClass = 'text-warning';
            }

            const displayName = indicator.display_name || indicator.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

            tableHTML += `
                <tr class="table-dark text-light">
                    <td class="text-light"><strong>${displayName}</strong></td>
                    <td class="text-light">${formatIndicatorValue(analysis.value)}</td>
                    <td class="text-light">${analysis.strength ? formatStrength(analysis.strength) : '--'}</td>
                    <td class="${statusClass}">${status}</td>
                </tr>
            `;
        } else {
            // 分析データがない場合
            const displayName = indicator.display_name || indicator.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            tableHTML += `
                <tr class="table-dark text-light">
                    <td class="text-light"><strong>${displayName}</strong></td>
                    <td class="text-light">--</td>
                    <td class="text-light">--</td>
                    <td class="text-muted">--</td>
                </tr>
            `;
        }
    });

    tbody.innerHTML = tableHTML;
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

// 重要度のフォーマット
function formatStrength(strength) {
    if (typeof strength === 'number') {
        const strengthText = strength.toFixed(2);

        if (strength >= 0.8) {
            return `<span class="text-danger fw-bold">${strengthText} (高)</span>`;
        } else if (strength >= 0.6) {
            return `<span class="text-warning fw-bold">${strengthText} (中)</span>`;
        } else {
            return `<span class="text-muted">${strengthText} (低)</span>`;
        }
    }
    return '--';
}



// グローバルに公開
window.IndicatorTable = {
    updateIndicatorTable,
    formatIndicatorValue,
    formatStrength
};
