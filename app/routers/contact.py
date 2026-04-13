"""
联系我们路由 - 处理联系表单提交
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field
import logging

from app.services.email_service import email_service

router = APIRouter(prefix="/contact", tags=["联系我们"])
logger = logging.getLogger(__name__)

# 客服邮箱
SUPPORT_EMAIL = "support@imvu-analytics.com"


# ==================== 请求模型 ====================

class ContactRequest(BaseModel):
    """联系表单请求"""
    name: str = Field(None, max_length=100, description="姓名（可选）")
    email: EmailStr = Field(..., description="邮箱地址（必填）")
    subject: str = Field(..., description="主题（必填）")
    message: str = Field(..., min_length=10, max_length=5000, description="消息内容（必填）")


class ContactResponse(BaseModel):
    """联系表单响应"""
    success: bool
    message: str


# ==================== 页面路由 ====================

@router.get("/", response_class=HTMLResponse)
async def contact_page(request: Request):
    """
    联系我们页面
    无需登录即可访问
    """
    from config import BASE_URL, CANONICAL_URL, APP_NAME, APP_VERSION, DEBUG
    
    page_title = "Contact Us"
    meta_description = "Contact IMVU Analytics support team. Get help with technical issues, account questions, feature suggestions, and subscription inquiries."
    
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - IMVU Analytics</title>
    <meta name="description" content="{meta_description}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{CANONICAL_URL}/contact">
    
    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{page_title} - IMVU Analytics">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:url" content="{CANONICAL_URL}/contact">
    <meta property="og:site_name" content="IMVU Analytics">
    
    <!-- Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <script src="/static/i18n.js"></script>
    
    <style>
        :root {{
            --primary: #667eea;
            --secondary: #764ba2;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 40px 20px;
        }}
        
        .contact-container {{
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .contact-card {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }}
        
        .contact-header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .contact-header h1 {{
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .contact-header p {{
            color: #666;
            font-size: 16px;
        }}
        
        .form-label {{
            font-weight: 500;
            color: #333;
            margin-bottom: 8px;
        }}
        
        .form-control {{
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 15px;
            transition: all 0.3s;
        }}
        
        .form-control:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        }}
        
        .form-select {{
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 15px;
            cursor: pointer;
        }}
        
        .form-select:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        }}
        
        .required-field::after {{
            content: " *";
            color: #dc3545;
        }}
        
        .btn-submit {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            border: none;
            color: white;
            padding: 14px 40px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
        }}
        
        .btn-submit:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
            color: white;
        }}
        
        .btn-submit:disabled {{
            opacity: 0.7;
            transform: none;
        }}
        
        .back-home {{
            text-align: center;
            margin-top: 20px;
        }}
        
        .back-home a {{
            color: white;
            text-decoration: none;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .back-home a:hover {{
            opacity: 1;
            text-decoration: underline;
        }}
        
        .alert-success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
        }}
        
        .alert-error {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
        }}
        
        .lang-switch {{
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 8px;
        }}
        
        .lang-switch button {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        
        .lang-switch button:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .lang-switch button.active {{
            background: white;
            color: var(--primary);
        }}
        
        .brand-title {{
            position: fixed;
            top: 20px;
            left: 30px;
            color: white;
            font-weight: 700;
            font-size: 20px;
        }}
        
        .brand-title span {{
            opacity: 0.9;
            font-size: 14px;
            display: block;
            font-weight: 400;
        }}
    </style>
</head>
<body>
    <div class="brand-title">
        IMVU Analytics
        <span>Data Platform</span>
    </div>
    
    <div class="lang-switch">
        <button class="lang-btn" data-lang="en">EN</button>
        <button class="lang-btn" data-lang="zh">中文</button>
    </div>
    
    <div class="contact-container">
        <div class="contact-card">
            <div class="contact-header">
                <h1 data-i18n="contact.title">Contact Us</h1>
                <p data-i18n="contact.subtitle">We'd love to hear from you. Send us a message and we'll respond as soon as possible.</p>
            </div>
            
            <div id="alert-container"></div>
            
            <form id="contact-form">
                <div class="mb-3">
                    <label class="form-label" data-i18n="contact.name">Name</label>
                    <input type="text" class="form-control" id="name" name="name" 
                           data-i18n-placeholder="contact.namePlaceholder" placeholder="Your name (optional)">
                </div>
                
                <div class="mb-3">
                    <label class="form-label required-field" data-i18n="contact.email">Email</label>
                    <input type="email" class="form-control" id="email" name="email" required
                           data-i18n-placeholder="contact.emailPlaceholder" placeholder="your.email@example.com">
                </div>
                
                <div class="mb-3">
                    <label class="form-label required-field" data-i18n="contact.subject">Subject</label>
                    <select class="form-select" id="subject" name="subject" required>
                        <option value="" data-i18n="contact.selectSubject">Select a subject</option>
                        <option value="technical" data-i18n="contact.subjectTechnical">Technical Support</option>
                        <option value="account" data-i18n="contact.subjectAccount">Account Issues</option>
                        <option value="feature" data-i18n="contact.subjectFeature">Feature Suggestions</option>
                        <option value="subscription" data-i18n="contact.subjectSubscription">Subscription Questions</option>
                        <option value="other" data-i18n="contact.subjectOther">Other</option>
                    </select>
                </div>
                
                <div class="mb-4">
                    <label class="form-label required-field" data-i18n="contact.message">Message</label>
                    <textarea class="form-control" id="message" name="message" rows="5" required
                              data-i18n-placeholder="contact.messagePlaceholder" placeholder="Please describe your question or feedback in detail (minimum 10 characters)"></textarea>
                    <small class="text-muted" data-i18n="contact.messageHint">Minimum 10 characters</small>
                </div>
                
                <button type="submit" class="btn btn-submit" id="submit-btn">
                    <span data-i18n="contact.submit">Send Message</span>
                </button>
            </form>
            
            <div class="back-home">
                <a href="/login" data-i18n="contact.backHome">Back to Login</a>
            </div>
        </div>
    </div>
    
    <script>
        // 表单提交
        document.getElementById('contact-form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const submitBtn = document.getElementById('submit-btn');
            const alertContainer = document.getElementById('alert-container');
            
            // 获取表单数据
            const formData = {{
                name: document.getElementById('name').value.trim(),
                email: document.getElementById('email').value.trim(),
                subject: document.getElementById('subject').value,
                message: document.getElementById('message').value.trim()
            }};
            
            // 验证必填字段
            if (!formData.email) {{
                alertContainer.innerHTML = '<div class="alert-error">' + t('contact.errorEmailRequired') + '</div>';
                return;
            }}
            
            if (!formData.subject) {{
                alertContainer.innerHTML = '<div class="alert-error">' + t('contact.errorSubjectRequired') + '</div>';
                return;
            }}
            
            if (formData.message.length < 10) {{
                alertContainer.innerHTML = '<div class="alert-error">' + t('contact.errorMessageTooShort') + '</div>';
                return;
            }}
            
            // 禁用按钮，显示加载状态
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' + t('contact.sending');
            
            try {{
                const response = await fetch('/api/contact', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(formData)
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    alertContainer.innerHTML = '<div class="alert-success">' + t('contact.success') + '</div>';
                    document.getElementById('contact-form').reset();
                }} else {{
                    alertContainer.innerHTML = '<div class="alert-error">' + result.message + '</div>';
                }}
            }} catch (error) {{
                alertContainer.innerHTML = '<div class="alert-error">' + t('contact.error') + '</div>';
            }} finally {{
                submitBtn.disabled = false;
                submitBtn.innerHTML = t('contact.submit');
            }}
        }});
    </script>
</body>
</html>
""")


# ==================== API路由 ====================

@router.post("/api", response_model=ContactResponse)
async def submit_contact(request: ContactRequest):
    """
    提交联系表单
    
    - **name**: 姓名（可选）
    - **email**: 邮箱地址（必填）
    - **subject**: 主题（必填）
    - **message**: 消息内容（必填，最少10字符）
    """
    try:
        # 主题映射
        subject_map = {
            "technical": "Technical Support",
            "account": "Account Issues", 
            "feature": "Feature Suggestions",
            "subscription": "Subscription Questions",
            "other": "Other"
        }
        
        subject_display = subject_map.get(request.subject, request.subject)
        
        # 构建邮件内容
        email_subject = f"[IMVU Analytics] {subject_display} - from {request.email}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">New Contact Form Submission</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p><strong>Subject:</strong> {subject_display}</p>
                <p><strong>User Email:</strong> <a href="mailto:{request.email}">{request.email}</a></p>
                <p><strong>Name:</strong> {request.name or 'Not provided'}</p>
            </div>
            
            <div style="background: #fff; padding: 20px; border: 1px solid #e9ecef; border-radius: 10px;">
                <h4 style="color: #333; margin-bottom: 15px;">Message:</h4>
                <p style="white-space: pre-wrap; line-height: 1.6;">{request.message}</p>
            </div>
            
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                This message was sent via the IMVU Analytics contact form.
            </p>
        </div>
        """
        
        # 发送邮件
        success, message = email_service.send_contact_email(
            to_email=SUPPORT_EMAIL,
            subject=email_subject,
            html_content=html_content,
            user_email=request.email,
            user_name=request.name
        )
        
        if success:
            return ContactResponse(
                success=True,
                message="Your message has been sent successfully! We'll get back to you soon."
            )
        else:
            return ContactResponse(
                success=False,
                message=f"Failed to send message: {message}"
            )
            
    except Exception as e:
        logger.error(f"Contact form submission error: {e}", exc_info=True)
        return ContactResponse(
            success=False,
            message="An error occurred. Please try again later."
        )
