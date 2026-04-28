"""
文件上传路由 - 处理XML文件上传
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import os
import logging

import config
from app.services.parser import XMLParserService
from app.database import get_db_context, ProductDataRepository, DatasetRepository
from app.services.auth import get_current_user
from app.services.subscription_check import require_subscription
from app.routers.dashboard import _clear_user_cache  # 导入缓存清除函数
from app.services.cache import get_cache
from app.services.activity_tracker import activity_tracker
from app.core.rate_limiter import check_tiered_rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["上传"])


@router.post("/")
async def upload_xml_file(
    request: Request,
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    current_user: dict = Depends(require_subscription)
):
    """
    上传XML文件并解析（分层限流：free=5/day, pro=50/day）
    
    - **file**: XML格式的产品数据文件
    - **dataset_name**: 数据集名称（可选），如 "2024年1月"
    """
    # 检查分层限流
    check_result = await check_tiered_rate_limit("upload", request, current_user)
    if hasattr(check_result, 'status_code'):
        return check_result  # 返回限流响应
    
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
            
            from datetime import datetime, timedelta, timezone
            from typing import Dict
            
            # 北京时间
            beijing_tz = timezone(timedelta(hours=8))
            beijing_now = datetime.now(beijing_tz)
            
            if dataset_name:
                # 使用用户提供的数据集名称，添加时间戳确保唯一性
                timestamp = beijing_now.strftime("%m-%d %H:%M")
                unique_name = f"{dataset_name} ({timestamp})"
            else:
                # 自动生成带时间戳的数据集名称，确保每次上传都是独立数据集
                timestamp = beijing_now.strftime("%Y-%m-%d %H:%M")
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
            
            # 记录用户上传行为（在数据库事务内）
            activity_tracker.log_activity(
                db, current_user.get('id'), 'upload',
                resource_type='dataset',
                resource_id=dataset_id,
                metadata={'record_count': count, 'dataset_name': dataset_name_display}
            )
            
            # 检查并发放推荐奖励（关键操作：上传第一个数据集）
            from app.services.auth import AuthService
            auth_service = AuthService(db)
            reward_granted = auth_service.grant_pending_referral_rewards(current_user.get('id'))
            
            if reward_granted:
                logger.info(f"用户 {current_user.get('email')} 完成关键操作，已向其推荐人发放奖励")
        
        # 清除仪表盘缓存，确保新数据立即可见
        _clear_cache()
        
        logger.info(f"用户 {current_user.get('id')} 成功上传 {count} 条产品数据到数据集 '{dataset_name_display}'")
        
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
        raise HTTPException(status_code=400, detail="操作失败，请稍后重试")
    except Exception as e:
        logger.error(f"上传失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后重试")


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


@router.delete("/clear-all")
async def clear_all_data(current_user: dict = Depends(require_subscription)):
    """
    清空当前用户的所有 XML 数据（删除所有 Dataset 及关联的产品数据）
    """
    user_id = current_user.get('id')
    logger.info(f"[API] 用户 {current_user.get('email')} 请求清空所有数据 - 开始")
    
    try:
        with get_db_context() as db:
            dataset_repo = DatasetRepository(db)
            
            # 获取用户的所有数据集
            datasets = dataset_repo.get_all(user_id=user_id)
            
            if not datasets:
                logger.info(f"[API] 用户 {current_user.get('email')} 没有数据需要清空")
                return {
                    "success": True,
                    "message": "No data to clear"
                }
            
            # 删除所有数据集（关联的产品数据会级联删除）
            deleted_count = 0
            for dataset in datasets:
                dataset_repo.delete(dataset.id)
                deleted_count += 1
            
            # 清除仪表盘缓存
            _clear_cache()
            
            logger.info(f"[API] 用户 {current_user.get('email')} 成功清空 {deleted_count} 个数据集")
            
            return {
                "success": True,
                "message": f"Successfully deleted {deleted_count} dataset(s)"
            }
            
    except Exception as e:
        logger.error(f"[API] 清空数据失败: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear data. Please try again later.")


@router.get("/sample")
async def download_sample_data():
    """
    下载示例数据文件
    提供IMVU Creator的真实示例数据，用于体验平台功能
    """
    import os
    
    # 尝试从static目录读取示例数据
    sample_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "static", "sample_data.xml"
    )
    
    if os.path.exists(sample_file_path):
        with open(sample_file_path, 'r', encoding='utf-8') as f:
            sample_xml = f.read()
    else:
        # 如果文件不存在，返回内置的示例数据
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<product_list>
    <product_list_entry product_id="SMP001" product_name="Elegant Evening Gown - Purple" price="899" profit="450" visible="Y" direct_sales="12500" indirect_sales="8900" promoted_sales="18500" cart_adds="520" wishlist_adds="380" organic_impressions="98000" paid_impressions="72000" />
    <product_list_entry product_id="SMP002" product_name="Crystal Pendant Necklace" price="299" profit="155" visible="Y" direct_sales="8200" indirect_sales="5600" promoted_sales="11200" cart_adds="360" wishlist_adds="275" organic_impressions="68000" paid_impressions="48000" />
    <product_list_entry product_id="SMP003" product_name="Long Wavy Red Hair" price="349" profit="175" visible="Y" direct_sales="15200" indirect_sales="11800" promoted_sales="20600" cart_adds="620" wishlist_adds="480" organic_impressions="145000" paid_impressions="98000" />
    <product_list_entry product_id="SMP004" product_name="Golden Butterfly Wings" price="459" profit="235" visible="Y" direct_sales="6500" indirect_sales="4200" promoted_sales="8900" cart_adds="265" wishlist_adds="198" organic_impressions="58000" paid_impressions="42000" />
    <product_list_entry product_id="SMP005" product_name="Luxury King Size Bed" price="1599" profit="820" visible="Y" direct_sales="3200" indirect_sales="2100" promoted_sales="4800" cart_adds="145" wishlist_adds="98" organic_impressions="35000" paid_impressions="28000" />
    <product_list_entry product_id="SMP006" product_name="Cute Fluffy Cat Companion" price="599" profit="310" visible="Y" direct_sales="4200" indirect_sales="2800" promoted_sales="5800" cart_adds="185" wishlist_adds="135" organic_impressions="48000" paid_impressions="36000" />
    <product_list_entry product_id="SMP007" product_name="Casual Summer Dress - Floral" price="399" profit="195" visible="Y" direct_sales="9800" indirect_sales="7200" promoted_sales="14200" cart_adds="420" wishlist_adds="315" organic_impressions="88000" paid_impressions="65000" />
    <product_list_entry product_id="SMP008" product_name="Diamond Tiara Crown" price="599" profit="320" visible="Y" direct_sales="12500" indirect_sales="8900" promoted_sales="16800" cart_adds="540" wishlist_adds="410" organic_impressions="95000" paid_impressions="72000" />
</product_list>
"""
    
    return JSONResponse(
        content=sample_xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": "attachment; filename=imvu_sample_data.xml"
        }
    )