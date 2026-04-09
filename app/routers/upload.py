"""
文件上传路由 - 处理XML文件上传
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import os
import logging

import config
from app.services.parser import XMLParserService
from app.database import get_db_context, ProductDataRepository, DatasetRepository
from app.services.auth import get_current_user
from app.routers.dashboard import _clear_cache  # 导入缓存清除函数

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["上传"])


@router.post("/")
async def upload_xml_file(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    上传XML文件并解析
    
    - **file**: XML格式的产品数据文件
    - **dataset_name**: 数据集名称（可选），如 "2024年1月"
    """
    # 检查文件类型
    if not file.filename.endswith('.xml'):
        raise HTTPException(
            status_code=400,
            detail="只支持XML格式文件"
        )
    
    # 检查文件大小
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > config.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({config.MAX_UPLOAD_SIZE}MB)"
        )
    
    try:
        # 验证XML结构
        is_valid, message = XMLParserService.validate_xml_structure(content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # 解析XML
        products = XMLParserService.parse_content(content)
        
        if not products:
            raise HTTPException(
                status_code=400,
                detail="文件中没有找到产品数据"
            )
        
        # 保存到数据库，关联用户ID
        with get_db_context() as db:
            repo = ProductDataRepository(db)
            dataset_repo = DatasetRepository(db)
            
            from datetime import datetime
            from typing import Dict
            
            if dataset_name:
                # 使用用户提供的数据集名称，添加时间戳确保唯一性
                timestamp = datetime.now().strftime("%m-%d %H:%M")
                unique_name = f"{dataset_name} ({timestamp})"
            else:
                # 自动生成带时间戳的数据集名称，确保每次上传都是独立数据集
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                unique_name = f"数据集 {timestamp}"
            
            # 始终创建新的数据集记录，确保数据独立性，并关联用户
            dataset = dataset_repo.create(
                name=unique_name, 
                record_count=len(products),
                user_id=current_user.get('id')  # 关联用户ID
            )
            count = repo.bulk_insert_with_dataset(products, dataset.id)
            dataset_id = dataset.id
            dataset_name_display = dataset.name
        
        # 清除仪表盘缓存，确保新数据立即可见
        _clear_cache()
        
        logger.info(f"用户 {current_user.get('email')} 成功上传 {count} 条产品数据到数据集 '{dataset_name_display}'")
        
        return {
            "success": True,
            "message": f"成功解析并保存 {count} 条产品数据",
            "data": {
                "count": count,
                "dataset_id": dataset_id,
                "dataset_name": dataset_name_display,
                "preview": products[:3] if len(products) >= 3 else products
            }
        }
        
    except ValueError as e:
        logger.error(f"解析错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/validate")
async def validate_xml(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    验证XML文件结构（不上传）
    
    - **file**: XML格式的产品数据文件
    """
    if not file.filename.endswith('.xml'):
        return {"valid": False, "message": "只支持XML格式文件"}
    
    content = await file.read()
    is_valid, message = XMLParserService.validate_xml_structure(content)
    
    return {
        "valid": is_valid,
        "message": message
    }


@router.get("/template")
async def download_template():
    """
    下载XML模板文件
    """
    template_xml = """<?xml version="1.0" encoding="UTF-8"?>
<product_list>
    <!-- 示例数据 -->
    <product_list_entry 
        product_id="68521162" 
        product_name="示例产品 A" 
        price="715" 
        profit="300" 
        visible="Y" 
        direct_sales="1500" 
        indirect_sales="800" 
        promoted_sales="1200" 
        cart_adds="250" 
        wishlist_adds="180" 
        organic_impressions="50000" 
        paid_impressions="30000" />
        
    <product_list_entry 
        product_id="68521163" 
        product_name="示例产品 B" 
        price="299" 
        profit="120" 
        visible="Y" 
        direct_sales="800" 
        indirect_sales="400" 
        promoted_sales="600" 
        cart_adds="120" 
        wishlist_adds="90" 
        organic_impressions="35000" 
        paid_impressions="20000" />
        
    <product_list_entry 
        product_id="68521164" 
        product_name="示例产品 C" 
        price="1200" 
        profit="500" 
        visible="N" 
        direct_sales="200" 
        indirect_sales="100" 
        promoted_sales="150" 
        cart_adds="30" 
        wishlist_adds="20" 
        organic_impressions="10000" 
        paid_impressions="5000" />
</product_list>
"""
    
    return JSONResponse(
        content=template_xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": "attachment; filename=template.xml"
        }
    )
