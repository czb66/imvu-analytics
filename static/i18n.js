/**
 * IMVU Analytics Platform - 多语言配置文件
 * 支持中英文切换，默认英文
 */

// 先初始化当前语言
let currentLang = localStorage.getItem('imvu_lang') || 'en';

const translations = {
    en: {
        // 应用名称
        appName: 'IMVU Analytics Platform',
        
        // 导航
        nav: {
            dashboard: 'Dashboard',
            diagnosis: 'Deep Analysis',
            compare: 'Data Compare',
            report: 'Reports',
            profile: 'Profile',
            guide: 'User Guide',
            contact: 'Contact Us',
            subscribe: 'Subscribe',
            login: 'Login',
            register: 'Register',
            logout: 'Logout'
        },
        
        // 联系我们页面
        contact: {
            pageTitle: 'Contact Us',
            title: 'Contact Us',
            subtitle: "We'd love to hear from you. Send us a message and we'll respond as soon as possible.",
            name: 'Name',
            namePlaceholder: 'Your name (optional)',
            email: 'Email',
            emailPlaceholder: 'your.email@example.com',
            subject: 'Subject',
            selectSubject: 'Select a subject',
            subjectTechnical: 'Technical Support',
            subjectAccount: 'Account Issues',
            subjectFeature: 'Feature Suggestions',
            subjectSubscription: 'Subscription Questions',
            subjectOther: 'Other',
            message: 'Message',
            messagePlaceholder: 'Please describe your question or feedback in detail (minimum 10 characters)',
            messageHint: 'Minimum 10 characters',
            submit: 'Send Message',
            sending: 'Sending...',
            success: 'Your message has been sent successfully! We\'ll get back to you soon.',
            error: 'An error occurred. Please try again later.',
            errorEmailRequired: 'Please enter your email address.',
            errorSubjectRequired: 'Please select a subject.',
            errorMessageTooShort: 'Message must be at least 10 characters.',
            backHome: 'Back to Login'
        },
        
        // 使用指南页面
        guide: {
            heroTitle: '📖 IMVU Analytics User Guide',
            heroSubtitle: 'Learn how to use the data analysis tools to boost your IMVU creator revenue',
            quickStart: 'Quick Start',
            step1: { title: 'Register Account', desc: 'Sign up for free to start using basic features. Subscribe to unlock all premium features.' },
            step2: { title: 'Download XML Data', desc: 'Login to your IMVU Creator account, go to Product Stats page, and download your product data XML file.' },
            step3: { title: 'Upload Data', desc: 'Upload the XML file to the platform, the system will automatically parse and generate detailed analysis reports.' },
            step4: { title: 'View Analysis', desc: 'Browse dashboard, deep diagnosis, data comparison and other features to get AI insights and optimization suggestions.' },
            features: 'Core Features',
            feature: {
                upload: 'Data Upload',
                upload1: 'Support XML format IMVU product data',
                upload2: 'Automatically parse product info, sales, profit data',
                upload3: 'Support multiple time period data comparison',
                upload4: 'Secure data storage, view history anytime',
                dashboard: 'Data Dashboard',
                dashboard1: 'Total sales, profit, product count at a glance',
                dashboard2: 'Top product rankings',
                dashboard3: 'Visible/hidden product statistics',
                dashboard4: 'Profit USD conversion display',
                diagnosis: 'Deep Diagnosis',
                diagnosis1: 'Conversion funnel analysis (exposure → cart → favorite → purchase)',
                diagnosis2: 'Sales diagnosis and profit analysis',
                diagnosis3: 'Anomaly detection (Z-score algorithm)',
                diagnosis4: 'SEO product name optimization suggestions',
                ai: 'AI Insights',
                ai1: 'Intelligent analysis based on DeepSeek AI',
                ai2: 'Auto-generate trend insights and optimization suggestions',
                ai3: 'Product name SEO optimization analysis',
                ai4: 'Support bilingual output (Chinese/English)',
                compare: 'Data Comparison',
                compare1: 'Multi-period data comparison analysis',
                compare2: 'Product ranking change tracking',
                compare3: 'Sales, profit trend analysis',
                compare4: 'AI comparison insight reports',
                report: 'Report Generation',
                report1: 'Generate detailed data analysis reports',
                report2: 'Support PDF export',
                report3: 'View historical reports anytime',
                report4: 'Email report subscription (optional)'
            },
            dataFormat: 'Data Format',
            howToDownload: 'How to Get Data File',
            howToDownloadDesc: 'Follow these steps to download product data from IMVU Creator dashboard:',
            downloadStep1: 'Login to IMVU Creator account',
            downloadStep2: 'Go to Products → Product Stats page',
            downloadStep3: 'Select the time range to analyze',
            downloadStep4: 'Click "Export to XML" to download file',
            xmlFields: 'XML File Data Fields:',
            seoGuide: 'SEO Optimization Guide',
            seoTips: 'Product Name Optimization Tips',
            seoTipsDesc: 'A good product name can significantly improve search exposure. Here are optimization tips:',
            seoBestPractices: 'Best Practices:',
            seoTip1: 'Use descriptive keywords: include product type, style, color, etc.',
            seoTip2: 'Structured naming: [Style/Theme] + [Product Type] + [Key Features]',
            seoTip3: 'Control length: 3-8 effective words recommended',
            seoTip4: 'Avoid meaningless characters: do not use pure numbers or default names',
            seoAvoid: 'Avoid These Issues:',
            seoAvoid1: '❌ Pure number names (like "Product 123")',
            seoAvoid2: '❌ Overly long names (over 100 characters will be truncated)',
            seoAvoid3: '❌ Keyword stuffing',
            seoAvoid4: '❌ Names unrelated to product content',
            seoAiHint: 'Smart SEO Analysis',
            seoAiHintDesc: 'Use the "Deep Diagnosis" feature, AI will automatically analyze your product names and provide specific SEO optimization suggestions.',
            pricing: 'Subscription Plans',
            faq: 'FAQ'
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
            items: 'items',
            
            // 数据集命名
            datasetNamePlaceholder: 'Dataset name (optional, e.g. 2024-01)',
            datasetNameHint: 'Leave empty for default dataset'
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
            selectHint: 'Select 2-10 datasets to compare',
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
            
            // Top 10 产品对比
            topProductsComparison: 'Top 10 Products Comparison',
            rankingImproved: 'Ranking Improved',
            rankingDeclined: 'Ranking Declined',
            newEntries: 'New Entries',
            droppedOut: 'Dropped Out',
            productName: 'Product Name',
            oldRank: 'Old Rank',
            newRank: 'New Rank',
            change: 'Change',
            
            // 操作
            products: 'products',
            confirmDelete: 'Are you sure you want to delete this dataset?'
        },
        
        // AI洞察
        insights: {
            pageTitle: 'AI Insights',
            dashboard: {
                title: 'AI Data Insights'
            },
            diagnosis: {
                title: 'AI Diagnostic Insights'
            },
            compare: {
                title: 'AI Comparison Insights'
            },
            quickAnalysis: 'Quick Analysis',
            salesTrends: 'Sales Trends Analysis',
            profitOptimization: 'Profit Optimization',
            productRecommendations: 'Product Recommendations',
            suggestedQuestions: 'Suggested Questions',
            q1: 'Top 5 best-selling products',
            q2: 'Products with highest profit margin',
            q3: 'Marketing strategy suggestions',
            aiChat: 'AI Assistant',
            welcome: "Hello! I\'m your AI assistant. Ask me anything about your marketing data.",
            askPlaceholder: 'Ask about your data...',
            apiKeyRequired: 'DeepSeek API Key is required. Please configure it in Settings.',
            generate: 'Generate AI Insights',
            refresh: 'Refresh Insights',
            generating: 'Generating AI insights...',
            configHint: 'Configure DeepSeek API Key for smarter analysis. Go to',
            settings: 'Settings Page',
            loadError: 'Failed to load, please try again later',
            seo: {
                title: 'Product Name SEO Analysis',
                generate: 'Analyze Product Names',
                analyzing: 'Analyzing product names...'
            },
            offlineMode: 'Offline Mode',
            noData: 'No data available. Please upload product data first.',
            selectDatasets: 'Please select at least 2 datasets to compare',
            insufficientData: 'Insufficient valid datasets for comparison',
            generatingFailed: 'Failed to generate insights',
            retry: 'Retry',
            analyzing: 'Analyzing your data...',
            error: 'An error occurred. Please try again.'
        },

        // 上传页面
        upload: {
            dataFormat: 'Data Format Requirements',
            formatXml: 'XML format file',
            maxSize: 'Maximum file size: 50MB',
            requiredFields: 'Required fields: Product Id, Product Name, Wholesale Price, Profit',
            invalidFormat: 'Please upload an XML file.',
            uploadSuccess: 'Data uploaded successfully!',
            uploadError: 'Upload failed. Please try again.',
            processing: 'Processing data...'
        },
        
        // 设置页面
        settings: {
            nav: 'Settings',
            pageTitle: 'Settings',
            systemInfo: 'System Information',
            apiNote: 'AI features (DeepSeek) are configured by the server administrator. API Key is not exposed to users for security reasons.'
        },
        
        // 个人中心
        profile: {
            pageTitle: 'Personal Center',
            userInfo: 'User Information',
            email: 'Email',
            username: 'Username',
            memberSince: 'Member Since',
            subscription: 'Subscription',
            subscriptionStatus: 'Status',
            subscriptionEndDate: 'End Date',
            notSubscribed: 'Not Subscribed',
            subscribed: 'Subscribed',
            updateUsername: 'Update Username',
            newUsername: 'New Username',
            usernamePlaceholder: 'Enter new username (optional)',
            usernameHint: 'Leave empty to remove username',
            saveUsername: 'Save Username',
            changePassword: 'Change Password',
            oldPassword: 'Current Password',
            oldPasswordPlaceholder: 'Enter current password',
            newPassword: 'New Password',
            newPasswordPlaceholder: 'Enter new password (min 8 characters)',
            confirmPassword: 'Confirm Password',
            confirmPasswordPlaceholder: 'Confirm new password',
            passwordHint: 'Password must be at least 8 characters',
            changePasswordBtn: 'Change Password',
            logout: 'Logout',
            logoutHint: 'Click the button below to safely logout of your account.',
            logoutBtn: 'Logout',
            loading: 'Loading...',
            updateSuccess: 'Update successful!',
            updateFailed: 'Update failed. Please try again.',
            passwordChangeSuccess: 'Password changed successfully!',
            passwordChangeFailed: 'Password change failed. Please try again.',
            passwordMinLength: 'Password must be at least 8 characters.',
            passwordMismatch: 'New passwords do not match.'
        },
        
        // 语言切换
        language: {
            switchTo: 'Switch to',
            current: 'Current'
        },

        // 注册页面
        register: {
            pageTitle: 'Register - IMVU Analytics',
            subtitle: 'Create your account',
            email: 'Email',
            username: 'Username (optional)',
            usernamePlaceholder: 'Username (optional)',
            password: 'Password',
            confirmPassword: 'Confirm Password',
            passwordReq: 'Password must be at least 8 characters',
            registerBtn: 'Register',
            hasAccount: 'Already have an account?',
            loginLink: 'Login now',
            // 表单验证消息
            registerSuccess: 'Registration successful! Redirecting to login...',
            registerError: 'Registration failed. Please try again.',
            emailUsed: 'This email is already registered',
            invalidEmail: 'Please enter a valid email address',
            passwordMismatch: 'Passwords do not match',
            passwordShort: 'Password must be at least 8 characters',
            // 密码强度
            weak: 'Weak',
            medium: 'Medium',
            strong: 'Strong',
            veryStrong: 'Very Strong'
        },

        // 登录页面
        login: {
            pageTitle: 'Login - IMVU Analytics',
            welcomeBack: 'Welcome Back',
            subtitle: 'Sign in to your account',
            email: 'Email',
            password: 'Password',
            rememberMe: 'Remember me',
            forgotPassword: 'Forgot password?',
            loginBtn: 'Login',
            noAccount: "Don't have an account?",
            registerLink: 'Register now',
            // 表单验证消息
            loginSuccess: 'Login successful! Redirecting...',
            loginError: 'Login failed. Please check your credentials.',
            invalidEmail: 'Please enter a valid email address',
            passwordRequired: 'Password is required'
        },

        // 忘记密码页面
        forgotPassword: {
            pageTitle: 'Forgot Password - IMVU Analytics',
            title: 'Forgot Password',
            description: 'Enter your registered email, we will send a password reset link',
            email: 'Email',
            sendResetLink: 'Send Reset Link',
            backToLogin: 'Back to Login',
            // 表单验证消息
            invalidEmail: 'Please enter a valid email address',
            emailRequired: 'Email is required',
            sending: 'Sending...',
            sendSuccess: 'If this email is registered, a reset link has been sent. Please check your spam folder.',
            sendError: 'Failed to send email. Please try again later.'
        },

        // 重置密码页面
        resetPassword: {
            pageTitle: 'Reset Password - IMVU Analytics',
            title: 'Reset Password',
            enterNewPassword: 'Please enter your new password',
            newPassword: 'New Password',
            confirmPassword: 'Confirm Password',
            passwordsMatch: 'Passwords match',
            passwordsMismatch: 'Passwords do not match',
            passwordHint: 'Password must be at least 8 characters',
            resetBtn: 'Reset Password',
            backToLogin: 'Back to Login',
            validatingToken: 'Validating link...',
            // 表单验证消息
            passwordRequired: 'Password is required',
            passwordTooShort: 'Password must be at least 8 characters',
            passwordsNotMatch: 'Passwords do not match',
            resetSuccess: 'Password reset successfully! Redirecting to login...',
            resetError: 'Failed to reset password. The link may have expired.',
            invalidToken: 'Invalid or expired reset link'
        },

        // 公共翻译
        common: {
            loading: 'Loading...',
            error: 'Error',
            success: 'Success',
            confirm: 'Confirm',
            cancel: 'Cancel',
            close: 'Close',
            submit: 'Submit',
            save: 'Save',
            delete: 'Delete',
            edit: 'Edit',
            view: 'View',
            back: 'Back',
            next: 'Next',
            previous: 'Previous',
            yes: 'Yes',
            no: 'No'
        },

        // 取消页面
        cancel: {
            pageTitle: 'Account Cancelled',
            title: 'Account Cancelled',
            description: 'Your account has been successfully cancelled.',
            message: 'We\'re sorry to see you go. If you wish to rejoin, you can register again at any time.',
            returnHome: 'Return to Home',
            registerAgain: 'Register Again'
        },

        // 成功页面
        success: {
            pageTitle: 'Success',
            title: 'Success!',
            message: 'Your operation was completed successfully.',
            continueText: 'Continue',
            returnHome: 'Return to Home'
        },

        // 定价页面
        pricing: {
            pageTitle: 'Pricing - IMVU Analytics',
            title: 'Simple, Transparent Pricing',
            subtitle: 'One plan, all features, no hidden fees',
            // 计划名称
            free: 'Free',
            pro: 'Pro',
            enterprise: 'Enterprise',
            // 计划描述
            freeDesc: 'Perfect for getting started',
            proDesc: 'For growing businesses',
            enterpriseDesc: 'For large organizations',
            // 功能列表
            compare1: 'Data Upload',
            compare2: 'Basic Dashboard',
            compare3: 'Data Diagnosis',
            compare4: 'AI Insights',
            compare5: 'Email Reports',
            subscribe_btn: 'Subscribe Now - $12/month',
            manage: 'Manage Subscription',
            current_plan: 'Current Plan',
            renews_at: 'Renews at',
            subscribe_success: 'Redirecting to payment...',
            subscribe_error: 'Failed to create checkout session',
            not_logged_in: 'Please login first',
            network_error: 'Network error, please try again',
            // 功能
            features: {
                uploads: 'Monthly Uploads',
                products: 'Products per Upload',
                datasets: 'Historical Datasets',
                aiInsights: 'AI Insights',
                reports: 'Report Generation',
                emailReports: 'Email Reports',
                support: 'Priority Support',
                customBranding: 'Custom Branding'
            },
            // 功能限制
            unlimited: 'Unlimited',
            notIncluded: 'Not Included',
            // CTA按钮
            getStarted: 'Get Started',
            upgrade: 'Upgrade Now',
            contactSales: 'Contact Sales',
            currentPlan: 'Current Plan'
        },

        // 公共翻译
        common: {
            loading: 'Loading...',
            error: 'Error',
            success: 'Success',
            confirm: 'Confirm',
            cancel: 'Cancel',
            close: 'Close',
            submit: 'Submit',
            save: 'Save',
            delete: 'Delete',
            edit: 'Edit',
            view: 'View',
            back: 'Back',
            next: 'Next',
            previous: 'Previous',
            yes: 'Yes',
            no: 'No'
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
            report: '报告中心',
            profile: '个人中心',
            guide: '使用指南',
            contact: '联系我们',
            subscribe: '订阅',
            login: '登录',
            register: '注册',
            logout: '退出登录'
        },
        
        // 联系我们页面
        contact: {
            pageTitle: '联系我们',
            title: '联系我们',
            subtitle: '我们很乐意收到您的来信。请发送消息，我们会尽快回复。',
            name: '姓名',
            namePlaceholder: '您的姓名（可选）',
            email: '邮箱',
            emailPlaceholder: 'your.email@example.com',
            subject: '主题',
            selectSubject: '请选择主题',
            subjectTechnical: '技术支持',
            subjectAccount: '账户问题',
            subjectFeature: '功能建议',
            subjectSubscription: '订阅问题',
            subjectOther: '其他',
            message: '消息内容',
            messagePlaceholder: '请详细描述您的问题或反馈（至少10个字符）',
            messageHint: '至少10个字符',
            submit: '发送消息',
            sending: '发送中...',
            success: '消息发送成功！我们会尽快回复您。',
            error: '发生错误，请稍后重试。',
            errorEmailRequired: '请输入您的邮箱地址。',
            errorSubjectRequired: '请选择主题。',
            errorMessageTooShort: '消息内容至少需要10个字符。',
            backHome: '返回登录'
        },
        
        // 使用指南页面
        guide: {
            heroTitle: '📖 IMVU Analytics 使用指南',
            heroSubtitle: '全面了解如何使用数据分析工具提升您的 IMVU 创作收益',
            quickStart: '快速开始',
            step1: { title: '注册账户', desc: '免费注册账户，即可开始使用基础功能。订阅后解锁全部高级功能。' },
            step2: { title: '下载 XML 数据', desc: '登录 IMVU Creator 账户，进入 Product Stats 页面，下载您的产品数据 XML 文件。' },
            step3: { title: '上传数据', desc: '将 XML 文件上传到平台，系统会自动解析并生成详细的数据分析报告。' },
            step4: { title: '查看分析', desc: '浏览仪表盘、深度诊断、数据对比等功能，获取 AI 智能洞察和优化建议。' },
            features: '核心功能',
            feature: {
                upload: '数据上传',
                upload1: '支持 XML 格式的 IMVU 产品数据',
                upload2: '自动解析产品信息、销量、利润等数据',
                upload3: '支持多个时间段的数据对比',
                upload4: '数据安全存储，随时查看历史记录',
                dashboard: '数据仪表盘',
                dashboard1: '总销量、总利润、产品数量一目了然',
                dashboard2: 'Top 产品排行榜',
                dashboard3: '可见/隐藏产品统计',
                dashboard4: '利润 USD 换算显示',
                diagnosis: '深度诊断',
                diagnosis1: '转化漏斗分析（曝光→加购→收藏→购买）',
                diagnosis2: '销售诊断与利润分析',
                diagnosis3: '异常产品检测（Z-score 算法）',
                diagnosis4: 'SEO 产品名称优化建议',
                ai: 'AI 智能洞察',
                ai1: '基于 DeepSeek AI 的智能分析',
                ai2: '自动生成趋势洞察和优化建议',
                ai3: '产品名称 SEO 优化分析',
                ai4: '支持中英文双语输出',
                compare: '数据对比',
                compare1: '多时间段数据对比分析',
                compare2: '产品排名变化追踪',
                compare3: '销量、利润趋势分析',
                compare4: 'AI 对比洞察报告',
                report: '报告生成',
                report1: '生成详细的数据分析报告',
                report2: '支持 PDF 导出',
                report3: '历史报告随时查看',
                report4: '邮件报告订阅（可选）'
            },
            dataFormat: '数据格式说明',
            howToDownload: '如何获取数据文件',
            howToDownloadDesc: '请按以下步骤从 IMVU Creator 后台下载产品数据：',
            downloadStep1: '登录 IMVU Creator 账户',
            downloadStep2: '进入 Products → Product Stats 页面',
            downloadStep3: '选择需要分析的时间范围',
            downloadStep4: '点击 "Export to XML" 下载文件',
            xmlFields: 'XML 文件包含的数据字段：',
            seoGuide: 'SEO 优化指南',
            seoTips: '产品名称优化建议',
            seoTipsDesc: '好的产品名称可以显著提高搜索曝光率。以下是优化建议：',
            seoBestPractices: '最佳实践：',
            seoTip1: '使用描述性关键词：包含产品类型、风格、颜色等',
            seoTip2: '结构化命名：[风格/主题] + [产品类型] + [关键特征]',
            seoTip3: '控制长度：3-8 个有效词汇为宜',
            seoTip4: '避免无意义字符：不要使用纯数字或默认名称',
            seoAvoid: '避免的问题：',
            seoAvoid1: '❌ 纯数字名称（如 "Product 123"）',
            seoAvoid2: '❌ 过长的名称（超过 100 字符会被截断）',
            seoAvoid3: '❌ 关键词堆砌',
            seoAvoid4: '❌ 与产品内容无关的名称',
            seoAiHint: '智能 SEO 分析',
            seoAiHintDesc: '使用平台的「深度诊断」功能，AI 会自动分析您的产品名称并给出具体的 SEO 优化建议。',
            pricing: '订阅方案',
            faq: '常见问题'
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
            items: '个',
            
            // 数据集命名
            datasetNamePlaceholder: '数据集名称（可选，如 2024年1月）',
            datasetNameHint: '留空则使用默认数据集'
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
            selectHint: '选择2-10个数据集进行对比',
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
            
            // Top 10 产品对比
            topProductsComparison: 'Top 10 产品排名对比',
            rankingImproved: '排名上升',
            rankingDeclined: '排名下降',
            newEntries: '新进入',
            droppedOut: '退出 Top 10',
            productName: '产品名称',
            oldRank: '原排名',
            newRank: '新排名',
            change: '变化',
            
            // 操作
            products: '个产品',
            confirmDelete: '确定要删除此数据集吗？'
        },
        
        // AI洞察
        insights: {
            pageTitle: 'AI洞察',
            dashboard: {
                title: 'AI 数据洞察'
            },
            diagnosis: {
                title: 'AI 诊断洞察'
            },
            compare: {
                title: 'AI 对比洞察'
            },
            quickAnalysis: '快速分析',
            salesTrends: '销售趋势分析',
            profitOptimization: '利润优化建议',
            productRecommendations: '产品推荐',
            suggestedQuestions: '推荐问题',
            q1: '最畅销的5个产品',
            q2: '利润率最高的产品',
            q3: '营销策略建议',
            aiChat: 'AI助手',
            welcome: '您好！我是您的AI助手，可以询问任何关于营销数据的问题。',
            askPlaceholder: '询问关于您的数据...',
            apiKeyRequired: '需要配置DeepSeek API Key，请在设置页面配置。',
            generate: '生成AI洞察',
            refresh: '刷新洞察',
            generating: '正在生成AI洞察...',
            configHint: '配置 DeepSeek API Key 可获得更智能的分析。前往',
            settings: '设置页面',
            loadError: '加载失败，请稍后重试',
            seo: {
                title: '产品名称 SEO 分析',
                generate: '分析产品名称',
                analyzing: '正在分析产品名称...'
            },
            offlineMode: '离线模式',
            noData: '暂无数据可分析，请先上传产品数据。',
            selectDatasets: '请至少选择2个数据集进行对比',
            insufficientData: '有效数据集不足，无法进行对比',
            generatingFailed: '生成洞察失败',
            retry: '重试',
            analyzing: '正在分析您的数据...',
            error: '发生错误，请重试。'
        },

        // 上传页面
        upload: {
            dataFormat: '数据格式要求',
            formatXml: 'XML格式文件',
            maxSize: '最大文件大小：50MB',
            requiredFields: '必填字段：产品ID、产品名称、批发价、利润',
            invalidFormat: '请上传XML文件。',
            uploadSuccess: '数据上传成功！',
            uploadError: '上传失败，请重试。',
            processing: '正在处理数据...'
        },
        
        // 设置页面
        settings: {
            nav: '设置',
            pageTitle: '设置',
            systemInfo: '系统信息',
            apiNote: 'AI 功能（DeepSeek）由服务器管理员统一配置。为了安全起见，API Key 不会暴露给用户。'
        },
        
        // 个人中心
        profile: {
            pageTitle: '个人中心',
            userInfo: '用户信息',
            email: '邮箱',
            username: '用户名',
            memberSince: '注册时间',
            subscription: '订阅信息',
            subscriptionStatus: '订阅状态',
            subscriptionEndDate: '到期时间',
            notSubscribed: '未订阅',
            subscribed: '已订阅',
            updateUsername: '修改用户名',
            newUsername: '新用户名',
            usernamePlaceholder: '输入新用户名（可选）',
            usernameHint: '留空可移除用户名',
            saveUsername: '保存用户名',
            changePassword: '修改密码',
            oldPassword: '当前密码',
            oldPasswordPlaceholder: '输入当前密码',
            newPassword: '新密码',
            newPasswordPlaceholder: '输入新密码（至少8位）',
            confirmPassword: '确认密码',
            confirmPasswordPlaceholder: '再次输入新密码',
            passwordHint: '密码长度至少8位',
            changePasswordBtn: '修改密码',
            logout: '退出登录',
            logoutHint: '点击下方按钮安全退出账号',
            logoutBtn: '退出登录',
            loading: '加载中...',
            updateSuccess: '更新成功！',
            updateFailed: '更新失败，请重试。',
            passwordChangeSuccess: '密码修改成功！',
            passwordChangeFailed: '密码修改失败，请重试。',
            passwordMinLength: '密码长度至少8位',
            passwordMismatch: '两次输入的密码不一致'
        },
        
        // 语言切换
        language: {
            switchTo: '切换到',
            current: '当前'
        },

        // 注册页面
        register: {
            pageTitle: '注册 - IMVU Analytics',
            subtitle: '创建您的账户',
            email: '邮箱',
            username: '用户名',
            usernamePlaceholder: '用户名（可选）',
            password: '密码',
            confirmPassword: '确认密码',
            passwordReq: '密码长度至少8位',
            registerBtn: '注册',
            hasAccount: '已有账号？',
            loginLink: '立即登录',
            // 表单验证消息
            registerSuccess: '注册成功！正在跳转登录...',
            registerError: '注册失败，请重试。',
            emailUsed: '该邮箱已被注册',
            invalidEmail: '请输入有效的邮箱地址',
            passwordMismatch: '两次输入的密码不一致',
            passwordShort: '密码长度至少8位',
            // 密码强度
            weak: '弱',
            medium: '中等',
            strong: '强',
            veryStrong: '非常强'
        },

        // 登录页面
        login: {
            pageTitle: '登录 - IMVU Analytics',
            welcomeBack: '欢迎回来',
            subtitle: '登录您的账号',
            email: '邮箱',
            password: '密码',
            rememberMe: '记住我',
            forgotPassword: '忘记密码？',
            loginBtn: '登录',
            noAccount: '还没有账号？',
            registerLink: '立即注册',
            // 表单验证消息
            loginSuccess: '登录成功！正在跳转...',
            loginError: '登录失败，请检查邮箱和密码。',
            invalidEmail: '请输入有效的邮箱地址',
            passwordRequired: '请输入密码'
        },

        // 忘记密码页面
        forgotPassword: {
            pageTitle: '忘记密码 - IMVU Analytics',
            title: '忘记密码',
            description: '输入您的注册邮箱，我们将发送密码重置链接',
            email: '邮箱',
            sendResetLink: '发送重置链接',
            backToLogin: '返回登录',
            // 表单验证消息
            invalidEmail: '请输入有效的邮箱地址',
            emailRequired: '请输入邮箱',
            sending: '发送中...',
            sendSuccess: '如果该邮箱已注册，重置链接已发送至您的邮箱，请检查垃圾邮件文件夹。',
            sendError: '邮件发送失败，请稍后重试。'
        },

        // 重置密码页面
        resetPassword: {
            pageTitle: '重置密码 - IMVU Analytics',
            title: '重置密码',
            enterNewPassword: '请输入您的新密码',
            newPassword: '新密码',
            confirmPassword: '确认密码',
            passwordsMatch: '两次输入的密码一致',
            passwordsMismatch: '两次输入的密码不一致',
            passwordHint: '密码至少8个字符',
            resetBtn: '重置密码',
            backToLogin: '返回登录',
            validatingToken: '正在验证链接...',
            // 表单验证消息
            passwordRequired: '请输入密码',
            passwordTooShort: '密码长度至少8位',
            passwordsNotMatch: '两次输入的密码不一致',
            resetSuccess: '密码重置成功！正在跳转至登录页面...',
            resetError: '密码重置失败，链接可能已过期。',
            invalidToken: '重置链接无效或已过期'
        },

        // 公共翻译
        common: {
            loading: '加载中...',
            error: '错误',
            success: '成功',
            confirm: '确认',
            cancel: '取消',
            close: '关闭',
            submit: '提交',
            save: '保存',
            delete: '删除',
            edit: '编辑',
            view: '查看',
            back: '返回',
            next: '下一步',
            previous: '上一步',
            yes: '是',
            no: '否'
        },

        // 取消页面
        cancel: {
            pageTitle: '账号已注销',
            title: '账号已注销',
            description: '您的账号已成功注销。',
            message: '很遗憾看到您离开。如需重新加入，您可以随时再次注册。',
            returnHome: '返回首页',
            registerAgain: '重新注册'
        },

        // 成功页面
        success: {
            pageTitle: '成功',
            title: '成功！',
            message: '您的操作已成功完成。',
            continueText: '继续',
            returnHome: '返回首页'
        },

        // 定价页面
        pricing: {
            pageTitle: '定价 - IMVU Analytics',
            title: '简单、透明的定价',
            subtitle: '一个计划，所有功能，无隐藏费用',
            // 计划名称
            free: '免费版',
            pro: '专业版',
            enterprise: '企业版',
            // 计划描述
            freeDesc: '非常适合入门',
            proDesc: '适合成长型企业',
            enterpriseDesc: '适合大型组织',
            // 功能列表
            compare1: '数据上传',
            compare2: '基础仪表板',
            compare3: '数据诊断',
            compare4: 'AI洞察',
            compare5: '邮件报告',
            subscribe_btn: '立即订阅 - $12/月',
            manage: '管理订阅',
            current_plan: '当前计划',
            renews_at: '续费日期',
            subscribe_success: '正在跳转到支付页面...',
            subscribe_error: '创建支付会话失败',
            not_logged_in: '请先登录',
            network_error: '网络错误，请重试',
            // 功能
            features: {
                uploads: '每月上传次数',
                products: '每次上传产品数',
                datasets: '历史数据集',
                aiInsights: 'AI洞察',
                reports: '报告生成',
                emailReports: '邮件报告',
                support: '优先支持',
                customBranding: '自定义品牌'
            },
            // 功能限制
            unlimited: '无限制',
            notIncluded: '不包含',
            // CTA按钮
            getStarted: '开始使用',
            upgrade: '立即升级',
            contactSales: '联系销售',
            currentPlan: '当前计划'
        }
    }
};

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
 * 更新页面翻译（applyTranslations 的别名）
 */
function updateLanguage() {
    applyTranslations();
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

/**
 * 获取当前语言 (别名函数)
 * 与 getCurrentLanguage() 功能相同，提供更简洁的函数名供页面调用
 */
function getLanguage() {
    return currentLang;
}

// 页面加载完成后应用翻译
document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
});

// 导出到全局作用域，供 HTML 页面使用
window.t = t;
window.setLanguage = setLanguage;
window.updateLanguage = updateLanguage;
window.getCurrentLanguage = getCurrentLanguage;
window.getLanguage = getLanguage;
