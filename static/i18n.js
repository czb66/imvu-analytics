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
            faq: 'FAQ',
            faq1: {
                q: 'Is my data secure?',
                a: 'Yes, data security is our top priority. All data transfers use HTTPS encryption, and data is stored on secure cloud servers. Your product data is used only for analysis and is never shared with third parties.'
            },
            faq2: {
                q: 'What data formats are supported?',
                a: 'Currently only XML format files exported from IMVU Creator dashboard are supported. This is the official product statistics format provided by IMVU, containing complete product information and sales data.'
            },
            faq3: {
                q: 'Does AI Insights require extra payment?',
                a: 'AI Insights is included in the Pro subscription at no extra cost. After subscribing, you can use AI analysis features unlimited times, including data insights, SEO analysis, comparison analysis, and more.'
            },
            faq4: {
                q: 'How do I cancel my subscription?',
                a: 'You can manage your subscription anytime in the "Profile" page. Click "Manage Subscription" to access the Stripe customer portal and cancel. After cancellation, you can continue using the service until the current billing period ends.'
            },
            faq5: {
                q: 'How long is my data stored?',
                a: 'Uploaded data is stored in your account indefinitely. You can view historical data and generate comparison reports anytime. To delete data, manually remove specific datasets from the dashboard.'
            },
            faq6: {
                q: 'Can I get a refund?',
                a: 'We do not offer refunds for partial months. However, you can cancel anytime and continue using the service until your billing period ends. No additional charges will be made after cancellation.'
            },
            faq7: {
                q: 'What AI technology is used?',
                a: 'We use DeepSeek AI for intelligent analysis. It automatically generates trend insights, SEO optimization suggestions, and data comparison reports. Supports bilingual output in Chinese and English.'
            },
            faq8: {
                q: 'How accurate is the analysis?',
                a: 'Data parsing is 100% accurate based on IMVU official XML format. AI insights provide trend analysis and optimization suggestions based on your actual data. Results may vary depending on data quality.'
            },
            ctaTitle: 'Ready to Boost Your IMVU Creator Revenue?',
            ctaBtn: 'Get Started Free'
        },
        
        // Privacy Policy page
        privacy: {
            title: 'Privacy Policy',
            subtitle: 'How we collect, use and protect your data',
            section1: {
                title: '1. Introduction',
                content: 'IMVU Analytics ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our data analytics platform.'
            },
            section2: {
                title: '2. Information We Collect',
                intro: 'We collect information that you provide directly to us:',
                item1: 'Account Information: Email address, username, and password when you register.',
                item2: 'Payment Information: Billing details processed securely through Stripe. We do not store your credit card numbers.',
                item3: 'Uploaded Data: XML files and product data you upload for analysis.',
                item4: 'Usage Data: Information about how you interact with our service.'
            },
            section3: {
                title: '3. How We Use Your Information',
                item1: 'Provide, maintain, and improve our services',
                item2: 'Process your payments and manage your subscription',
                item3: 'Generate analytics reports and insights',
                item4: 'Send you technical and administrative communications',
                item5: 'Respond to your comments and support requests'
            },
            section4: {
                title: '4. Data Security',
                content: 'We implement appropriate technical and organizational measures to protect your data, including:',
                item1: 'Encrypted data transmission (HTTPS/TLS)',
                item2: 'Secure password hashing (bcrypt)',
                item3: 'Data isolation between user accounts',
                item4: 'Regular security reviews and updates'
            },
            section5: {
                title: '5. Data Retention',
                content: 'We retain your data for as long as your account is active or as needed to provide you services. You can request deletion of your account and associated data at any time by contacting us.'
            },
            section6: {
                title: '6. Third-Party Services',
                content: 'We use the following third-party services:',
                item1: 'Stripe: Payment processing (they handle your payment information)',
                item2: 'DeepSeek: AI-powered insights (optional feature)',
                item3: 'Resend: Email delivery for reports and notifications'
            },
            section7: {
                title: '7. Your Rights',
                content: 'You have the right to:',
                item1: 'Access and download your personal data',
                item2: 'Correct inaccurate information',
                item3: 'Request deletion of your data',
                item4: 'Opt-out of marketing communications'
            },
            section8: {
                title: '8. Contact Us',
                content: 'If you have any questions about this Privacy Policy, please contact us at:'
            },
            home: 'Home',
            terms: 'Terms of Service',
            lastUpdated: 'Last Updated: April 13, 2026'
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
            
            // Top 5 产品卡片
            top5Products: 'Top 5 Products',
            revenueTrend: 'Revenue Trend',
            totalRevenue: 'Latest Revenue',
            avgDailyRevenue: 'Avg Revenue',
            trendUp: 'Rising',
            trendDown: 'Falling',
            trendNeutral: 'Stable',
            days7: '7 Days',
            days30: '30 Days',
            revenue: 'Revenue',
            singleUploadHint: 'Only one upload. Upload more XML files to see trends.',
            singleDayHint: 'Only one day of data. Upload more XML files to see trend changes.',
            noDataHint: 'No historical data available. Upload XML files to start tracking trends.',
            uploadTime: 'Upload Time',
            products: 'Products',
            change: 'Change',
            clearAllData: 'Clear All Data',
            confirmClearAll: 'Are you sure you want to delete ALL your XML data? This action cannot be undone.',
            clearing: 'Clearing data...',
            clearSuccess: 'All data has been cleared',
            clearFailed: 'Failed to clear data',
            conversion: 'Conversion',
            
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
            guideTitle: 'User Guide',
            guideDesc: 'Learn how to use IMVU Analytics effectively with our comprehensive guide.',
            // Feature cards
            feature1Title: 'AI-Powered Sales Reports',
            feature1Desc: 'Automatically generate comprehensive sales reports with AI insights and trend analysis.',
            feature2Title: 'Crystal Clear Visualizations',
            feature2Desc: 'Interactive charts that make data interpretation effortless and intuitive.',
            feature3Title: 'Smart Decision Support',
            feature3Desc: 'Data-driven recommendations to optimize your product strategy and pricing.',
            feature4Title: 'Secure & Private',
            feature4Desc: 'Your data stays local. We never store or share your information externally.',
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
        },

        // Terms of Service page
        terms: {
            title: 'Terms of Service',
            subtitle: 'Please read these terms carefully before using our service',
            section1: {
                title: '1. Acceptance of Terms',
                content: 'By accessing and using IMVU Analytics Platform ("the Service"), you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.'
            },
            section2: {
                title: '2. Description of Service',
                content: 'IMVU Analytics Platform provides data analysis tools for IMVU creators, including but not limited to:',
                item1: 'Product sales data upload and parsing',
                item2: 'Data dashboard and visualization',
                item3: 'AI-powered insights and analysis',
                item4: 'Data comparison and trend analysis',
                item5: 'Report generation and export'
            },
            section3: {
                title: '3. User Accounts',
                item1: 'You must provide accurate and complete information during registration.',
                item2: 'You are responsible for maintaining the security of your account credentials.',
                item3: 'You are responsible for all activities that occur under your account.',
                item4: 'You must notify us immediately of any unauthorized use of your account.'
            },
            section4: {
                title: '4. Subscription and Payment',
                price: 'Subscription Price: $12 USD per month',
                item1: 'Subscriptions are billed monthly through Stripe.',
                item2: 'You may cancel your subscription at any time.',
                item3: 'Cancelled subscriptions remain active until the end of the billing period.',
                item4: 'No refunds are provided for partial months.'
            },
            section5: {
                title: '5. Acceptable Use',
                content: 'You agree NOT to:',
                item1: 'Upload malicious files or attempt to compromise our systems',
                item2: 'Use the Service for any illegal purpose',
                item3: 'Attempt to reverse engineer or extract source code from the Service',
                item4: 'Share your account credentials with others',
                item5: 'Upload data that infringes on others\' intellectual property rights'
            },
            section6: {
                title: '6. Data and Privacy',
                content: 'Your use of the Service is also governed by our Privacy Policy. Key points:',
                item1: 'We collect and process your data as described in our Privacy Policy',
                item2: 'You retain ownership of your uploaded data',
                item3: 'We implement security measures to protect your data'
            },
            section7: {
                title: '7. Intellectual Property',
                content: 'IMVU Analytics Platform and its original content, features, and functionality are owned by us and are protected by international copyright, trademark, and other intellectual property laws.'
            },
            section8: {
                title: '8. Limitation of Liability',
                content: 'To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of the Service.'
            },
            section9: {
                title: '9. Changes to Terms',
                content: 'We reserve the right to modify these terms at any time. We will notify users of significant changes via email or through the Service. Continued use of the Service after changes constitutes acceptance of the new terms.'
            },
            section10: {
                title: '10. Contact Information',
                content: 'For questions about these Terms of Service, please contact us at:'
            },
            backHome: 'Back to Home',
            lastUpdated: 'Last Updated: April 13, 2026'
        },

        // Footer
        footer: {
            terms: 'Terms of Service',
            privacy: 'Privacy Policy',
            links: 'Links',
            home: 'Home',
            guide: 'User Guide',
            pricing: 'Pricing',
            support: 'Support',
            login: 'Login',
            register: 'Register',
            tagline: 'Professional IMVU Creator Data Analysis Tool',
            copyright: '© 2024-2026 IMVU Analytics. All rights reserved.'
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
            faq: '常见问题',
            faq1: {
                q: '数据是否安全？',
                a: '是的，数据安全是我们的首要任务。所有数据传输都使用 HTTPS 加密，数据存储在安全的云服务器上。您的产品数据仅用于分析，不会与第三方共享。'
            },
            faq2: {
                q: '支持哪些数据格式？',
                a: '目前仅支持从 IMVU Creator 后台导出的 XML 格式文件。这是 IMVU 官方提供的产品统计数据格式，包含完整的产品信息和销售数据。'
            },
            faq3: {
                q: 'AI 洞察功能需要额外付费吗？',
                a: 'AI 洞察功能包含在 Pro 订阅中，无需额外付费。订阅后即可无限次使用 AI 分析功能，包括数据洞察、SEO 分析、对比分析等。'
            },
            faq4: {
                q: '如何取消订阅？',
                a: '您可以随时在「个人中心」页面管理订阅，点击「管理订阅」即可进入 Stripe 客户门户取消订阅。取消后，您仍可使用服务直到当前计费周期结束。'
            },
            faq5: {
                q: '数据可以保存多久？',
                a: '上传的数据会一直保存在您的账户中，您可以随时查看历史数据、生成对比报告。如需删除数据，可以在仪表盘中手动删除特定数据集。'
            },
            faq6: {
                q: '可以退款吗？',
                a: '我们不提供部分月份的退款。但您可以随时取消订阅，并继续使用服务直到计费周期结束。取消后不会再产生新的费用。'
            },
            faq7: {
                q: '使用的是什么 AI 技术？',
                a: '我们使用 DeepSeek AI 进行智能分析。它会自动生成趋势洞察、SEO 优化建议和数据对比报告。支持中英文双语输出。'
            },
            faq8: {
                q: '分析结果准确吗？',
                a: '数据解析基于 IMVU 官方 XML 格式，准确率 100%。AI 洞察基于您的实际数据提供趋势分析和优化建议，结果可能因数据质量而异。'
            },
            ctaTitle: '准备好提升您的 IMVU 创作收益了吗？',
            ctaBtn: '免费开始使用'
        },
        
        // Privacy Policy page
        privacy: {
            title: '隐私政策',
            subtitle: '我们如何收集、使用和保护您的数据',
            section1: {
                title: '1. 简介',
                content: 'IMVU Analytics（简称"我们"）致力于保护您的隐私。本隐私政策说明了当您使用我们的数据分析平台时，我们如何收集、使用、披露和保护您的信息。'
            },
            section2: {
                title: '2. 我们收集的信息',
                intro: '我们收集您直接提供给我们的信息：',
                item1: '账户信息：您注册时提供的电子邮件地址、用户名和密码。',
                item2: '支付信息：通过Stripe安全处理的账单详情。我们不存储您的信用卡号码。',
                item3: '上传数据：您上传用于分析的XML文件和产品数据。',
                item4: '使用数据：关于您如何与我们服务互动的信息。'
            },
            section3: {
                title: '3. 我们如何使用您的信息',
                item1: '提供、维护和改进我们的服务',
                item2: '处理您的付款并管理您的订阅',
                item3: '生成分析报告和洞察',
                item4: '向您发送技术和行政通知',
                item5: '回应您的评论和支持请求'
            },
            section4: {
                title: '4. 数据安全',
                content: '我们采取适当的技术和组织措施来保护您的数据，包括：',
                item1: '加密数据传输（HTTPS/TLS）',
                item2: '安全密码哈希（bcrypt）',
                item3: '用户账户间的数据隔离',
                item4: '定期安全审查和更新'
            },
            section5: {
                title: '5. 数据保留',
                content: '我们会保留您的数据，直到您的账户处于活跃状态或需要为您提供服务。您可以随时联系我们请求删除您的账户和相关数据。'
            },
            section6: {
                title: '6. 第三方服务',
                content: '我们使用以下第三方服务：',
                item1: 'Stripe：支付处理（他们处理您的支付信息）',
                item2: 'DeepSeek：AI驱动洞察（可选功能）',
                item3: 'Resend：报告和通知的邮件发送'
            },
            section7: {
                title: '7. 您的权利',
                content: '您有权：',
                item1: '访问和下载您的个人数据',
                item2: '更正不准确的信息',
                item3: '请求删除您的数据',
                item4: '选择退出营销通讯'
            },
            section8: {
                title: '8. 联系我们',
                content: '如果您对本隐私政策有任何疑问，请通过以下方式联系我们：'
            },
            home: '首页',
            terms: '服务条款',
            lastUpdated: '最后更新：2026年4月13日'
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
            
            // Top 5 产品卡片
            top5Products: 'Top 5 产品',
            revenueTrend: '收入趋势',
            totalRevenue: '最新收入',
            avgDailyRevenue: '平均收入',
            trendUp: '上升',
            trendDown: '下降',
            trendNeutral: '持平',
            days7: '7天',
            days30: '30天',
            revenue: '收入',
            singleUploadHint: '只有一次上传，继续上传 XML 可查看趋势变化。',
            singleDayHint: '仅有一天的数据，上传更多 XML 可查看趋势变化。',
            noDataHint: '暂无历史数据，上传 XML 文件即可开始趋势追踪。',
            uploadTime: '上传时间',
            products: '产品数',
            change: '变化',
            clearAllData: '清空数据',
            confirmClearAll: '确定要删除所有 XML 数据吗？此操作不可撤销！',
            clearing: '正在清空数据...',
            clearSuccess: '数据已清空',
            clearFailed: '清空失败',
            conversion: '转化率',
            
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
            guideTitle: '用户指南',
            guideDesc: '查看完整的使用指南，快速掌握 IMVU Analytics 的各项功能。',
            // Feature cards
            feature1Title: 'AI智能销售报告',
            feature1Desc: '自动生成包含AI洞察和趋势分析的综合销售报告。',
            feature2Title: '清晰数据可视化',
            feature2Desc: '交互式图表让数据解读变得轻松直观。',
            feature3Title: '智能决策支持',
            feature3Desc: '基于数据的建议，优化您的产品策略和定价。',
            feature4Title: '安全与隐私',
            feature4Desc: '您的数据保存在本地，我们绝不存储或对外分享您的信息。',
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
        },

        // 服务条款页面
        terms: {
            title: '服务条款',
            subtitle: '请在使用我们的服务前仔细阅读这些条款',
            section1: {
                title: '1. 接受条款',
                content: '访问和使用 IMVU Analytics 平台（简称"服务"），即表示您接受并同意受这些服务条款的约束。如果您不同意这些条款，请不要使用本服务。'
            },
            section2: {
                title: '2. 服务描述',
                content: 'IMVU Analytics 平台为 IMVU 创作者提供数据分析工具，包括但不限于：',
                item1: '产品销售数据上传和解析',
                item2: '数据仪表盘和可视化',
                item3: 'AI 智能洞察和分析',
                item4: '数据对比和趋势分析',
                item5: '报告生成和导出'
            },
            section3: {
                title: '3. 用户账户',
                item1: '您必须在注册时提供准确完整的信息。',
                item2: '您有责任保护账户凭据的安全。',
                item3: '您对账户下发生的所有活动负责。',
                item4: '如发现账户被未授权使用，请立即通知我们。'
            },
            section4: {
                title: '4. 订阅和付款',
                price: '订阅价格：$12 美元/月',
                item1: '订阅通过 Stripe 按月计费。',
                item2: '您可以随时取消订阅。',
                item3: '取消的订阅在计费周期结束前保持有效。',
                item4: '部分月份不提供退款。'
            },
            section5: {
                title: '5. 可接受使用',
                content: '您同意不会：',
                item1: '上传恶意文件或试图破坏我们的系统',
                item2: '将服务用于任何非法目的',
                item3: '尝试逆向工程或从服务中提取源代码',
                item4: '与他人共享您的账户凭据',
                item5: '上传侵犯他人知识产权的数据'
            },
            section6: {
                title: '6. 数据和隐私',
                content: '您对服务的使用也受我们的隐私政策约束。要点：',
                item1: '我们按照隐私政策收集和处理您的数据',
                item2: '您保留上传数据的所有权',
                item3: '我们实施安全措施保护您的数据'
            },
            section7: {
                title: '7. 知识产权',
                content: 'IMVU Analytics 平台及其原创内容、功能和特性归我们所有，受国际版权、商标和其他知识产权法保护。'
            },
            section8: {
                title: '8. 责任限制',
                content: '在法律允许的最大范围内，我们不对因您使用服务而产生的任何间接、偶然、特殊、后果性或惩罚性损害承担责任。'
            },
            section9: {
                title: '9. 条款变更',
                content: '我们保留随时修改这些条款的权利。我们将通过电子邮件或服务通知用户重大变更。变更后继续使用服务即表示接受新条款。'
            },
            section10: {
                title: '10. 联系信息',
                content: '如有关于服务条款的问题，请联系我们：'
            },
            backHome: '返回首页',
            lastUpdated: '最后更新：2026年4月13日'
        },

        // Footer
        footer: {
            terms: '服务条款',
            privacy: '隐私政策',
            links: '链接',
            home: '首页',
            guide: '使用指南',
            pricing: '价格',
            support: '支持',
            login: '登录',
            register: '注册',
            tagline: '专业的 IMVU Creator 数据分析工具',
            copyright: '© 2024-2026 IMVU Analytics. All rights reserved.'
        }
    },
    
    fr: {
        // Nom de l'application
        appName: 'Plateforme IMVU Analytics',
        
        // Navigation
        nav: {
            dashboard: 'Tableau de bord',
            diagnosis: 'Analyse approfondie',
            compare: 'Comparaison de données',
            report: 'Rapports',
            profile: 'Profil',
            guide: 'Guide utilisateur',
            contact: 'Contactez-nous',
            subscribe: 'Abonnement',
            login: 'Connexion',
            register: 'Inscription',
            logout: 'Déconnexion'
        },
        
        // Page Contactez-nous
        contact: {
            pageTitle: 'Contactez-nous',
            title: 'Contactez-nous',
            subtitle: 'Nous serions ravis d\'avoir de vos nouvelles. Envoyez-nous un message et nous vous répondrons dès que possible.',
            name: 'Nom',
            namePlaceholder: 'Votre nom (optionnel)',
            email: 'E-mail',
            emailPlaceholder: 'votre.email@exemple.com',
            subject: 'Sujet',
            selectSubject: 'Sélectionnez un sujet',
            subjectTechnical: 'Support technique',
            subjectAccount: 'Problèmes de compte',
            subjectFeature: 'Suggestions de fonctionnalités',
            subjectSubscription: 'Questions d\'abonnement',
            subjectOther: 'Autre',
            message: 'Message',
            messagePlaceholder: 'Veuillez décrire votre question ou feedback en détail (minimum 10 caractères)',
            messageHint: 'Minimum 10 caractères',
            submit: 'Envoyer le message',
            sending: 'Envoi en cours...',
            success: 'Votre message a été envoyé avec succès ! Nous vous répondrons bientôt.',
            error: 'Une erreur s\'est produite. Veuillez réessayer plus tard.',
            errorEmailRequired: 'Veuillez entrer votre adresse e-mail.',
            errorSubjectRequired: 'Veuillez sélectionner un sujet.',
            errorMessageTooShort: 'Le message doit contenir au moins 10 caractères.',
            backHome: 'Retour à la connexion'
        },
        
        // Page Guide utilisateur
        guide: {
            heroTitle: '📖 Guide utilisateur IMVU Analytics',
            heroSubtitle: 'Apprenez à utiliser les outils d\'analyse de données pour augmenter vos revenus de créateur IMVU',
            quickStart: 'Démarrage rapide',
            step1: { title: 'Créer un compte', desc: 'Inscrivez-vous gratuitement pour commencer à utiliser les fonctionnalités de base. Abonnez-vous pour débloquer toutes les fonctionnalités premium.' },
            step2: { title: 'Télécharger les données XML', desc: 'Connectez-vous à votre compte IMVU Creator, allez sur la page Product Stats et téléchargez votre fichier XML de données produits.' },
            step3: { title: 'Importer les données', desc: 'Importez le fichier XML sur la plateforme, le système analysera automatiquement et générera des rapports d\'analyse détaillés.' },
            step4: { title: 'Voir l\'analyse', desc: 'Parcourez le tableau de bord, le diagnostic approfondi, la comparaison de données et autres fonctionnalités pour obtenir des informations IA et des suggestions d\'optimisation.' },
            features: 'Fonctionnalités principales',
            feature: {
                upload: 'Import de données',
                upload1: 'Prend en charge les données produits IMVU au format XML',
                upload2: 'Analyse automatique des informations produits, ventes, données de profit',
                upload3: 'Prend en charge la comparaison de données sur plusieurs périodes',
                upload4: 'Stockage sécurisé des données, consultation de l\'historique à tout moment',
                dashboard: 'Tableau de bord',
                dashboard1: 'Ventes totales, profit, nombre de produits en un coup d\'œil',
                dashboard2: 'Classement des meilleurs produits',
                dashboard3: 'Statistiques des produits visibles/cachés',
                dashboard4: 'Affichage de la conversion du profit en USD',
                diagnosis: 'Diagnostic approfondi',
                diagnosis1: 'Analyse de l\'entonnoir de conversion (exposition → panier → favoris → achat)',
                diagnosis2: 'Diagnostic des ventes et analyse des profits',
                diagnosis3: 'Détection d\'anomalies (algorithme Z-score)',
                diagnosis4: 'Suggestions d\'optimisation SEO des noms de produits',
                ai: 'Insights IA',
                ai1: 'Analyse intelligente basée sur DeepSeek AI',
                ai2: 'Génération automatique d\'aperçus de tendances et de suggestions d\'optimisation',
                ai3: 'Analyse d\'optimisation SEO des noms de produits',
                ai4: 'Prend en charge la sortie bilingue (français/anglais)',
                compare: 'Comparaison de données',
                compare1: 'Analyse comparative de données sur plusieurs périodes',
                compare2: 'Suivi des changements de classement des produits',
                compare3: 'Analyse des tendances des ventes et des profits',
                compare4: 'Rapports d\'insights comparatifs IA',
                report: 'Génération de rapports',
                report1: 'Génère des rapports d\'analyse de données détaillés',
                report2: 'Prend en charge l\'exportation PDF',
                report3: 'Consultez les rapports historiques à tout moment',
                report4: 'Abonnement aux rapports par e-mail (optionnel)'
            },
            dataFormat: 'Format des données',
            howToDownload: 'Comment obtenir le fichier de données',
            howToDownloadDesc: 'Suivez ces étapes pour télécharger les données produits depuis le tableau de bord IMVU Creator :',
            downloadStep1: 'Connectez-vous au compte IMVU Creator',
            downloadStep2: 'Allez sur la page Products → Product Stats',
            downloadStep3: 'Sélectionnez la période à analyser',
            downloadStep4: 'Cliquez sur "Export to XML" pour télécharger le fichier',
            xmlFields: 'Champs de données du fichier XML :',
            seoGuide: 'Guide d\'optimisation SEO',
            seoTips: 'Conseils d\'optimisation des noms de produits',
            seoTipsDesc: 'Un bon nom de produit peut améliorer considérablement l\'exposition dans les recherches. Voici quelques conseils d\'optimisation :',
            seoBestPractices: 'Bonnes pratiques :',
            seoTip1: 'Utilisez des mots-clés descriptifs : incluez le type de produit, le style, la couleur, etc.',
            seoTip2: 'Nommage structuré : [Style/Thème] + [Type de produit] + [Caractéristiques clés]',
            seoTip3: 'Contrôlez la longueur : 3-8 mots efficaces recommandés',
            seoTip4: 'Évitez les caractères sans signification : n\'utilisez pas de chiffres purs ou de noms par défaut',
            seoAvoid: 'Évitez ces problèmes :',
            seoAvoid1: '❌ Noms avec uniquement des chiffres (comme "Produit 123")',
            seoAvoid2: '❌ Noms trop longs (plus de 100 caractères seront tronqués)',
            seoAvoid3: '❌ Remplissage de mots-clés',
            seoAvoid4: '❌ Noms sans rapport avec le contenu du produit',
            seoAiHint: 'Analyse SEO intelligente',
            seoAiHintDesc: 'Utilisez la fonctionnalité "Diagnostic approfondi", l\'IA analysera automatiquement vos noms de produits et fournira des suggestions d\'optimisation SEO spécifiques.',
            pricing: 'Plans d\'abonnement',
            faq: 'FAQ',
            faq1: {
                q: 'Mes données sont-elles sécurisées ?',
                a: 'Oui, la sécurité des données est notre priorité absolue. Toutes les transmissions de données utilisent le chiffrement HTTPS, et les données sont stockées sur des serveurs cloud sécurisés. Vos données produits sont utilisées uniquement pour l\'analyse et ne sont jamais partagées avec des tiers.'
            },
            faq2: {
                q: 'Quels formats de données sont pris en charge ?',
                a: 'Actuellement, seuls les fichiers au format XML exportés depuis le tableau de bord IMVU Creator sont pris en charge. C\'est le format officiel de statistiques produits fourni par IMVU, contenant les informations complètes sur les produits et les données de ventes.'
            },
            faq3: {
                q: 'Les Insights IA nécessitent-ils un paiement supplémentaire ?',
                a: 'Les Insights IA sont inclus dans l\'abonnement Pro sans frais supplémentaires. Après votre abonnement, vous pouvez utiliser les fonctionnalités d\'analyse IA un nombre illimité de fois, y compris les aperçus de données, l\'analyse SEO, l\'analyse comparative, et plus encore.'
            },
            faq4: {
                q: 'Comment annuler mon abonnement ?',
                a: 'Vous pouvez gérer votre abonnement à tout moment depuis la page "Profil". Cliquez sur "Gérer l\'abonnement" pour accéder au portail client Stripe et annuler. Après l\'annulation, vous pouvez continuer à utiliser le service jusqu\'à la fin de la période de facturation en cours.'
            },
            faq5: {
                q: 'Combien de temps mes données sont-elles stockées ?',
                a: 'Les données importées sont stockées dans votre compte indéfiniment. Vous pouvez consulter les données historiques et générer des rapports comparatifs à tout moment. Pour supprimer des données, supprimez manuellement des ensembles de données spécifiques depuis le tableau de bord.'
            },
            faq6: {
                q: 'Puis-je obtenir un remboursement ?',
                a: 'Nous n\'offrons pas de remboursements pour les mois partiels. Cependant, vous pouvez annuler à tout moment et continuer à utiliser le service jusqu\'à la fin de votre période de facturation. Aucun frais supplémentaire ne sera facturé après l\'annulation.'
            },
            faq7: {
                q: 'Quelle technologie IA est utilisée ?',
                a: 'Nous utilisons DeepSeek AI pour l\'analyse intelligente. Il génère automatiquement des aperçus de tendances, des suggestions d\'optimisation SEO et des rapports comparatifs de données. Prend en charge la sortie bilingue en français et en anglais.'
            },
            faq8: {
                q: 'Quelle est la précision de l\'analyse ?',
                a: 'L\'analyse des données est précise à 100% selon le format XML officiel IMVU. Les insights IA fournissent une analyse des tendances et des suggestions d\'optimisation basées sur vos données réelles. Les résultats peuvent varier en fonction de la qualité des données.'
            },
            ctaTitle: 'Prêt à augmenter vos revenus de créateur IMVU ?',
            ctaBtn: 'Commencer gratuitement'
        },
        
        // Page Politique de confidentialité
        privacy: {
            title: 'Politique de confidentialité',
            subtitle: 'Comment nous collectons, utilisons et protégeons vos données',
            section1: {
                title: '1. Introduction',
                content: 'IMVU Analytics ("nous", "notre" ou "nos") s\'engage à protéger votre vie privée. Cette politique de confidentialité explique comment nous collectons, utilisons, divulguons et protégeons vos informations lorsque vous utilisez notre plateforme d\'analyse de données.'
            },
            section2: {
                title: '2. Informations que nous collectons',
                intro: 'Nous collectons les informations que vous nous fournissez directement :',
                item1: 'Informations de compte : Adresse e-mail, nom d\'utilisateur et mot de passe lors de votre inscription.',
                item2: 'Informations de paiement : Détails de facturation traités de manière sécurisée via Stripe. Nous ne stockons pas vos numéros de carte de crédit.',
                item3: 'Données importées : Fichiers XML et données de produits que vous importez pour analyse.',
                item4: 'Données d\'utilisation : Informations sur la façon dont vous interagissez avec notre service.'
            },
            section3: {
                title: '3. Comment nous utilisons vos informations',
                item1: 'Fournir, maintenir et améliorer nos services',
                item2: 'Traiter vos paiements et gérer votre abonnement',
                item3: 'Générer des rapports d\'analyse et des aperçus',
                item4: 'Vous envoyer des communications techniques et administratives',
                item5: 'Répondre à vos commentaires et demandes de support'
            },
            section4: {
                title: '4. Sécurité des données',
                content: 'Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour protéger vos données, y compris :',
                item1: 'Transmission de données chiffrée (HTTPS/TLS)',
                item2: 'Hachage de mot de passe sécurisé (bcrypt)',
                item3: 'Isolation des données entre les comptes utilisateurs',
                item4: 'Examens et mises à jour de sécurité réguliers'
            },
            section5: {
                title: '5. Conservation des données',
                content: 'Nous conservons vos données tant que votre compte est actif ou selon nécessaire pour vous fournir des services. Vous pouvez demander la suppression de votre compte et des données associées à tout moment en nous contactant.'
            },
            section6: {
                title: '6. Services tiers',
                content: 'Nous utilisons les services tiers suivants :',
                item1: 'Stripe : Traitement des paiements (ils gèrent vos informations de paiement)',
                item2: 'DeepSeek : Insights alimentés par l\'IA (fonctionnalité optionnelle)',
                item3: 'Resend : Envoi d\'e-mails pour les rapports et notifications'
            },
            section7: {
                title: '7. Vos droits',
                content: 'Vous avez le droit de :',
                item1: 'Accéder et télécharger vos données personnelles',
                item2: 'Corriger les informations inexactes',
                item3: 'Demander la suppression de vos données',
                item4: 'Vous désinscrire des communications marketing'
            },
            section8: {
                title: '8. Contactez-nous',
                content: 'Si vous avez des questions concernant cette politique de confidentialité, veuillez nous contacter à :'
            },
            home: 'Accueil',
            terms: 'Conditions d\'utilisation',
            lastUpdated: 'Dernière mise à jour : 13 avril 2026'
        },
        
        // Titres des pages
        pageTitles: {
            dashboard: 'Aperçu des données',
            diagnosis: 'Analyse approfondie',
            compare: 'Comparaison de données',
            report: 'Centre de rapports'
        },
        
        // Tableau de bord
        dashboard: {
            uploadTitle: 'Importer des données XML',
            uploadHint: 'Glissez le fichier ici ou cliquez pour sélectionner',
            selectFile: 'Sélectionner un fichier',
            downloadTemplate: 'Télécharger le modèle',
            uploading: 'Import et analyse en cours...',
            uploadSuccess: 'Import réussi !',
            uploadFailed: 'Échec de l\'import',
            
            // Cartes métriques
            directSales: 'Ventes directes',
            indirectSales: 'Ventes indirectes',
            promotedSales: 'Ventes promotionnelles',
            totalSales: 'Ventes totales',
            totalProfit: 'Profit total',
            totalProfitCredits: 'Profit total (Credits)',
            totalProfitUsd: 'Profit total (USD)',
            visibleProducts: 'Produits visibles',
            hiddenProducts: 'Produits cachés',
            totalProducts: 'Total des produits',
            
            // Titres des graphiques
            topProductsBySales: 'Top 10 des produits (Ventes)',
            visibilityDistribution: 'Distribution de visibilité',
            trafficComparison: 'Comparaison du trafic',
            priceRangeDistribution: 'Distribution par gamme de prix',
            
            // Tableau des produits
            productList: 'Liste des produits',
            searchPlaceholder: 'Rechercher par ID ou nom...',
            productId: 'ID du produit',
            productName: 'Nom du produit',
            price: 'Prix',
            profit: 'Profit',
            profitMargin: 'Marge bénéficiaire',
            visibility: 'Visibilité',
            visible: 'Visible',
            hidden: 'Caché',
            
            // Étiquettes des graphiques
            sales: 'Ventes',
            visibleLabel: 'Visible',
            hiddenLabel: 'Caché',
            organicTraffic: 'Trafic organique',
            paidTraffic: 'Trafic payant',
            
            // Messages d\'état
            noData: 'Aucune donnée disponible',
            loading: 'Chargement des données...',
            loadingFailed: 'Échec du chargement des données',
            retry: 'Réessayer',
            requestTimeout: 'Délai d\'attente dépassé, veuillez vérifier votre connexion',
            items: 'éléments',
            
            // Nom de l\'ensemble de données
            datasetNamePlaceholder: 'Nom de l\'ensemble de données (optionnel, ex. 2024-01)',
            datasetNameHint: 'Laissez vide pour utiliser l\'ensemble de données par défaut',
            
            // Top 5 produits et tendances
            top5Products: 'Top 5 des produits',
            revenueTrend: 'Tendance des revenus',
            totalRevenue: 'Revenu récent',
            avgDailyRevenue: 'Revenu moyen',
            trendUp: 'En hausse',
            trendDown: 'En baisse',
            trendNeutral: 'Stable',
            days7: '7 jours',
            days30: '30 jours',
            revenue: 'Revenu',
            singleUploadHint: 'Un seul import. Importez plus de fichiers XML pour voir les tendances.',
            singleDayHint: 'Une seule journée de données. Importez plus de fichiers XML pour voir les changements de tendance.',
            noDataHint: 'Aucune donnée historique disponible. Importez des fichiers XML pour commencer le suivi des tendances.',
            uploadTime: 'Date d\'import',
            products: 'Produits',
            change: 'Variation',
            clearAllData: 'Effacer les données',
            confirmClearAll: 'Êtes-vous sûr de vouloir supprimer TOUTES vos données XML ? Cette action est irréversible.',
            clearing: 'Suppression en cours...',
            clearSuccess: 'Toutes les données ont été effacées',
            clearFailed: 'Échec de la suppression',
            conversion: 'Conversion'
        },
        
        // Diagnostic approfondi
        diagnosis: {
            funnelAnalysis: 'Analyse de l\'entonnoir de conversion',
            impressions: 'Impressions',
            addToCart: 'Ajout au panier',
            wishlist: 'Favoris',
            sales: 'Ventes',
            impressionToCart: 'Impression → Panier',
            cartToWishlist: 'Panier → Favoris',
            wishlistToSales: 'Favoris → Commande',
            
            // Diagnostic des ventes
            totalSalesAmount: 'Montant total des ventes',
            totalProfit: 'Profit total',
            avgProfitMargin: 'Marge bénéficiaire moyenne',
            
            // Gamme de prix
            priceRangeAnalysis: 'Analyse par gamme de prix',
            priceRange: 'Gamme de prix',
            productCount: 'Produits',
            totalSalesQty: 'Ventes totales',
            totalProfitAmount: 'Profit total',
            avgProfitAmount: 'Profit moyen',
            
            // Trafic et ROI
            trafficAnalysis: 'Analyse du trafic',
            roiAnalysis: 'Analyse du ROI',
            organicRevenue: 'Revenu organique',
            paidRevenue: 'Revenu payant',
            estimatedCost: 'Coût estimé (payant)',
            estimatedRoi: 'ROI estimé',
            ratio: 'ratio',
            
            // Comportement utilisateur
            userBehavior: 'Analyse du comportement utilisateur',
            cartToSalesRate: 'Taux Panier → Commande',
            cartToWishlistRate: 'Taux Panier → Favoris',
            wishlistToSalesRate: 'Taux Favoris → Commande',
            
            // Produits à haut profit
            highProfitProducts: 'Produits à haut profit',
            noHighProfitProducts: 'Aucun produit à haut profit',
            
            // Détection d\'anomalies
            anomalyDetection: 'Détection d\'anomalies',
            noAnomalyDetected: 'Aucune anomalie de ventes détectée',
            type: 'Type',
            zScore: 'Z-score',
            
            // Alerte de faible conversion
            lowConversionAlert: 'Alerte de faible conversion',
            noLowConversionAlert: 'Aucune alerte de faible conversion',
            cartAdds: 'Ajouts au panier',
            conversionRate: 'Taux de conversion'
        },
        
        // Centre de rapports
        report: {
            quickActions: 'Actions rapides',
            generateFullReport: 'Générer le rapport complet',
            viewHtmlReport: 'Voir le rapport HTML',
            downloadLatest: 'Télécharger le dernier',
            generating: 'Génération du rapport en cours...',
            generationSuccess: 'Rapport généré avec succès !',
            generationFailed: 'Échec de la génération',
            emailSent: 'E-mail envoyé.',
            
            customReport: 'Paramètres du rapport personnalisé',
            reportOptions: 'Options du rapport',
            includeAnomalyDetection: 'Inclure la détection d\'anomalies',
            includeTopBottomProducts: 'Inclure les produits Top/Bottom',
            sendEmailNotification: 'Envoyer une notification par e-mail',
            topProductsLimit: 'Limite des produits Top',
            emailRecipients: 'Destinataires (séparés par des virgules)',
            generateCustomReport: 'Générer le rapport personnalisé',
            
            reportHistory: 'Historique des rapports',
            dailyReport: 'Rapport quotidien',
            manualReport: 'Rapport manuel',
            noReportHistory: 'Aucun historique de rapports',
            loading: 'Chargement...',
            loadFailed: 'Échec du chargement',
            status: {
                pending: 'En cours',
                completed: 'Terminé',
                failed: 'Échoué'
            },
            sentTo: 'Envoyé à',
            
            scheduledReport: 'Paramètres des rapports planifiés',
            scheduledReportInfo: 'Le système génère automatiquement un rapport à 1h00 UTC (9h00 Beijing) et l\'envoie à l\'e-mail configuré.',
            modifySchedule: 'Pour modifier la planification, modifiez REPORT_CRON_HOUR et REPORT_CRON_MINUTE dans config.py.',
            
            emailConfig: 'Configuration e-mail',
            configEnvVariables: 'Configurez les variables d\'environnement suivantes pour activer l\'envoi d\'e-mails :',
            envVariable: 'Variable d\'environnement',
            description: 'Description',
            example: 'Exemple',
            smtpHost: 'Serveur SMTP',
            smtpPort: 'Port SMTP',
            smtpUser: 'E-mail de l\'expéditeur',
            smtpPassword: 'Mot de passe / Mot de passe d\'application',
            emailTo: 'Destinataire par défaut',
            securityTip: 'Conseil de sécurité : Ne saisissez pas de mots de passe dans le code. Utilisez un fichier .env ou des variables d\'environnement.',
            
            download: 'Télécharger'
        },
        
        // Comparaison de données
        compare: {
            selectDatasets: 'Sélectionner les ensembles de données',
            selectHint: 'Sélectionnez 2-10 ensembles de données à comparer',
            noDatasets: 'Aucun ensemble de données disponible. Importez d\'abord des données.',
            uploadData: 'Importer des données',
            runCompare: 'Comparer la sélection',
            loading: 'Chargement...',
            
            // Métriques
            metricsComparison: 'Comparaison des métriques',
            totalSales: 'Ventes totales',
            totalProfit: 'Profit total',
            totalProducts: 'Total des produits',
            visibleProducts: 'Produits visibles',
            changeTrend: 'Tendance du changement',
            sales: 'Ventes',
            profit: 'Profit',
            
            // Graphiques de tendance
            salesTrend: 'Tendance des ventes',
            profitTrend: 'Tendance du profit',
            
            // Changements de classement
            rankUpProducts: 'Produits en hausse',
            rankDownProducts: 'Produits en baisse',
            newInTop: 'Nouveau dans le Top 10',
            exitedTop: 'Sorti du Top 10',
            rank: 'rang',
            new: 'NOUVEAU',
            exited: 'SORTI',
            noChange: 'Aucun changement de classement',
            noneInTop: 'Aucun',
            
            // Comparaison des Top 10
            topProductsComparison: 'Comparaison des Top 10 produits',
            rankingImproved: 'Classement amélioré',
            rankingDeclined: 'Classement baissé',
            newEntries: 'Nouvelles entrées',
            droppedOut: 'Sortis du Top 10',
            productName: 'Nom du produit',
            oldRank: 'Ancien rang',
            newRank: 'Nouveau rang',
            change: 'Changement',
            
            // Opérations
            products: 'produits',
            confirmDelete: 'Êtes-vous sûr de vouloir supprimer cet ensemble de données ?'
        },
        
        // Insights IA
        insights: {
            pageTitle: 'Insights IA',
            dashboard: {
                title: 'Insights de données IA'
            },
            diagnosis: {
                title: 'Insights de diagnostic IA'
            },
            compare: {
                title: 'Insights comparatifs IA'
            },
            quickAnalysis: 'Analyse rapide',
            salesTrends: 'Analyse des tendances de ventes',
            profitOptimization: 'Optimisation du profit',
            productRecommendations: 'Recommandations de produits',
            suggestedQuestions: 'Questions suggérées',
            q1: 'Top 5 des produits les plus vendus',
            q2: 'Produits avec la marge bénéficiaire la plus élevée',
            q3: 'Suggestions de stratégie marketing',
            aiChat: 'Assistant IA',
            welcome: 'Bonjour ! Je suis votre assistant IA. Posez-moi n\'importe quelle question sur vos données marketing.',
            askPlaceholder: 'Posez des questions sur vos données...',
            apiKeyRequired: 'La clé API DeepSeek est requise. Veuillez la configurer dans les Paramètres.',
            generate: 'Générer les Insights IA',
            refresh: 'Actualiser les insights',
            generating: 'Génération des insights IA en cours...',
            configHint: 'Configurez la clé API DeepSeek pour une analyse plus intelligente. Allez sur',
            settings: 'Page des paramètres',
            loadError: 'Échec du chargement, veuillez réessayer plus tard',
            seo: {
                title: 'Analyse SEO des noms de produits',
                generate: 'Analyser les noms de produits',
                analyzing: 'Analyse des noms de produits en cours...'
            },
            offlineMode: 'Mode hors ligne',
            noData: 'Aucune donnée disponible. Veuillez d\'abord importer des données de produits.',
            selectDatasets: 'Veuillez sélectionner au moins 2 ensembles de données à comparer',
            insufficientData: 'Ensembles de données valides insuffisants pour la comparaison',
            generatingFailed: 'Échec de la génération des insights',
            retry: 'Réessayer',
            analyzing: 'Analyse de vos données en cours...',
            error: 'Une erreur s\'est produite. Veuillez réessayer.'
        },

        // Page d\'import
        upload: {
            dataFormat: 'Exigences de format de données',
            formatXml: 'Fichier au format XML',
            maxSize: 'Taille maximale du fichier : 50 Mo',
            requiredFields: 'Champs requis : ID du produit, Nom du produit, Prix de gros, Profit',
            invalidFormat: 'Veuillez importer un fichier XML.',
            uploadSuccess: 'Données importées avec succès !',
            uploadError: 'Échec de l\'import. Veuillez réessayer.',
            processing: 'Traitement des données en cours...'
        },
        
        // Page des paramètres
        settings: {
            nav: 'Paramètres',
            pageTitle: 'Paramètres',
            systemInfo: 'Informations système',
            apiNote: 'Les fonctionnalités IA (DeepSeek) sont configurées par l\'administrateur du serveur. La clé API n\'est pas exposée aux utilisateurs pour des raisons de sécurité.'
        },
        
        // Centre personnel
        profile: {
            pageTitle: 'Centre personnel',
            userInfo: 'Informations utilisateur',
            email: 'E-mail',
            username: 'Nom d\'utilisateur',
            memberSince: 'Membre depuis',
            subscription: 'Abonnement',
            subscriptionStatus: 'Statut',
            subscriptionEndDate: 'Date de fin',
            notSubscribed: 'Non abonné',
            subscribed: 'Abonné',
            updateUsername: 'Modifier le nom d\'utilisateur',
            newUsername: 'Nouveau nom d\'utilisateur',
            usernamePlaceholder: 'Entrez un nouveau nom d\'utilisateur (optionnel)',
            usernameHint: 'Laissez vide pour supprimer le nom d\'utilisateur',
            saveUsername: 'Enregistrer le nom d\'utilisateur',
            changePassword: 'Modifier le mot de passe',
            oldPassword: 'Mot de passe actuel',
            oldPasswordPlaceholder: 'Entrez le mot de passe actuel',
            newPassword: 'Nouveau mot de passe',
            newPasswordPlaceholder: 'Entrez un nouveau mot de passe (minimum 8 caractères)',
            confirmPassword: 'Confirmer le mot de passe',
            confirmPasswordPlaceholder: 'Confirmez le nouveau mot de passe',
            passwordHint: 'Le mot de passe doit comporter au moins 8 caractères',
            changePasswordBtn: 'Modifier le mot de passe',
            logout: 'Déconnexion',
            logoutHint: 'Cliquez sur le bouton ci-dessous pour vous déconnecter en toute sécurité.',
            logoutBtn: 'Déconnexion',
            loading: 'Chargement...',
            updateSuccess: 'Mise à jour réussie !',
            updateFailed: 'Échec de la mise à jour. Veuillez réessayer.',
            passwordChangeSuccess: 'Mot de passe modifié avec succès !',
            passwordChangeFailed: 'Échec de la modification du mot de passe. Veuillez réessayer.',
            passwordMinLength: 'Le mot de passe doit comporter au moins 8 caractères.',
            passwordMismatch: 'Les nouveaux mots de passe ne correspondent pas.'
        },
        
        // Changement de langue
        language: {
            switchTo: 'Passer à',
            current: 'Actuel'
        },

        // Page d\'inscription
        register: {
            pageTitle: 'Inscription - IMVU Analytics',
            subtitle: 'Créez votre compte',
            email: 'E-mail',
            username: 'Nom d\'utilisateur (optionnel)',
            usernamePlaceholder: 'Nom d\'utilisateur (optionnel)',
            password: 'Mot de passe',
            confirmPassword: 'Confirmer le mot de passe',
            passwordReq: 'Le mot de passe doit comporter au moins 8 caractères',
            registerBtn: 'S\'inscrire',
            hasAccount: 'Vous avez déjà un compte ?',
            loginLink: 'Se connecter maintenant',
            // Messages de validation du formulaire
            registerSuccess: 'Inscription réussie ! Redirection vers la connexion...',
            registerError: 'Échec de l\'inscription. Veuillez réessayer.',
            emailUsed: 'Cet e-mail est déjà enregistré',
            invalidEmail: 'Veuillez entrer une adresse e-mail valide',
            passwordMismatch: 'Les mots de passe ne correspondent pas',
            passwordShort: 'Le mot de passe doit comporter au moins 8 caractères',
            // Force du mot de passe
            weak: 'Faible',
            medium: 'Moyen',
            strong: 'Fort',
            veryStrong: 'Très fort'
        },

        // Page de connexion
        login: {
            pageTitle: 'Connexion - IMVU Analytics',
            welcomeBack: 'Bon retour',
            subtitle: 'Connectez-vous à votre compte',
            email: 'E-mail',
            password: 'Mot de passe',
            rememberMe: 'Se souvenir de moi',
            forgotPassword: 'Mot de passe oublié ?',
            loginBtn: 'Connexion',
            noAccount: 'Vous n\'avez pas de compte ?',
            registerLink: 'S\'inscrire maintenant',
            guideTitle: 'Guide d\'utilisation',
            guideDesc: 'Consultez notre guide complet pour maîtriser rapidement IMVU Analytics.',
            // Feature cards
            feature1Title: 'Rapports de vente IA',
            feature1Desc: 'Générez automatiquement des rapports de vente complets avec des insights IA et une analyse de tendances.',
            feature2Title: 'Visualisations claires',
            feature2Desc: 'Des graphiques interactifs qui rendent l\'interprétation des données simple et intuitive.',
            feature3Title: 'Support décisionnel intelligent',
            feature3Desc: 'Des recommandations basées sur les données pour optimiser votre stratégie produit et vos prix.',
            feature4Title: 'Sécurité et confidentialité',
            feature4Desc: 'Vos données restent locales. Nous ne stockons ni ne partageons vos informations.',
            // Messages de validation du formulaire
            loginSuccess: 'Connexion réussie ! Redirection...',
            loginError: 'Échec de la connexion. Veuillez vérifier vos identifiants.',
            invalidEmail: 'Veuillez entrer une adresse e-mail valide',
            passwordRequired: 'Le mot de passe est requis'
        },

        // Page mot de passe oublié
        forgotPassword: {
            pageTitle: 'Mot de passe oublié - IMVU Analytics',
            title: 'Mot de passe oublié',
            description: 'Entrez votre e-mail enregistré, nous enverrons un lien de réinitialisation du mot de passe',
            email: 'E-mail',
            sendResetLink: 'Envoyer le lien de réinitialisation',
            backToLogin: 'Retour à la connexion',
            // Messages de validation du formulaire
            invalidEmail: 'Veuillez entrer une adresse e-mail valide',
            emailRequired: 'L\'e-mail est requis',
            sending: 'Envoi en cours...',
            sendSuccess: 'Si cet e-mail est enregistré, un lien de réinitialisation a été envoyé. Veuillez vérifier votre dossier de spam.',
            sendError: 'Échec de l\'envoi de l\'e-mail. Veuillez réessayer plus tard.'
        },

        // Page de réinitialisation du mot de passe
        resetPassword: {
            pageTitle: 'Réinitialisation du mot de passe - IMVU Analytics',
            title: 'Réinitialisation du mot de passe',
            enterNewPassword: 'Veuillez entrer votre nouveau mot de passe',
            newPassword: 'Nouveau mot de passe',
            confirmPassword: 'Confirmer le mot de passe',
            passwordsMatch: 'Les mots de passe correspondent',
            passwordsMismatch: 'Les mots de passe ne correspondent pas',
            passwordHint: 'Le mot de passe doit comporter au moins 8 caractères',
            resetBtn: 'Réinitialiser le mot de passe',
            backToLogin: 'Retour à la connexion',
            validatingToken: 'Validation du lien en cours...',
            // Messages de validation du formulaire
            passwordRequired: 'Le mot de passe est requis',
            passwordTooShort: 'Le mot de passe doit comporter au moins 8 caractères',
            passwordsNotMatch: 'Les mots de passe ne correspondent pas',
            resetSuccess: 'Mot de passe réinitialisé avec succès ! Redirection vers la connexion...',
            resetError: 'Échec de la réinitialisation du mot de passe. Le lien peut avoir expiré.',
            invalidToken: 'Lien invalide ou expiré'
        },

        // Traductions communes
        common: {
            loading: 'Chargement...',
            error: 'Erreur',
            success: 'Succès',
            confirm: 'Confirmer',
            cancel: 'Annuler',
            close: 'Fermer',
            submit: 'Soumettre',
            save: 'Enregistrer',
            delete: 'Supprimer',
            edit: 'Modifier',
            view: 'Voir',
            back: 'Retour',
            next: 'Suivant',
            previous: 'Précédent',
            yes: 'Oui',
            no: 'Non'
        },

        // Page d\'annulation
        cancel: {
            pageTitle: 'Compte annulé',
            title: 'Compte annulé',
            description: 'Votre compte a été annulé avec succès.',
            message: 'Nous sommes désolés de vous voir partir. Si vous souhaitez rejoindre à nouveau, vous pouvez vous réinscrire à tout moment.',
            returnHome: 'Retour à l\'accueil',
            registerAgain: 'Se réinscrire'
        },

        // Page de succès
        success: {
            pageTitle: 'Succès',
            title: 'Succès !',
            message: 'Votre opération a été terminée avec succès.',
            continueText: 'Continuer',
            returnHome: 'Retour à l\'accueil'
        },

        // Page de tarification
        pricing: {
            pageTitle: 'Tarifs - IMVU Analytics',
            title: 'Tarification simple et transparente',
            subtitle: 'Un plan, toutes les fonctionnalités, sans frais cachés',
            // Noms des plans
            free: 'Gratuit',
            pro: 'Pro',
            enterprise: 'Entreprise',
            // Descriptions des plans
            freeDesc: 'Parfait pour commencer',
            proDesc: 'Pour les entreprises en croissance',
            enterpriseDesc: 'Pour les grandes organisations',
            // Liste des fonctionnalités
            compare1: 'Import de données',
            compare2: 'Tableau de bord de base',
            compare3: 'Diagnostic des données',
            compare4: 'Insights IA',
            compare5: 'Rapports par e-mail',
            subscribe_btn: 'S\'abonner maintenant - 12$/mois',
            manage: 'Gérer l\'abonnement',
            current_plan: 'Plan actuel',
            renews_at: 'Renouvellement le',
            subscribe_success: 'Redirection vers le paiement...',
            subscribe_error: 'Échec de la création de la session de paiement',
            not_logged_in: 'Veuillez d\'abord vous connecter',
            network_error: 'Erreur réseau, veuillez réessayer',
            // Fonctionnalités
            features: {
                uploads: 'Imports mensuels',
                products: 'Produits par import',
                datasets: 'Ensembles de données historiques',
                aiInsights: 'Insights IA',
                reports: 'Génération de rapports',
                emailReports: 'Rapports par e-mail',
                support: 'Support prioritaire',
                customBranding: 'Marque personnalisée'
            },
            // Limites des fonctionnalités
            unlimited: 'Illimité',
            notIncluded: 'Non inclus',
            // Boutons CTA
            getStarted: 'Commencer',
            upgrade: 'Mettre à niveau maintenant',
            contactSales: 'Contacter les ventes',
            currentPlan: 'Plan actuel'
        },

        // Page des conditions d\'utilisation
        terms: {
            title: 'Conditions d\'utilisation',
            subtitle: 'Veuillez lire attentivement ces conditions avant d\'utiliser notre service',
            section1: {
                title: '1. Acceptation des conditions',
                content: 'En accédant et en utilisant la plateforme IMVU Analytics ("le Service"), vous acceptez et acceptez d\'être lié par ces conditions d\'utilisation. Si vous n\'acceptez pas ces conditions, veuillez ne pas utiliser le Service.'
            },
            section2: {
                title: '2. Description du service',
                content: 'La plateforme IMVU Analytics fournit des outils d\'analyse de données pour les créateurs IMVU, y compris mais sans s\'y limiter :',
                item1: 'Import et analyse de données de ventes de produits',
                item2: 'Tableau de bord et visualisation des données',
                item3: 'Insights et analyse alimentés par l\'IA',
                item4: 'Comparaison et analyse des tendances des données',
                item5: 'Génération et exportation de rapports'
            },
            section3: {
                title: '3. Comptes utilisateurs',
                item1: 'Vous devez fournir des informations exactes et complètes lors de l\'inscription.',
                item2: 'Vous êtes responsable du maintien de la sécurité de vos identifiants de compte.',
                item3: 'Vous êtes responsable de toutes les activités effectuées sous votre compte.',
                item4: 'Vous devez nous notifier immédiatement de toute utilisation non autorisée de votre compte.'
            },
            section4: {
                title: '4. Abonnement et paiement',
                price: 'Prix de l\'abonnement : 12 USD par mois',
                item1: 'Les abonnements sont facturés mensuellement via Stripe.',
                item2: 'Vous pouvez annuler votre abonnement à tout moment.',
                item3: 'Les abonnements annulés restent actifs jusqu\'à la fin de la période de facturation.',
                item4: 'Aucun remboursement n\'est fourni pour les mois partiels.'
            },
            section5: {
                title: '5. Utilisation acceptable',
                content: 'Vous acceptez de NE PAS :',
                item1: 'Importer des fichiers malveillants ou tenter de compromettre nos systèmes',
                item2: 'Utiliser le Service à des fins illégales',
                item3: 'Tenter de désosser ou d\'extraire le code source du Service',
                item4: 'Partager vos identifiants de compte avec d\'autres',
                item5: 'Importer des données qui enfreignent les droits de propriété intellectuelle d\'autrui'
            },
            section6: {
                title: '6. Données et confidentialité',
                content: 'Votre utilisation du Service est également régie par notre Politique de confidentialité. Points clés :',
                item1: 'Nous collectons et traitons vos données comme décrit dans notre Politique de confidentialité',
                item2: 'Vous conservez la propriété de vos données importées',
                item3: 'Nous mettons en œuvre des mesures de sécurité pour protéger vos données'
            },
            section7: {
                title: '7. Propriété intellectuelle',
                content: 'La plateforme IMVU Analytics et son contenu original, ses fonctionnalités et ses fonctions sont notre propriété et sont protégés par les lois internationales sur le droit d\'auteur, les marques commerciales et autres lois sur la propriété intellectuelle.'
            },
            section8: {
                title: '8. Limitation de responsabilité',
                content: 'Dans la mesure maximale autorisée par la loi, nous ne serons pas responsables des dommages indirects, accidentels, spéciaux, consécutifs ou punitifs résultant de votre utilisation du Service.'
            },
            section9: {
                title: '9. Modifications des conditions',
                content: 'Nous nous réservons le droit de modifier ces conditions à tout moment. Nous notifierons les utilisateurs des changements importants par e-mail ou via le Service. L\'utilisation continue du Service après les modifications constitue l\'acceptation des nouvelles conditions.'
            },
            section10: {
                title: '10. Informations de contact',
                content: 'Pour toute question concernant ces conditions d\'utilisation, veuillez nous contacter à :'
            },
            backHome: 'Retour à l\'accueil',
            lastUpdated: 'Dernière mise à jour : 13 avril 2026'
        },

        // Footer
        footer: {
            terms: 'Conditions d\'utilisation',
            privacy: 'Politique de confidentialité',
            links: 'Liens',
            home: 'Accueil',
            guide: 'Guide utilisateur',
            pricing: 'Tarifs',
            support: 'Support',
            login: 'Connexion',
            register: 'Inscription',
            tagline: 'Outil d\'analyse de données professionnel pour créateurs IMVU',
            copyright: '© 2024-2026 IMVU Analytics. Tous droits réservés.'
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
 * 更新下拉选择框的选中状态
 */
function updateLanguageSelect() {
    const select = document.getElementById('langSelect');
    if (select) {
        select.value = currentLang;
    }
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
    // 同时更新下拉选择框
    updateLanguageSelect();
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
    updateLanguageSelect();
});

// 导出到全局作用域，供 HTML 页面使用
window.t = t;
window.setLanguage = setLanguage;
window.updateLanguage = updateLanguage;
window.getCurrentLanguage = getCurrentLanguage;
window.getLanguage = getLanguage;
window.updateLanguageSelect = updateLanguageSelect;
