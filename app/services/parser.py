"""
XML解析服务 - 解析上传的XML文件
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class XMLParserService:
    """XML文件解析服务"""
    
    # XML字段到数据库字段的映射
    FIELD_MAPPING = {
        'product_id': 'product_id',
        'product_name': 'product_name',
        'price': 'price',
        'profit': 'profit',
        'visible': 'visible',
        'direct_sales': 'direct_sales',
        'indirect_sales': 'indirect_sales',
        'promoted_sales': 'promoted_sales',
        'cart_adds': 'cart_adds',
        'wishlist_adds': 'wishlist_adds',
        'organic_impressions': 'organic_impressions',
        'paid_impressions': 'paid_impressions',
    }
    
    @staticmethod
    def parse_file(file_path: str) -> List[Dict]:
        """
        解析XML文件
        
        Args:
            file_path: XML文件路径
            
        Returns:
            产品数据列表
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            return XMLParserService._parse_root(root)
        except ET.ParseError as e:
            logger.error(f"XML解析错误: {e}")
            raise ValueError(f"XML文件格式错误: {e}")
        except Exception as e:
            logger.error(f"文件读取错误: {e}")
            raise IOError(f"无法读取文件: {e}")
    
    @staticmethod
    def parse_content(content: bytes) -> List[Dict]:
        """
        解析XML内容（从上传的文件流）
        
        Args:
            content: 文件字节内容
            
        Returns:
            产品数据列表
        """
        try:
            root = ET.fromstring(content)
            return XMLParserService._parse_root(root)
        except ET.ParseError as e:
            logger.error(f"XML解析错误: {e}")
            raise ValueError(f"XML文件格式错误: {e}")
    
    @staticmethod
    def _parse_root(root: ET.Element) -> List[Dict]:
        """
        解析XML根元素
        
        Args:
            root: XML根元素
            
        Returns:
            产品数据列表
        """
        products = []
        
        # 查找产品列表条目
        # 支持多种可能的标签名
        for tag in ['product_list_entry', 'product', 'item', 'entry']:
            entries = root.findall(f".//{tag}")
            if entries:
                for entry in entries:
                    product = XMLParserService._parse_entry(entry)
                    if product:
                        products.append(product)
                break
        
        # 如果没有找到任何条目，尝试直接解析根元素（单个产品）
        if not products and root.tag in ['product_list_entry', 'product', 'item', 'entry']:
            product = XMLParserService._parse_entry(root)
            if product:
                products.append(product)
        
        logger.info(f"成功解析 {len(products)} 条产品数据")
        return products
    
    @staticmethod
    def _parse_entry(entry: ET.Element) -> Optional[Dict]:
        """
        解析单个产品条目
        
        Args:
            entry: 产品条目元素
            
        Returns:
            产品数据字典
        """
        try:
            product = {}
            
            # 从属性中提取数据
            for xml_attr, db_field in XMLParserService.FIELD_MAPPING.items():
                value = entry.get(xml_attr, '')
                product[db_field] = XMLParserService._convert_value(value, db_field)
            
            # 从子元素中提取数据（备用方式）
            for xml_attr, db_field in XMLParserService.FIELD_MAPPING.items():
                if db_field not in product or product[db_field] is None:
                    child = entry.find(xml_attr)
                    if child is not None and child.text:
                        product[db_field] = XMLParserService._convert_value(child.text, db_field)
            
            # 添加元数据
            product['upload_time'] = datetime.utcnow()
            
            return product
        except Exception as e:
            logger.warning(f"解析产品条目失败: {e}")
            return None
    
    @staticmethod
    def _convert_value(value: str, field: str) -> any:
        """
        根据字段类型转换值
        
        Args:
            value: 原始字符串值
            field: 字段名
            
        Returns:
            转换后的值
        """
        if value is None or value == '':
            return 0 if field in ['price', 'profit', 'direct_sales', 'indirect_sales',
                                   'promoted_sales', 'cart_adds', 'wishlist_adds',
                                   'organic_impressions', 'paid_impressions'] else None
        
        # 数值字段
        numeric_fields = ['price', 'profit', 'direct_sales', 'indirect_sales',
                         'promoted_sales', 'cart_adds', 'wishlist_adds',
                         'organic_impressions', 'paid_impressions']
        
        if field in numeric_fields:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0
        
        # 布尔/可见性字段
        if field == 'visible':
            return value.upper() if value else 'N'
        
        return value
    
    @staticmethod
    def validate_xml_structure(content: bytes) -> tuple:
        """
        验证XML结构
        
        Args:
            content: XML字节内容
            
        Returns:
            (is_valid, message)
        """
        try:
            root = ET.fromstring(content)
            
            # 检查是否有产品条目
            entries = root.findall('.//product_list_entry')
            if not entries:
                entries = root.findall('.//product')
            if not entries:
                entries = root.findall('.//item')
            
            if not entries:
                return False, "未找到产品数据条目 (product_list_entry/product/item)"
            
            # 检查必要字段
            sample = entries[0]
            required_fields = ['product_id', 'product_name', 'price', 'profit']
            missing_fields = []
            
            for field in required_fields:
                if sample.get(field) is None and sample.find(field) is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, f"缺少必要字段: {', '.join(missing_fields)}"
            
            return True, f"验证通过，共 {len(entries)} 条产品记录"
            
        except ET.ParseError as e:
            return False, f"XML格式错误: {e}"
        except Exception as e:
            return False, f"验证失败: {e}"
