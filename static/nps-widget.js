/**
 * NPS 弹窗组件
 * 用于收集用户满意度和反馈
 */

class NPSWidget {
    constructor(options = {}) {
        this.options = {
            dismissKey: 'nps_dismissed_until',
            dismissDays: 7,
            apiBase: '/api/feedback',
            ...options
        };
        
        this.currentStep = 1;
        this.maxSteps = 3;
        this.npsScore = null;
        this.feedbackType = null;
        this.feedbackContent = '';
        this.modal = null;
        
        this.init();
    }
    
    async init() {
        // 创建弹窗DOM
        this.createModal();
        
        // 检查是否应该显示弹窗
        const shouldShow = await this.checkShouldShow();
        
        if (shouldShow) {
            setTimeout(() => this.show(), 2000); // 延迟2秒显示
        }
    }
    
    createModal() {
        const overlay = document.createElement('div');
        overlay.className = 'nps-modal-overlay';
        overlay.id = 'nps-modal';
        
        overlay.innerHTML = `
            <div class="nps-modal" style="position: relative;">
                <button class="nps-close-btn" onclick="npsWidget.close()">&times;</button>
                
                <div class="nps-progress">
                    <div class="nps-progress-dot active" data-step="1"></div>
                    <div class="nps-progress-dot" data-step="2"></div>
                    <div class="nps-progress-dot" data-step="3"></div>
                </div>
                
                <div class="nps-modal-header">
                    <div class="nps-modal-icon">💬</div>
                    <h3 class="nps-modal-title" data-i18n="nps.title">We'd love your feedback!</h3>
                    <p class="nps-modal-subtitle" data-i18n="nps.subtitle">Help us improve IMVU Analytics</p>
                </div>
                
                <div class="nps-modal-body">
                    <!-- Step 1: Score -->
                    <div class="nps-step active" data-step="1">
                        <div class="nps-score-container">
                            <p class="nps-score-question" data-i18n="nps.scoreQuestion">How likely are you to recommend IMVU Analytics to a friend?</p>
                            <div class="nps-score-labels">
                                <span data-i18n="nps.notLikely">Not likely at all</span>
                                <span data-i18n="nps.veryLikely">Very likely</span>
                            </div>
                            <div class="nps-score-selector">
                                ${[0,1,2,3,4,5,6,7,8,9,10].map(n => 
                                    `<button class="nps-score-btn score-${n}" data-score="${n}">${n}</button>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Step 2: Feedback Type -->
                    <div class="nps-step" data-step="2">
                        <div class="nps-type-container">
                            <p class="nps-type-question" data-i18n="nps.typeQuestion">What type of feedback do you have?</p>
                            <div class="nps-type-grid">
                                <div class="nps-type-btn" data-type="bug">
                                    <div class="nps-type-icon">🐛</div>
                                    <div class="nps-type-label" data-i18n="nps.typeBug">Bug Report</div>
                                    <div class="nps-type-desc" data-i18n="nps.typeBugDesc">Something not working</div>
                                </div>
                                <div class="nps-type-btn" data-type="feature">
                                    <div class="nps-type-icon">✨</div>
                                    <div class="nps-type-label" data-i18n="nps.typeFeature">Feature</div>
                                    <div class="nps-type-desc" data-i18n="nps.typeFeatureDesc">New idea or suggestion</div>
                                </div>
                                <div class="nps-type-btn" data-type="general">
                                    <div class="nps-type-icon">💭</div>
                                    <div class="nps-type-label" data-i18n="nps.typeGeneral">General</div>
                                    <div class="nps-type-desc" data-i18n="nps.typeGeneralDesc">Other thoughts</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Step 3: Feedback Content -->
                    <div class="nps-step" data-step="3">
                        <div class="nps-feedback-container">
                            <p class="nps-feedback-question" data-i18n="nps.feedbackQuestion">What could we do better?</p>
                            <textarea class="nps-feedback-textarea" 
                                      id="nps-feedback-content"
                                      data-i18n-placeholder="nps.feedbackPlaceholder"
                                      placeholder="Share your thoughts (minimum 10 characters)"></textarea>
                            <p class="nps-feedback-hint" data-i18n="nps.feedbackHint">Your feedback helps us improve the product for everyone</p>
                            <p class="nps-feedback-optional" data-i18n="nps.feedbackOptional">This step is optional, you can skip</p>
                        </div>
                    </div>
                    
                    <!-- Thanks -->
                    <div class="nps-step" data-step="thanks">
                        <div class="nps-thanks-container">
                            <div class="nps-thanks-icon">🎉</div>
                            <h3 class="nps-thanks-title" data-i18n="nps.thanksTitle">Thank you!</h3>
                            <p class="nps-thanks-message" data-i18n="nps.thanksMessage">Your feedback is invaluable to us. We'll use it to make IMVU Analytics even better!</p>
                        </div>
                    </div>
                </div>
                
                <div class="nps-modal-footer">
                    <button class="nps-btn nps-btn-secondary" id="nps-prev-btn" style="display: none;" onclick="npsWidget.prevStep()">
                        <span data-i18n="nps.back">Back</span>
                    </button>
                    <button class="nps-btn nps-btn-skip" onclick="npsWidget.skip()">
                        <span data-i18n="nps.skip">Skip</span>
                    </button>
                    <button class="nps-btn nps-btn-primary" id="nps-next-btn" onclick="npsWidget.nextStep()" disabled>
                        <span data-i18n="nps.next">Next</span>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        this.modal = overlay;
        
        // 绑定事件
        this.bindEvents();
    }
    
    bindEvents() {
        // 评分按钮
        document.querySelectorAll('.nps-score-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectScore(parseInt(btn.dataset.score));
            });
        });
        
        // 反馈类型按钮
        document.querySelectorAll('.nps-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectType(btn.dataset.type);
            });
        });
        
        // 反馈内容输入
        const textarea = document.getElementById('nps-feedback-content');
        if (textarea) {
            textarea.addEventListener('input', (e) => {
                this.feedbackContent = e.target.value;
                this.updateNextButton();
            });
        }
        
        // ESC 关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.close();
            }
        });
        
        // 点击遮罩关闭
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
    }
    
    async checkShouldShow() {
        // 检查 localStorage
        const dismissedUntil = localStorage.getItem(this.options.dismissKey);
        if (dismissedUntil) {
            const until = new Date(dismissedUntil);
            if (new Date() < until) {
                return false;
            }
        }
        
        // 检查服务器配置
        try {
            const response = await fetch(`${this.options.apiBase}/nps-widget`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.data && data.data.should_show === true;
            }
        } catch (e) {
            console.log('NPS widget check failed:', e);
        }
        
        return false;
    }
    
    getAuthHeaders() {
        const token = localStorage.getItem('access_token');
        return {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
        };
    }
    
    show() {
        if (!this.modal) return;
        
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.currentStep = 1;
        this.updateUI();
    }
    
    close() {
        if (!this.modal) return;
        
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // 设置7天不显示
        const dismissUntil = new Date();
        dismissUntil.setDate(dismissUntil.getDate() + this.options.dismissDays);
        localStorage.setItem(this.options.dismissKey, dismissUntil.toISOString());
    }
    
    skip() {
        if (this.currentStep < this.maxSteps) {
            // 跳过反馈类型或内容，直接提交
            this.submit();
        } else {
            this.close();
        }
    }
    
    selectScore(score) {
        this.npsScore = score;
        
        // 更新UI
        document.querySelectorAll('.nps-score-btn').forEach(btn => {
            btn.classList.toggle('selected', parseInt(btn.dataset.score) === score);
        });
        
        this.updateNextButton();
    }
    
    selectType(type) {
        this.feedbackType = type;
        
        // 更新UI
        document.querySelectorAll('.nps-type-btn').forEach(btn => {
            btn.classList.toggle('selected', btn.dataset.type === type);
        });
        
        this.updateNextButton();
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateUI();
        }
    }
    
    nextStep() {
        if (this.currentStep < this.maxSteps) {
            this.currentStep++;
            this.updateUI();
        } else {
            this.submit();
        }
    }
    
    updateUI() {
        // 更新步骤显示
        document.querySelectorAll('.nps-step').forEach(step => {
            step.classList.toggle('active', step.dataset.step == this.currentStep);
        });
        
        // 更新进度点
        document.querySelectorAll('.nps-progress-dot').forEach(dot => {
            dot.classList.toggle('active', parseInt(dot.dataset.step) <= this.currentStep);
        });
        
        // 更新按钮
        const prevBtn = document.getElementById('nps-prev-btn');
        const nextBtn = document.getElementById('nps-next-btn');
        const skipBtn = document.querySelector('.nps-btn-skip');
        
        prevBtn.style.display = this.currentStep > 1 ? 'inline-block' : 'none';
        
        if (this.currentStep === this.maxSteps) {
            nextBtn.querySelector('span').dataset.i18n = 'nps.submit';
            nextBtn.querySelector('span').textContent = typeof t !== 'undefined' ? t('nps.submit') : 'Submit';
            skipBtn.style.display = 'inline-block';
        } else {
            nextBtn.querySelector('span').dataset.i18n = 'nps.next';
            nextBtn.querySelector('span').textContent = typeof t !== 'undefined' ? t('nps.next') : 'Next';
            skipBtn.style.display = 'inline-block';
        }
        
        this.updateNextButton();
    }
    
    updateNextButton() {
        const nextBtn = document.getElementById('nps-next-btn');
        let disabled = false;
        
        if (this.currentStep === 1 && this.npsScore === null) {
            disabled = true;
        } else if (this.currentStep === 2 && this.feedbackType === null) {
            disabled = true;
        }
        
        nextBtn.disabled = disabled;
    }
    
    async submit() {
        const nextBtn = document.getElementById('nps-next-btn');
        nextBtn.disabled = true;
        nextBtn.textContent = '...';
        
        try {
            const response = await fetch(`${this.options.apiBase}/submit`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    nps_score: this.npsScore,
                    feedback_type: this.feedbackType,
                    content: this.feedbackContent || null,
                    page_url: window.location.href
                })
            });
            
            if (response.ok) {
                // 显示感谢页
                document.querySelectorAll('.nps-step').forEach(step => {
                    step.classList.remove('active');
                });
                document.querySelector('.nps-step[data-step="thanks"]').classList.add('active');
                document.querySelector('.nps-modal-footer').style.display = 'none';
                document.querySelector('.nps-progress').style.display = 'none';
                
                // 3秒后自动关闭
                setTimeout(() => this.close(), 3000);
            } else {
                const error = await response.json();
                alert(error.message || '提交失败，请重试');
                nextBtn.disabled = false;
                nextBtn.textContent = 'Submit';
            }
        } catch (e) {
            console.error('NPS submit error:', e);
            alert('网络错误，请检查网络连接后重试');
            nextBtn.disabled = false;
            nextBtn.textContent = 'Submit';
        }
    }
}

// 初始化 NPS 组件
let npsWidget = null;

function initNPSWidget() {
    // 检查是否已登录
    const token = localStorage.getItem('access_token');
    if (token && !npsWidget) {
        npsWidget = new NPSWidget();
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNPSWidget);
} else {
    initNPSWidget();
}

// 导出给全局使用
window.NPSWidget = NPSWidget;
