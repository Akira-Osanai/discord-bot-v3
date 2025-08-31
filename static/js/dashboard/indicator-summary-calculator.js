/**
 * インジケータサマリー計算器
 * インジケータデータから買い・売り・中立のカウントを計算し、サマリー情報を生成します
 */

class IndicatorSummaryCalculator {
    constructor() {
        this.upCount = 0;
        this.downCount = 0;
        this.neutralCount = 0;
        this.totalCount = 0;
    }

    /**
     * インジケータデータからサマリーを計算
     * @param {Object} indicatorsData - インジケータデータ
     * @returns {Object} 計算結果 {upCount, downCount, neutralCount, totalCount}
     */
    calculateSummary(indicatorsData) {
        // カウントをリセット
        this.resetCounts();

        if (!indicatorsData || !indicatorsData.indicators || !indicatorsData.analysis) {
            console.log('インジケータデータが不足しています');
            console.log('indicatorsData:', indicatorsData);
            return this.getCounts();
        }

        // データ構造を確認
        console.log('データ構造確認:', {
            hasIndicators: !!indicatorsData.indicators,
            hasAnalysis: !!indicatorsData.analysis,
            indicatorsType: typeof indicatorsData.indicators,
            analysisType: typeof indicatorsData.analysis
        });

        // インジケータデータの構造に応じて処理
        let indicatorValues = {};

        if (indicatorsData.analysis && typeof indicatorsData.analysis === 'object') {
            // analysisオブジェクトから値を抽出
            Object.entries(indicatorsData.analysis).forEach(([name, data]) => {
                if (data && data.value !== undefined) {
                    indicatorValues[name] = data.value;
                }
            });
        } else if (indicatorsData.indicators && Array.isArray(indicatorsData.indicators)) {
            // 従来の配列形式の場合
            const latestData = indicatorsData.indicators[indicatorsData.indicators.length - 1];
            if (latestData && latestData.values) {
                indicatorValues = latestData.values;
            }
        }

        if (Object.keys(indicatorValues).length === 0) {
            console.log('インジケータ値が取得できませんでした');
            console.log('indicatorValues:', indicatorValues);
            return this.getCounts();
        }

        console.log('シンプルカウント計算開始:', indicatorValues);
        console.log('インジケータ値の型:', typeof indicatorValues);
        console.log('インジケータ値のキー:', Object.keys(indicatorValues || {}));

        // インジケータ値の状態を判定
        console.log('=== インジケータ値の詳細 ===');
        Object.entries(indicatorValues).forEach(([name, value]) => {
            console.log(`インジケータ: ${name}, 値: ${value}, 型: ${typeof value}`);
            console.log(`  名前判定: RSI含む=${name.includes('rsi')}, MACD含む=${name.includes('macd')}, Stochastic含む=${name.includes('stochastic')}`);

            // 各インジケータの値を集計
            if (typeof value === 'number' && !isNaN(value)) {
                this.analyzeIndicator(name, value);
                this.totalCount++;
            }
        });

        // 結果を表示
        this.logResults();

        return this.getCounts();
    }

    /**
     * 個別インジケータの分析
     * @param {string} name - インジケータ名
     * @param {number} value - インジケータ値
     */
    analyzeIndicator(name, value) {
        if (name.includes('rsi')) {
            this.analyzeRSI(name, value);
        } else if (name.includes('macd')) {
            this.analyzeMACD(name, value);
        } else if (name.includes('stochastic')) {
            this.analyzeStochastic(name, value);
        } else if (name.includes('williams_r')) {
            this.analyzeWilliamsR(name, value);
        } else if (name.includes('cci')) {
            this.analyzeCCI(name, value);
        } else if (name.includes('money_flow_index')) {
            this.analyzeMoneyFlowIndex(name, value);
        } else if (name.includes('adx')) {
            this.analyzeADX(name, value);
        } else if (name.includes('fear_greed_index')) {
            this.analyzeFearGreedIndex(name, value);
        } else if (name.includes('correlation')) {
            this.analyzeCorrelation(name, value);
        } else if (name.includes('rate_of_change')) {
            this.analyzeRateOfChange(name, value);
        } else {
            // その他のインジケータは中立として扱う
            this.neutralCount++;
            console.log(`  ${name}: その他 → neutralCount++`);
        }
    }

    /**
     * RSIの分析
     */
    analyzeRSI(name, value) {
        if (value > 70) {
            this.downCount++; // RSI > 70 は売られすぎ
            console.log(`  ${name}: 売られすぎ (${value} > 70) → downCount++`);
        } else if (value < 30) {
            this.upCount++; // RSI < 30 は買われすぎ
            console.log(`  ${name}: 買われすぎ (${value} < 30) → upCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 中立 (30 <= ${value} <= 70) → neutralCount++`);
        }
    }

    /**
     * MACDの分析
     */
    analyzeMACD(name, value) {
        // MACDは前回値との比較が必要
        this.neutralCount++;
        console.log(`  ${name}: MACD → neutralCount++`);
    }

    /**
     * Stochasticの分析
     */
    analyzeStochastic(name, value) {
        if (value > 80) {
            this.downCount++; // Stochastic > 80 は売られすぎ
            console.log(`  ${name}: 売られすぎ (${value} > 80) → downCount++`);
        } else if (value < 20) {
            this.upCount++; // Stochastic < 20 は買われすぎ
            console.log(`  ${name}: 買われすぎ (${value} < 20) → upCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 中立 (20 <= ${value} <= 80) → neutralCount++`);
        }
    }

    /**
     * Williams %Rの分析
     */
    analyzeWilliamsR(name, value) {
        if (value > -20) {
            this.downCount++; // Williams %R > -20 は売られすぎ
            console.log(`  ${name}: 売られすぎ (${value} > -20) → downCount++`);
        } else if (value < -80) {
            this.upCount++; // Williams %R < -80 は買われすぎ
            console.log(`  ${name}: 買われすぎ (${value} < -80) → upCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 中立 (-80 <= ${value} <= -20) → neutralCount++`);
        }
    }

    /**
     * CCIの分析
     */
    analyzeCCI(name, value) {
        if (value > 100) {
            this.downCount++; // CCI > 100 は売られすぎ
            console.log(`  ${name}: 売られすぎ (${value} > 100) → downCount++`);
        } else if (value < -100) {
            this.upCount++; // CCI < -100 は買われすぎ
            console.log(`  ${name}: 買われすぎ (${value} < -100) → upCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 中立 (-100 <= ${value} <= 100) → neutralCount++`);
        }
    }

    /**
     * Money Flow Indexの分析
     */
    analyzeMoneyFlowIndex(name, value) {
        if (value > 80) {
            this.downCount++; // MFI > 80 は売られすぎ
            console.log(`  ${name}: 売られすぎ (${value} > 80) → downCount++`);
        } else if (value < 20) {
            this.upCount++; // MFI < 20 は買われすぎ
            console.log(`  ${name}: 買われすぎ (${value} < 20) → upCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 中立 (20 <= ${value} <= 80) → neutralCount++`);
        }
    }

    /**
     * ADXの分析
     */
    analyzeADX(name, value) {
        if (value > 25) {
            this.upCount++; // ADX > 25 は強いトレンド
            console.log(`  ${name}: 強いトレンド (${value} > 25) → upCount++`);
        } else {
            this.neutralCount++; // ADX <= 25 は弱いトレンド
            console.log(`  ${name}: 弱いトレンド (${value} <= 25) → neutralCount++`);
        }
    }

    /**
     * Fear & Greed Indexの分析
     */
    analyzeFearGreedIndex(name, value) {
        if (value > 70) {
            this.downCount++; // > 70 は過度な楽観（売りシグナル）
            console.log(`  ${name}: 過度な楽観 (${value} > 70) → downCount++`);
        } else if (value < 30) {
            this.upCount++; // < 30 は過度な悲観（買いシグナル）
            console.log(`  ${name}: 過度な悲観 (${value} < 30) → upCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 中立 (30 <= ${value} <= 70) → neutralCount++`);
        }
    }

    /**
     * 相関係数の分析
     */
    analyzeCorrelation(name, value) {
        if (value > 0.5) {
            this.upCount++; // 強い正の相関
            console.log(`  ${name}: 強い正の相関 (${value} > 0.5) → upCount++`);
        } else if (value < -0.5) {
            this.downCount++; // 強い負の相関
            console.log(`  ${name}: 強い負の相関 (${value} < -0.5) → downCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 弱い相関 (-0.5 <= ${value} <= 0.5) → neutralCount++`);
        }
    }

    /**
     * 変化率の分析
     */
    analyzeRateOfChange(name, value) {
        if (value > 0) {
            this.upCount++; // 正の変化率
            console.log(`  ${name}: 正の変化率 (${value} > 0) → upCount++`);
        } else if (value < 0) {
            this.downCount++; // 負の変化率
            console.log(`  ${name}: 負の変化率 (${value} < 0) → downCount++`);
        } else {
            this.neutralCount++;
            console.log(`  ${name}: 変化なし (${value} = 0) → neutralCount++`);
        }
    }

    /**
     * カウントをリセット
     */
    resetCounts() {
        this.upCount = 0;
        this.downCount = 0;
        this.neutralCount = 0;
        this.totalCount = 0;
    }

    /**
     * 現在のカウントを取得
     */
    getCounts() {
        return {
            upCount: this.upCount,
            downCount: this.downCount,
            neutralCount: this.neutralCount,
            totalCount: this.totalCount
        };
    }

    /**
     * 結果をログ出力
     */
    logResults() {
        console.log(`=== カウント結果 ===`);
        console.log(`上昇: ${this.upCount}, 下降: ${this.downCount}, 中立: ${this.neutralCount}, 総数: ${this.totalCount}`);
        console.log(`上昇率: ${this.totalCount > 0 ? ((this.upCount / this.totalCount) * 100).toFixed(1) : 0}%`);
        console.log(`下降率: ${this.totalCount > 0 ? ((this.downCount / this.totalCount) * 100).toFixed(1) : 0}%`);
        console.log(`中立率: ${this.totalCount > 0 ? ((this.neutralCount / this.totalCount) * 100).toFixed(1) : 0}%`);
    }
}

// グローバルに公開
window.IndicatorSummaryCalculator = IndicatorSummaryCalculator;
