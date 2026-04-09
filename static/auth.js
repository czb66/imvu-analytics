/**
 * 用户认证模块
 * 处理登录状态、Token管理、页面保护
 */

// 获取Token
function getToken() {
    return localStorage.getItem('access_token');
}

// 获取用户信息
function getUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

// 检查是否已登录
function isLoggedIn() {
    return !!getToken();
}

// 获取认证头
function getAuthHeaders() {
    const token = getToken();
    if (token) {
        return {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        };
    }
    return {
        'Content-Type': 'application/json'
    };
}

// 登出
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// 验证Token并获取用户信息
async function validateToken() {
    const token = getToken();
    if (!token) {
        return null;
    }
    
    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                return data.data;
            }
        }
        
        // Token无效，清除
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        return null;
    } catch (e) {
        console.error('Token验证失败:', e);
        return null;
    }
}

// 页面保护：检查登录状态，未登录跳转到登录页
async function protectPage() {
    const user = await validateToken();
    if (!user) {
        window.location.href = '/login';
        return null;
    }
    return user;
}

// 更新导航栏的用户信息
function updateNavbarUser(user) {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay && user) {
        userDisplay.innerHTML = `
            <span class="user-email">${user.email}</span>
            <span class="user-name">${user.username || ''}</span>
            <button class="btn btn-sm btn-outline-light ms-2" onclick="logout()">
                <i class="bi bi-box-arrow-right"></i> <span data-i18n="logout">Logout</span>
            </button>
        `;
    }
}

// API请求封装（带认证）
async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...getAuthHeaders(),
            ...options.headers
        }
    });
    
    // 处理401未授权
    if (response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    
    return response;
}

// 初始化语言
function initLanguage() {
    let lang = localStorage.getItem('language') || 'zh';
    document.documentElement.lang = lang;
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (window.translations && window.translations[lang] && window.translations[lang][key]) {
            el.textContent = window.translations[lang][key];
        }
    });
}

// 多语言翻译
function t(key) {
    const lang = localStorage.getItem('language') || 'zh';
    if (window.translations && window.translations[lang] && window.translations[lang][key]) {
        return window.translations[lang][key];
    }
    return key;
}
