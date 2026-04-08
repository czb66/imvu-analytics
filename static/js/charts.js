/**
 * 图表配置模块 - 封装常用图表配置
 */

// 默认主题色
const CHART_COLORS = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#52c41a',
    danger: '#ff4d4f',
    warning: '#faad14',
    info: '#1890ff',
    gradients: [
        '#667eea', '#764ba2', '#f093fb', '#f5576c',
        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
    ]
};

// 通用图表选项
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                    family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: { size: 14 },
            bodyFont: { size: 13 },
            cornerRadius: 8
        }
    }
};

// 创建渐变色
function createGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
}

// 柱状图配置
function getBarChartConfig(data, options = {}) {
    return {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: options.label || '数据',
                data: data.values || [],
                backgroundColor: options.colors || CHART_COLORS.gradients,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: '#f0f0f0' }
                }
            },
            ...options.extraOptions
        }
    };
}

// 饼图/环形图配置
function getPieChartConfig(data, options = {}) {
    return {
        type: options.type || 'pie',
        data: {
            labels: data.labels || [],
            datasets: [{
                data: data.values || [],
                backgroundColor: options.colors || CHART_COLORS.gradients,
                borderWidth: 0
            }]
        },
        options: {
            ...commonOptions,
            cutout: options.cutout || '0%',
            plugins: {
                ...commonOptions.plugins,
                legend: {
                    ...commonOptions.plugins.legend,
                    position: options.legendPosition || 'bottom'
                }
            }
        }
    };
}

// 环形图配置
function getDoughnutChartConfig(data, options = {}) {
    return getPieChartConfig(data, { ...options, type: 'doughnut', cutout: '60%' });
}

// 折线图配置
function getLineChartConfig(data, options = {}) {
    return {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: options.label || '数据',
                data: data.values || [],
                borderColor: options.color || CHART_COLORS.primary,
                backgroundColor: options.fill !== false ? `${options.color || CHART_COLORS.primary}20` : 'transparent',
                fill: options.fill !== false,
                tension: options.tension || 0.4,
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                x: { grid: { display: false } },
                y: {
                    beginAtZero: true,
                    grid: { color: '#f0f0f0' }
                }
            }
        }
    };
}

// 多数据集折线图
function getMultiLineChartConfig(data, options = {}) {
    return {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: (data.datasets || []).map((ds, i) => ({
                label: ds.label,
                data: ds.values || [],
                borderColor: ds.color || CHART_COLORS.gradients[i % CHART_COLORS.gradients.length],
                backgroundColor: 'transparent',
                tension: 0.4,
                pointRadius: 3
            }))
        },
        options: {
            ...commonOptions,
            scales: {
                x: { grid: { display: false } },
                y: {
                    beginAtZero: true,
                    grid: { color: '#f0f0f0' }
                }
            }
        }
    };
}

// 雷达图配置
function getRadarChartConfig(data, options = {}) {
    return {
        type: 'radar',
        data: {
            labels: data.labels || [],
            datasets: (data.datasets || []).map((ds, i) => ({
                label: ds.label,
                data: ds.values || [],
                backgroundColor: `${ds.color || CHART_COLORS.gradients[i]}40`,
                borderColor: ds.color || CHART_COLORS.gradients[i],
                pointBackgroundColor: ds.color || CHART_COLORS.gradients[i]
            }))
        },
        options: {
            ...commonOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    grid: { color: '#f0f0f0' },
                    pointLabels: { font: { size: 12 } }
                }
            }
        }
    };
}

// 漏斗图配置
function getFunnelChartConfig(data, options = {}) {
    return {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                data: data.values || [],
                backgroundColor: CHART_COLORS.gradients,
                borderWidth: 0
            }]
        },
        options: {
            ...commonOptions,
            indexAxis: 'y',
            scales: {
                x: { beginAtZero: true, grid: { color: '#f0f0f0' } },
                y: { grid: { display: false } }
            },
            plugins: {
                ...commonOptions.plugins,
                legend: { display: false }
            }
        }
    };
}

// 仪表盘图表配置
function getGaugeChartConfig(value, options = {}) {
    const max = options.max || 100;
    const percent = Math.min(value / max * 100, 100);
    
    return {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [percent, 100 - percent],
                backgroundColor: [
                    options.color || CHART_COLORS.primary,
                    '#f0f0f0'
                ],
                borderWidth: 0
            }]
        },
        options: {
            ...commonOptions,
            cutout: '75%',
            rotation: -90,
            circumference: 180,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    };
}

// 初始化并渲染图表
function initChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, config);
}

// 更新图表数据
function updateChartData(chart, newData) {
    if (!chart) return;
    
    if (newData.labels) {
        chart.data.labels = newData.labels;
    }
    if (newData.values && chart.data.datasets[0]) {
        chart.data.datasets[0].data = newData.values;
    }
    if (newData.datasets) {
        chart.data.datasets = newData.datasets;
    }
    
    chart.update();
}

// 导出图表
function exportChart(chart, filename = 'chart.png') {
    if (!chart) return;
    
    const link = document.createElement('a');
    link.download = filename;
    link.href = chart.toBase64Image('image/png', 1);
    link.click();
}

// 销毁图表
function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CHART_COLORS,
        commonOptions,
        createGradient,
        getBarChartConfig,
        getPieChartConfig,
        getDoughnutChartConfig,
        getLineChartConfig,
        getMultiLineChartConfig,
        getRadarChartConfig,
        getFunnelChartConfig,
        getGaugeChartConfig,
        initChart,
        updateChartData,
        exportChart,
        destroyChart
    };
}
