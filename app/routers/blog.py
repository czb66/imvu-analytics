"""
博客系统路由 - 博客文章管理和展示API
"""

from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging
import math

from app.database import get_db
from app.services.auth import get_current_user, get_optional_user
from app.services.admin import require_admin
import config
from app.main import templates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blog", tags=["博客"])


# ==================== Pydantic 模型 ====================

class BlogPostBase(BaseModel):
    """博客文章基础模型"""
    slug: str = Field(..., max_length=200, description="URL友好slug")
    title_en: str = Field(..., max_length=200, description="英文标题")
    title_zh: Optional[str] = Field(None, max_length=200, description="中文标题")
    title_fr: Optional[str] = Field(None, max_length=200, description="法文标题")
    content_en: str = Field(..., description="英文内容（Markdown）")
    content_zh: Optional[str] = Field(None, description="中文内容")
    content_fr: Optional[str] = Field(None, description="法文内容")
    excerpt_en: Optional[str] = Field(None, max_length=500, description="英文摘要")
    excerpt_zh: Optional[str] = Field(None, max_length=500, description="中文摘要")
    excerpt_fr: Optional[str] = Field(None, max_length=500, description="法文摘要")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片URL")
    meta_title: Optional[str] = Field(None, max_length=200, description="SEO标题")
    meta_description: Optional[str] = Field(None, max_length=500, description="SEO描述")
    author: Optional[str] = Field("IMVU Analytics Team", max_length=100, description="作者")
    is_featured: Optional[bool] = Field(False, description="是否为特色文章")


class BlogPostCreate(BlogPostBase):
    """创建博客文章"""
    is_published: bool = Field(False, description="是否发布")


class BlogPostUpdate(BaseModel):
    """更新博客文章"""
    title_en: Optional[str] = Field(None, max_length=200)
    title_zh: Optional[str] = Field(None, max_length=200)
    title_fr: Optional[str] = Field(None, max_length=200)
    content_en: Optional[str] = None
    content_zh: Optional[str] = None
    content_fr: Optional[str] = None
    excerpt_en: Optional[str] = Field(None, max_length=500)
    excerpt_zh: Optional[str] = Field(None, max_length=500)
    excerpt_fr: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    cover_image: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, max_length=100)
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None


class BlogPostResponse(BlogPostBase):
    """博客文章响应"""
    id: int
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    view_count: int
    is_featured: bool

    class Config:
        from_attributes = True


class BlogListResponse(BaseModel):
    """博客列表响应"""
    posts: List[BlogPostResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    categories: List[dict]


# ==================== 辅助函数 ====================

def get_reading_time(content: str) -> int:
    """估算阅读时间（分钟）"""
    words = len(content.split())
    return max(1, math.ceil(words / 200))


def slug_exists(db: Session, slug: str, exclude_id: int = None) -> bool:
    """检查slug是否已存在"""
    from app.models import BlogPost
    query = db.query(BlogPost).filter(BlogPost.slug == slug)
    if exclude_id:
        query = query.filter(BlogPost.id != exclude_id)
    return query.first() is not None


# ==================== 前台页面路由 ====================

@router.get("", response_class=HTMLResponse)
async def blog_home(
    request: Request,
    category: Optional[str] = Query(None, description="按分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    db: Session = Depends(get_db)
):
    """
    博客首页 - 显示文章列表
    """
    from app.models import BlogPost
    
    per_page = 12
    lang = request.headers.get("Accept-Language", "en")
    lang = 'zh' if lang.startswith('zh') else ('fr' if lang.startswith('fr') else 'en')
    
    try:
        # 查询已发布的文章
        query = db.query(BlogPost).filter(BlogPost.is_published == True)
        
        if category:
            query = query.filter(BlogPost.category == category)
        
        # 获取总数
        total = query.count()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        # 分页
        posts = query.order_by(desc(BlogPost.published_at), desc(BlogPost.created_at)) \
                      .offset((page - 1) * per_page) \
                      .limit(per_page) \
                      .all()
        
        # 获取特色文章
        featured_post = db.query(BlogPost).filter(
            BlogPost.is_published == True,
            BlogPost.is_featured == True
        ).order_by(desc(BlogPost.published_at)).first()
        
        if not featured_post:
            featured_post = posts[0] if posts else None
        
        # 获取分类统计
        categories = db.query(
            BlogPost.category,
            func.count(BlogPost.id).label('count')
        ).filter(
            BlogPost.is_published == True,
            BlogPost.category.isnot(None)
        ).group_by(BlogPost.category).all()
        
        category_list = [{"name": c.category or "Uncategorized", "count": c.count} for c in categories]
        
        # 获取热门文章（按浏览量）
        popular_posts = db.query(BlogPost).filter(
            BlogPost.is_published == True
        ).order_by(desc(BlogPost.view_count)).limit(5).all()
        
        # SEO meta
        seo_title = "IMVU Creator Blog - Tips, Tutorials & Industry Insights"
        seo_desc = "Stay updated with the latest IMVU creator tips, data analysis tutorials, and industry insights to boost your sales."
        
        return templates.TemplateResponse("blog.html", {
            "request": request,
            "posts": posts,
            "featured_post": featured_post,
            "popular_posts": popular_posts,
            "categories": category_list,
            "current_category": category,
            "current_page": page,
            "total_pages": total_pages,
            "total": total,
            "lang": lang,
            "seo_title": seo_title,
            "seo_desc": seo_desc
        })
    except Exception as e:
        logger.error(f"获取博客列表失败: {e}", exc_info=True)
        return templates.TemplateResponse("blog.html", {
            "request": request,
            "posts": [],
            "featured_post": None,
            "popular_posts": [],
            "categories": [],
            "current_category": category,
            "current_page": 1,
            "total_pages": 1,
            "total": 0,
            "lang": lang,
            "seo_title": "IMVU Creator Blog",
            "seo_desc": "IMVU Creator tips and insights"
        })


@router.get("/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str, db: Session = Depends(get_db)):
    """
    博客文章详情页
    """
    from app.models import BlogPost
    
    lang = request.headers.get("Accept-Language", "en")
    lang = 'zh' if lang.startswith('zh') else ('fr' if lang.startswith('fr') else 'en')
    
    try:
        # 获取文章
        post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
        
        if not post or (not post.is_published):
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 增加浏览量
        post.view_count += 1
        db.commit()
        
        # 获取相关文章（同分类）
        related_posts = db.query(BlogPost).filter(
            BlogPost.is_published == True,
            BlogPost.category == post.category,
            BlogPost.id != post.id
        ).order_by(desc(BlogPost.published_at)).limit(3).all()
        
        # 计算阅读时间
        content = post.get_content(lang)
        reading_time = get_reading_time(content)
        
        # SEO
        seo_title = post.meta_title or post.get_title(lang)
        seo_desc = post.meta_description or post.get_excerpt(lang, 160)
        base_url = config.APP_BASE_URL or "https://imvucreators.com"
        
        # JSON-LD 结构化数据
        json_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.get_title(lang),
            "description": seo_desc,
            "author": {
                "@type": "Organization",
                "name": post.author
            },
            "publisher": {
                "@type": "Organization",
                "name": "IMVU Analytics",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{base_url}/static/logo.png"
                }
            },
            "datePublished": post.published_at.isoformat() if post.published_at else post.created_at.isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{base_url}/blog/{slug}"
            }
        }
        
        return templates.TemplateResponse("blog_post.html", {
            "request": request,
            "post": post,
            "related_posts": related_posts,
            "reading_time": reading_time,
            "lang": lang,
            "seo_title": seo_title,
            "seo_desc": seo_desc,
            "json_ld": json_ld,
            "base_url": base_url
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取博客文章失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load article")


# ==================== API 路由 ====================

@router.get("/api/posts", response_model=BlogListResponse)
async def get_blog_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    API: 获取博客文章列表（已发布）
    """
    from app.models import BlogPost
    
    try:
        query = db.query(BlogPost).filter(BlogPost.is_published == True)
        
        if category:
            query = query.filter(BlogPost.category == category)
        
        total = query.count()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        posts = query.order_by(desc(BlogPost.published_at), desc(BlogPost.created_at)) \
                     .offset((page - 1) * per_page) \
                     .limit(per_page) \
                     .all()
        
        # 获取分类统计
        categories = db.query(
            BlogPost.category,
            func.count(BlogPost.id).label('count')
        ).filter(
            BlogPost.is_published == True,
            BlogPost.category.isnot(None)
        ).group_by(BlogPost.category).all()
        
        category_list = [{"name": c.category or "Uncategorized", "count": c.count} for c in categories]
        
        return {
            "posts": posts,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "categories": category_list
        }
    except Exception as e:
        logger.error(f"API获取博客列表失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Failed to fetch posts"}
        )


@router.get("/api/posts/{slug}")
async def get_blog_post(slug: str, db: Session = Depends(get_db)):
    """
    API: 获取单篇文章详情
    """
    from app.models import BlogPost
    
    try:
        post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
        
        if not post:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Post not found"}
            )
        
        if not post.is_published:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"success": False, "message": "Post not published"}
            )
        
        # 增加浏览量
        post.view_count += 1
        db.commit()
        
        return {
            "success": True,
            "post": post
        }
    except Exception as e:
        logger.error(f"API获取博客文章失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Failed to fetch post"}
        )


# ==================== 管理后台 API ====================

@router.post("/api/admin/posts", response_model=BlogPostResponse)
async def create_blog_post(
    post_data: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    创建博客文章（仅管理员）
    """
    from app.models import BlogPost
    
    try:
        # 检查slug唯一性
        if slug_exists(db, post_data.slug):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Slug already exists"}
            )
        
        # 创建文章
        post = BlogPost(
            slug=post_data.slug,
            title_en=post_data.title_en,
            title_zh=post_data.title_zh,
            title_fr=post_data.title_fr,
            content_en=post_data.content_en,
            content_zh=post_data.content_zh,
            content_fr=post_data.content_fr,
            excerpt_en=post_data.excerpt_en,
            excerpt_zh=post_data.excerpt_zh,
            excerpt_fr=post_data.excerpt_fr,
            category=post_data.category,
            cover_image=post_data.cover_image,
            meta_title=post_data.meta_title,
            meta_description=post_data.meta_description,
            author=post_data.author,
            is_published=post_data.is_published,
            is_featured=post_data.is_featured,
            published_at=datetime.utcnow() if post_data.is_published else None
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        logger.info(f"管理员 {current_user.get('id')} 创建了博客文章: {post.slug}")
        
        return post
    except Exception as e:
        db.rollback()
        logger.error(f"创建博客文章失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Failed to create post"}
        )


@router.put("/api/admin/posts/{post_id}")
async def update_blog_post(
    post_id: int,
    post_data: BlogPostUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    更新博客文章（仅管理员）
    """
    from app.models import BlogPost
    
    try:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        
        if not post:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Post not found"}
            )
        
        # 更新字段
        update_data = post_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(post, key, value)
        
        # 如果设置为发布且还没有发布时间
        if post.is_published and not post.published_at:
            post.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(post)
        
        logger.info(f"管理员 {current_user.get('id')} 更新了博客文章: {post.slug}")
        
        return {"success": True, "post": post}
    except Exception as e:
        db.rollback()
        logger.error(f"更新博客文章失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Failed to update post"}
        )


@router.delete("/api/admin/posts/{post_id}")
async def delete_blog_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    删除博客文章（仅管理员）
    """
    from app.models import BlogPost
    
    try:
        post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
        
        if not post:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Post not found"}
            )
        
        slug = post.slug
        db.delete(post)
        db.commit()
        
        logger.info(f"管理员 {current_user.get('id')} 删除了博客文章: {slug}")
        
        return {"success": True, "message": "Post deleted"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除博客文章失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Failed to delete post"}
        )


@router.get("/api/admin/posts", response_model=BlogListResponse)
async def get_admin_blog_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status", description="published/draft/all"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    获取所有博客文章（仅管理员，包含草稿）
    """
    from app.models import BlogPost
    
    try:
        query = db.query(BlogPost)
        
        if status_filter == "published":
            query = query.filter(BlogPost.is_published == True)
        elif status_filter == "draft":
            query = query.filter(BlogPost.is_published == False)
        
        if category:
            query = query.filter(BlogPost.category == category)
        
        total = query.count()
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        
        posts = query.order_by(desc(BlogPost.created_at)) \
                     .offset((page - 1) * per_page) \
                     .limit(per_page) \
                     .all()
        
        # 获取分类统计
        categories = db.query(
            BlogPost.category,
            func.count(BlogPost.id).label('count')
        ).filter(BlogPost.category.isnot(None)).group_by(BlogPost.category).all()
        
        category_list = [{"name": c.category or "Uncategorized", "count": c.count} for c in categories]
        
        return {
            "posts": posts,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "categories": category_list
        }
    except Exception as e:
        logger.error(f"获取管理博客列表失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Failed to fetch posts"}
        )
