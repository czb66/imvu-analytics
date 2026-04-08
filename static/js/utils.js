/**
 * 营销数据分析平台 - 通用JavaScript工具
 */

// API基础URL
const API_BASE = '';

// 格式化数字
function formatNumber(num, decimals = 2) {
    if (num === undefined || num === null || isNaN(num)) return '-';
    if (num >= 1000000) return (num / 1000000).toFixed(decimals) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(decimals) + 'K';
    return num.toFixed(decimals);
}

// 格式化金额
function formatCurrency(num) {
    return '¥' + formatNumber(num);
}

// 格式化百分比
function formatPercent(num, decimals = 2) {
    if (num === undefined || num === null || isNaN(num)) return '-';
    return num.toFixed(decimals) + '%';
}

// 格式化日期时间
function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化日期
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('zh-CN');
}

// 显示加载状态
function showLoading(element) {
    element.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner"></div>
            <p class="mt-2 text-muted">加载中...</p>
        </div>
    `;
}

// 显示错误状态
function showError(element, message) {
    element.innerHTML = `
        <div class="alert alert-danger">
            <i class="bi bi-exclamation-triangle"></i>
            ${message || '加载失败'}
        </div>
    `;
}

// 显示空状态
function showEmpty(element, message) {
    element.innerHTML = `
        <div class="text-center py-4 text-muted">
            <i class="bi bi-inbox fs-1"></i>
            <p class="mt-2">${message || '暂无数据'}</p>
        </div>
    `;
}

// 通用API请求
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// 获取仪表盘数据
async function fetchDashboardData() {
    return apiRequest(`${API_BASE}/api/dashboard/summary`);
}

// 获取产品列表
async function fetchProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return apiRequest(`${API_BASE}/api/dashboard/products?${query}`);
}

// 获取Top产品
async function fetchTopProducts(metric = 'profit', limit = 10) {
    return apiRequest(`${API_BASE}/api/dashboard/top-products?metric=${metric}&limit=${limit}`);
}

// 获取诊断报告
async function fetchDiagnosisReport() {
    return apiRequest(`${API_BASE}/api/diagnosis/full-report`);
}

// 导出图表为PNG
function exportChartAsImage(chart, filename = 'chart.png') {
    const link = document.createElement('a');
    link.download = filename;
    link.href = chart.toBase64Image();
    link.click();
}

// 复制文本到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('复制失败:', err);
        return false;
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 表格排序
function sortTable(table, column, direction = 'asc') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.querySelector(`td:nth-child(${column})`).textContent;
        const bVal = b.querySelector(`td:nth-child(${column})`).textContent;
        
        // 尝试数字排序
        const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return direction === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // 字符串排序
        return direction === 'asc' 
            ? aVal.localeCompare(bVal) 
            : bVal.localeCompare(aVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// 颜色工具
const Colors = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#52c41a',
    danger: '#ff4d4f',
    warning: '#faad14',
    info: '#1890ff',
    
    gradients: [
        ['#667eea', '#764ba2'],
        ['#f093fb', '#f5576c'],
        ['#4facfe', '#00f2fe'],
        ['#43e97b', '#38f9d7'],
        ['#fa709a', '#fee140'],
        ['#a8edea', '#fed6e3']
    ],
    
    random() {
        return this.gradients[Math.floor(Math.random() * this.gradients.length)];
    }
};

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatNumber,
        formatCurrency,
        formatPercent,
        formatDateTime,
        formatDate,
        showLoading,
        showError,
        showEmpty,
        apiRequest,
        fetchDashboardData,
        fetchProducts,
        fetchTopProducts,
        fetchDiagnosisReport,
        exportChartAsImage,
        copyToClipboard,
        debounce,
        throttle,
        sortTable,
        Colors
    };
}
