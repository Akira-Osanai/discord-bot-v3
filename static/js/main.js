// メインJavaScriptファイル
document.addEventListener('DOMContentLoaded', function () {
    console.log('BTC/USD API ダッシュボードが読み込まれました✨');

    // ページ読み込み時のアニメーション
    animatePageLoad();

    // ナビゲーションのアクティブ状態を設定
    setActiveNavigation();
});

// ページ読み込みアニメーション
function animatePageLoad() {
    const elements = document.querySelectorAll('.card, .hero-section');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';

        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ナビゲーションのアクティブ状態を設定
function setActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ユーティリティ関数
window.Utils = {
    // 数値をフォーマット
    formatNumber: function (num) {
        if (num === null || num === undefined) return '--';

        if (num >= 1e9) {
            return (num / 1e9).toFixed(2) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(2) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(2) + 'K';
        } else {
            return num.toLocaleString();
        }
    },

    // 通貨をフォーマット
    formatCurrency: function (amount, currency = 'USD') {
        if (amount === null || amount === undefined) return '--';

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    },

    // 日時をフォーマット
    formatDateTime: function (dateString) {
        if (!dateString) return '--';

        const date = new Date(dateString);
        return date.toLocaleString('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // パーセンテージをフォーマット
    formatPercentage: function (value) {
        if (value === null || value === undefined) return '--';

        return value.toFixed(2) + '%';
    },

    // ローディング表示
    showLoading: function () {
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();
    },

    // ローディング非表示
    hideLoading: function () {
        const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (loadingModal) {
            loadingModal.hide();
        }
    },

    // エラーメッセージを表示
    showError: function (message) {
        // Bootstrap のトーストまたはアラートを使用
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // 5秒後に自動で消す
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    },

    // 成功メッセージを表示
    showSuccess: function (message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 3000);
    }
};

// グローバルに公開完了


