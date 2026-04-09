/**
 * IMVU Analytics Platform - 多语言配置文件
 * 支持中英文切换，默认英文
 */

const translations = {
    en: {
        // 应用名称
        appName: 'IMVU Analytics Platform',
        
        // 导航
        nav: {
            dashboard: 'Dashboard',
            diagnosis: 'Deep Analysis',
            compare: 'Data Compare',
            report: 'Reports'
        },
        
        // 页面标题
        pageTitles: {
            dashboard: 'Data Overview',
            diagnosis: 'Deep Analysis',
            compare: 'Data Compare',
            report: 'Reports Center'
        },
        
        // 仪表盘
        dashboard: {
            uploadTitle: 'Upload XML Data',
            uploadHint: 'Drag file here or click to select',
            selectFile: 'Select File',
            downloadTemplate: 'Download Template',
            uploading: 'Uploading and parsing...',
            uploadSuccess: 'Upload successful!',
            uploadFailed: 'Upload failed',
            
            // 指标卡
            directSales: 'Direct Sales',
            indirectSales: 'Indirect Sales',
            promotedSales: 'Promoted Sales',
            totalSales: 'Total Sales',
            totalProfit: 'Total Profit',
            totalProfitCredits: 'Total Profit (Credits)',
            totalProfitUsd: 'Total Profit (USD)',
            visibleProducts: 'Visible Products',
            hiddenProducts: 'Hidden Products',
            totalProducts: 'Total Products',
            
            // 图表标题
            topProductsBySales: 'Top 10 Products (Sales)',
            visibilityDistribution: 'Visibility Distribution',
            trafficComparison: 'Traffic Comparison',
            priceRangeDistribution: 'Price Range Distribution',
            
            // 产品表格
            productList: 'Product List',
            searchPlaceholder: 'Search by ID or name...',
            productId: 'Product ID',
            productName: 'Product Name',
            price: 'Price',
            profit: 'Profit',
            profitMargin: 'Profit Margin',
            visibility: 'Visibility',
            visible: 'Visible',
            hidden: 'Hidden',
            
            // 图表标签
            sales: 'Sales',
            visibleLabel: 'Visible',
            hiddenLabel: 'Hidden',
            organicTraffic: 'Organic Traffic',
            paidTraffic: 'Paid Traffic',
            
            // 状态消息
            noData: 'No data available',
            loading: 'Loading data...',
            loadingFailed: 'Failed to load data',
            retry: 'Retry',
            requestTimeout: 'Request timeout, please check network',
            items: 'items'
        },
        
        // 深度诊断
        diagnosis: {
            funnelAnalysis: 'Conversion Funnel Analysis',
            impressions: 'Impressions',
            addToCart: 'Add to Cart',
            wishlist: 'Wishlist',
            sales: 'Sales',
            impressionToCart: 'Impression → Cart',
            cartToWishlist: 'Cart → Wishlist',
            wishlistToSales: 'Wishlist → Order',
            
            // 销售诊断
            totalSalesAmount: 'Total Sales Amount',
            totalProfit: 'Total Profit',
            avgProfitMargin: 'Avg Profit Margin',
            
            // 价格区间
            priceRangeAnalysis: 'Price Range Analysis',
            priceRange: 'Price Range',
            productCount: 'Products',
            totalSalesQty: 'Total Sales',
            totalProfitAmount: 'Total Profit',
            avgProfitAmount: 'Avg Profit',
            
            // 流量与ROI
            trafficAnalysis: 'Traffic Analysis',
            roiAnalysis: 'ROI Analysis',
            organicRevenue: 'Organic Revenue',
            paidRevenue: 'Paid Revenue',
            estimatedCost: 'Est. Paid Cost',
            estimatedRoi: 'Est. ROI',
            ratio: 'ratio',
            
            // 用户行为
            userBehavior: 'User Behavior Analysis',
            cartToSalesRate: 'Cart → Order Rate',
            cartToWishlistRate: 'Cart → Wishlist Rate',
            wishlistToSalesRate: 'Wishlist → Order Rate',
            
            // 高利润产品
            highProfitProducts: 'High Profit Products',
            noHighProfitProducts: 'No high profit products',
            
            // 异常检测
            anomalyDetection: 'Anomaly Detection',
            noAnomalyDetected: 'No sales anomalies detected',
            type: 'Type',
            zScore: 'Z-score',
            
            // 低转化预警
            lowConversionAlert: 'Low Conversion Alert',
            noLowConversionAlert: 'No low conversion alerts',
            cartAdds: 'Cart Adds',
            conversionRate: 'Conversion Rate'
        },
        
        // 报告中心
        report: {
            quickActions: 'Quick Actions',
            generateFullReport: 'Generate Full Report',
            viewHtmlReport: 'View HTML Report',
            downloadLatest: 'Download Latest',
            generating: 'Generating report...',
            generationSuccess: 'Report generated successfully!',
            generationFailed: 'Generation failed',
            emailSent: 'Email has been sent.',
            
            customReport: 'Custom Report Settings',
            reportOptions: 'Report Options',
            includeAnomalyDetection: 'Include Anomaly Detection',
            includeTopBottomProducts: 'Include Top/Bottom Products',
            sendEmailNotification: 'Send Email Notification',
            topProductsLimit: 'Top Products Limit',
            emailRecipients: 'Email Recipients (comma separated)',
            generateCustomReport: 'Generate Custom Report',
            
            reportHistory: 'Report History',
            dailyReport: 'Daily Report',
            manualReport: 'Manual Report',
            noReportHistory: 'No report history',
            loading: 'Loading...',
            loadFailed: 'Failed to load',
            status: {
                pending: 'Processing',
                completed: 'Completed',
                failed: 'Failed'
            },
            sentTo: 'Sent to',
            
            scheduledReport: 'Scheduled Report Settings',
            scheduledReportInfo: 'System automatically generates report at UTC 1:00 (Beijing 9:00) and sends to configured email.',
            modifySchedule: 'To modify schedule, edit REPORT_CRON_HOUR and REPORT_CRON_MINUTE in config.py.',
            
            emailConfig: 'Email Configuration',
            configEnvVariables: 'Configure following environment variables to enable email:',
            envVariable: 'Env Variable',
            description: 'Description',
            example: 'Example',
            smtpHost: 'SMTP Server',
            smtpPort: 'SMTP Port',
            smtpUser: 'Sender Email',
            smtpPassword: 'Email Password/App Password',
            emailTo: 'Default Recipient',
            securityTip: 'Security Tip: Do not write passwords in code. Use .env file or environment variables.',
            
            download: 'Download'
        },
        
        // 数据对比
        compare: {
            selectDatasets: 'Select Datasets',
            selectHint: 'Select 2-3 datasets to compare',
            noDatasets: 'No datasets available. Upload data first.',
            uploadData: 'Upload Data',
            runCompare: 'Compare Selected',
            loading: 'Loading...',
            
            // 指标
            metricsComparison: 'Metrics Comparison',
            totalSales: 'Total Sales',
            totalProfit: 'Total Profit',
            totalProducts: 'Total Products',
            visibleProducts: 'Visible Products',
            changeTrend: 'Change Trend',
            sales: 'Sales',
            profit: 'Profit',
            
            // 趋势图表
            salesTrend: 'Sales Trend',
            profitTrend: 'Profit Trend',
            
            // 排名变化
            rankUpProducts: 'Products Moving Up',
            rankDownProducts: 'Products Moving Down',
            newInTop: 'New in Top 10',
            exitedTop: 'Exited Top 10',
            rank: 'rank',
            new: 'NEW',
            exited: 'EXITED',
            noChange: 'No ranking changes',
            noneInTop: 'None',
            
            // 操作
            products: 'products',
            confirmDelete: 'Are you sure you want to delete this dataset?',
            
            // 上传相关
            datasetNamePlaceholder: 'Dataset name (optional, e.g. 2024-01)',
            datasetNameHint: 'Leave empty for default dataset'
        },
        
        // 语言切换
        language: {
            switchTo: 'Switch to',
            current: 'Current'
        }
    },
    
    zh: {
        // 应用名称
        appName: 'IMVU 数据分析平台',
        
        // 导航
        nav: {
            dashboard: '仪表盘',
            diagnosis: '深度诊断',
            compare: '数据对比',
            report: '报告中心'
        },
        
        // 页面标题
        pageTitles: {
            dashboard: '数据概览',
            diagnosis: '深度诊断分析',
            compare: '数据对比',
            report: '报告中心'
        },
        
        // 仪表盘
        dashboard: {
            uploadTitle: '上传XML数据',
            uploadHint: '拖拽文件到此处或点击选择',
            selectFile: '选择文件',
            downloadTemplate: '下载模板',
            uploading: '正在上传和解析...',
            uploadSuccess: '上传成功！',
            uploadFailed: '上传失败',
            
            // 指标卡
            directSales: '直接销售',
            indirectSales: '间接销售',
            promotedSales: '推广销售',
            totalSales: '总销售数量',
            totalProfit: '总利润',
            totalProfitCredits: '总利润 (Credits)',
            totalProfitUsd: '总利润 (USD)',
            visibleProducts: '可见产品',
            hiddenProducts: '隐藏产品',
            totalProducts: '总产品数',
            
            // 图表标题
            topProductsBySales: 'Top 10 产品（销量）',
            visibilityDistribution: '可见性分布',
            trafficComparison: '流量对比',
            priceRangeDistribution: '价格区间分布',
            
            // 产品表格
            productList: '产品列表',
            searchPlaceholder: '搜索产品ID或名称...',
            productId: '产品ID',
            productName: '产品名称',
            price: '价格',
            profit: '利润',
            profitMargin: '利润率',
            visibility: '可见性',
            visible: '可见',
            hidden: '隐藏',
            
            // 图表标签
            sales: '销量',
            visibleLabel: '可见',
            hiddenLabel: '隐藏',
            organicTraffic: '自然流量',
            paidTraffic: '付费流量',
            
            // 状态消息
            noData: '暂无数据',
            loading: '正在加载数据...',
            loadingFailed: '加载数据失败',
            retry: '重试',
            requestTimeout: '请求超时，请检查网络连接',
            items: '个'
        },
        
        // 深度诊断
        diagnosis: {
            funnelAnalysis: '转化漏斗分析',
            impressions: '展示',
            addToCart: '加购',
            wishlist: '收藏',
            sales: '销售',
            impressionToCart: '展示→加购',
            cartToWishlist: '加购→收藏',
            wishlistToSales: '收藏→下单',
            
            // 销售诊断
            totalSalesAmount: '总销售额',
            totalProfit: '总利润',
            avgProfitMargin: '平均利润率',
            
            // 价格区间
            priceRangeAnalysis: '价格区间分析',
            priceRange: '价格区间',
            productCount: '产品数',
            totalSalesQty: '总销量',
            totalProfitAmount: '总利润',
            avgProfitAmount: '平均利润',
            
            // 流量与ROI
            trafficAnalysis: '流量分析',
            roiAnalysis: 'ROI分析',
            organicRevenue: '自然流量收入',
            paidRevenue: '付费流量收入',
            estimatedCost: '预估付费成本',
            estimatedRoi: '预估ROI',
            ratio: '占比',
            
            // 用户行为
            userBehavior: '用户行为分析',
            cartToSalesRate: '加购→下单转化率',
            cartToWishlistRate: '加购→收藏转化率',
            wishlistToSalesRate: '收藏→下单转化率',
            
            // 高利润产品
            highProfitProducts: '高利润产品',
            noHighProfitProducts: '无高利润产品',
            
            // 异常检测
            anomalyDetection: '异常检测',
            noAnomalyDetected: '未检测到销量异常',
            type: '类型',
            zScore: 'Z-score',
            
            // 低转化预警
            lowConversionAlert: '低转化预警',
            noLowConversionAlert: '无低转化预警',
            cartAdds: '加购数',
            conversionRate: '转化率'
        },
        
        // 报告中心
        report: {
            quickActions: '快速操作',
            generateFullReport: '生成完整报告',
            viewHtmlReport: '查看HTML报告',
            downloadLatest: '下载最新报告',
            generating: '正在生成报告...',
            generationSuccess: '报告生成成功！',
            generationFailed: '生成失败',
            emailSent: '邮件已发送。',
            
            customReport: '自定义报告设置',
            reportOptions: '报告选项',
            includeAnomalyDetection: '包含异常检测',
            includeTopBottomProducts: '包含Top/Bottom产品',
            sendEmailNotification: '发送邮件通知',
            topProductsLimit: 'Top产品数量',
            emailRecipients: '邮件收件人（多个用逗号分隔）',
            generateCustomReport: '生成自定义报告',
            
            reportHistory: '报告历史',
            dailyReport: '每日报告',
            manualReport: '手动报告',
            noReportHistory: '暂无报告历史',
            loading: '正在加载...',
            loadFailed: '加载失败',
            status: {
                pending: '处理中',
                completed: '已完成',
                failed: '失败'
            },
            sentTo: '已发送至',
            
            scheduledReport: '定时报告设置',
            scheduledReportInfo: '系统每天 UTC 1:00 (北京时间 9:00) 自动生成报告并发送至配置的邮箱。',
            modifySchedule: '如需修改定时任务时间，请编辑 config.py 中的 REPORT_CRON_HOUR 和 REPORT_CRON_MINUTE 配置。',
            
            emailConfig: '邮件配置说明',
            configEnvVariables: '配置以下环境变量以启用邮件发送功能：',
            envVariable: '环境变量',
            description: '说明',
            example: '示例',
            smtpHost: 'SMTP服务器地址',
            smtpPort: 'SMTP端口',
            smtpUser: '发件人邮箱',
            smtpPassword: '邮箱密码/授权码',
            emailTo: '默认收件人',
            securityTip: '安全提示：请勿将密码直接写入代码，推荐使用 .env 文件或环境变量。',
            
            download: '下载'
        },
        
        // 数据对比
        compare: {
            selectDatasets: '选择数据集',
            selectHint: '选择2-3个数据集进行对比',
            noDatasets: '暂无可用数据集，请先上传数据。',
            uploadData: '上传数据',
            runCompare: '对比所选',
            loading: '加载中...',
            
            // 指标
            metricsComparison: '指标对比',
            totalSales: '总销量',
            totalProfit: '总利润',
            totalProducts: '产品总数',
            visibleProducts: '可见产品',
            changeTrend: '变化趋势',
            sales: '销量',
            profit: '利润',
            
            // 趋势图表
            salesTrend: '销量趋势',
            profitTrend: '利润趋势',
            
            // 排名变化
            rankUpProducts: '排名上升产品',
            rankDownProducts: '排名下降产品',
            newInTop: '新进入Top 10',
            exitedTop: '退出Top 10',
            rank: '名',
            new: '新晋',
            exited: '退出',
            noChange: '无排名变化',
            noneInTop: '无',
            
            // 操作
            products: '个产品',
            confirmDelete: '确定要删除此数据集吗？',
            
            // 上传相关
            datasetNamePlaceholder: '数据集名称（可选，如 2024年1月）',
            datasetNameHint: '留空则使用默认数据集'
        },
        
        // 语言切换
        language: {
            switchTo: '切换到',
            current: '当前'
        }
    }
};

// 当前语言
let currentLang = localStorage.getItem('imvu_lang') || 'en';

/**
 * 获取翻译文本
 * @param {string} key - 翻译键，支持点号分隔的嵌套键，如 'dashboard.directSales'
 * @param {string} lang - 语言，默认为当前语言
 */
function t(key, lang = currentLang) {
    const keys = key.split('.');
    let value = translations[lang] || translations.en;
    
    for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
            value = value[k];
        } else {
            console.warn(`Translation not found: ${key}`);
            return key;
        }
    }
    
    return value;
}

/**
 * 切换语言
 * @param {string} lang - 目标语言
 */
function setLanguage(lang) {
    if (!translations[lang]) {
        console.warn(`Language not supported: ${lang}`);
        return;
    }
    
    currentLang = lang;
    localStorage.setItem('imvu_lang', lang);
    applyTranslations();
    updateLanguageButtons();
    
    // 触发自定义事件，以便页面可以响应语言变化
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
}

/**
 * 应用翻译到页面
 */
function applyTranslations() {
    // 应用 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = t(key);
    });
    
    // 应用 data-i18n-placeholder 属性的元素
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.placeholder = t(key);
    });
    
    // 应用 data-i18n-title 属性的元素
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        el.title = t(key);
    });
    
    // 更新语言切换按钮
    document.querySelectorAll('.lang-btn').forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        if (btnLang === currentLang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

/**
 * 更新语言按钮状态
 */
function updateLanguageButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        if (btnLang === currentLang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

/**
 * 获取当前语言
 */
function getCurrentLanguage() {
    return currentLang;
}

// 立即初始化语言设置（不等待 DOMContentLoaded）
currentLang = localStorage.getItem('imvu_lang') || 'en';

// 页面加载完成后应用翻译
document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
});
