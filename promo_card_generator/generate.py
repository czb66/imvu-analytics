#!/usr/bin/env python3
"""
IMVU 产品推广卡片生成器
使用方法：编辑 config.json，然后运行 python generate.py
"""

import json
import os
from datetime import datetime

def load_config(config_path="config.json"):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_product_html(product):
    """生成单个产品的HTML"""
    tag_class = "vip" if product.get("tag_type") == "vip" else ""
    
    html = f'''            <div class="product-card">
                <img src="{product['image']}" alt="{product['name']}" class="product-image">
                <div class="product-info">
                    <span class="product-tag {tag_class}">{product['tag']}</span>
                    <h3 class="product-name">{product['name']}</h3>
                    <p class="product-desc">{product['description']}</p>
                    <a href="{product['link']}" class="shop-btn" target="_blank">Shop Now →</a>
                </div>
            </div>'''
    
    return html

def generate_html(config):
    """生成完整的HTML"""
    # 读取模板
    template_path = os.path.join(os.path.dirname(__file__), "template.html")
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 生成产品列表HTML
    products_html = "\n".join([generate_product_html(p) for p in config['products']])
    
    # 替换占位符
    html = template.replace("{{TITLE}}", config['title'])
    html = html.replace("{{SUBTITLE}}", config['subtitle'])
    html = html.replace("{{INTRO}}", config['intro'])
    html = html.replace("{{PRODUCTS}}", products_html)
    html = html.replace("{{FOOTER}}", config['footer'])
    
    return html

def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    output_dir = os.path.join(script_dir, "output")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载配置
    print("📋 正在读取配置文件...")
    config = load_config(config_path)
    
    # 生成HTML
    print("🔨 正在生成HTML...")
    html = generate_html(config)
    
    # 保存输出
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"promo_card_{timestamp}.html")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 生成完成！")
    print(f"📁 输出文件：{output_file}")
    print(f"\n📦 共生成 {len(config['products'])} 个产品卡片")

if __name__ == "__main__":
    main()
