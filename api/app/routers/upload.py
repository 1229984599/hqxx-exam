import os
import httpx
import aiofiles
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.config import settings
from app.dependencies.auth import get_current_active_admin

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post("/image", summary="上传图片到CDN")
async def upload_image_to_cdn(
    image: UploadFile = File(...),
    folder: Optional[str] = Form("tinymce"),
    current_admin = Depends(get_current_active_admin)
):
    """
    上传图片到CDN
    支持从TinyMCE编辑器粘贴上传
    """
    # 验证文件类型
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    
    # 验证文件大小
    if image.size and image.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    
    # 检查CDN配置
    if not settings.IMAGE_CDN_TOKEN:
        raise HTTPException(status_code=500, detail="图床配置未设置")
    
    try:
        # 读取文件内容
        file_content = await image.read()

        # 准备上传到CDN的数据
        files = {
            'image': (image.filename, file_content, image.content_type)
        }
        data = {
            'folder': folder
        }

        # 设置请求头
        headers = {
            'token': settings.IMAGE_CDN_TOKEN
        }

        # 上传到CDN
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.IMAGE_CDN_URL,
                files=files,
                data=data,
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="CDN上传失败")

            result = response.json()

            if result.get('code') != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"CDN上传失败: {result.get('msg', '未知错误')}"
                )

            # 返回成功结果
            return {
                "success": True,
                "message": "上传成功",
                "data": {
                    "url": result['data']['url'],
                    "id": result['data']['id'],
                    "name": result['data']['name'],
                    "size": result['data']['size'],
                    "mime": result['data']['mime']
                }
            }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"网络请求失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/image/base64", summary="上传Base64图片到CDN")
async def upload_base64_image_to_cdn(
    image_data: str = Form(...),
    filename: Optional[str] = Form("pasted_image.png"),
    folder: Optional[str] = Form("tinymce"),
    current_admin = Depends(get_current_active_admin)
):
    """
    上传Base64编码的图片到CDN
    主要用于处理粘贴的图片
    """
    import base64
    import io
    from PIL import Image
    
    try:
        # 解析Base64数据
        if image_data.startswith('data:image/'):
            # 移除data:image/xxx;base64,前缀
            header, encoded = image_data.split(',', 1)
            content_type = header.split(';')[0].split(':')[1]
        else:
            encoded = image_data
            content_type = 'image/png'
        
        # 解码Base64
        image_bytes = base64.b64decode(encoded)
        
        # 验证是否为有效图片
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="无效的图片数据")
        
        # 验证文件大小
        if len(image_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        # 检查CDN配置
        if not settings.IMAGE_CDN_TOKEN:
            raise HTTPException(status_code=500, detail="图床配置未设置")
        
        # 准备上传到CDN的数据
        files = {
            'image': (filename, image_bytes, content_type)
        }
        data = {
            'folder': folder
        }

        # 设置请求头
        headers = {
            'token': settings.IMAGE_CDN_TOKEN
        }

        # 上传到CDN
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.IMAGE_CDN_URL,
                files=files,
                data=data,
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="CDN上传失败")

            result = response.json()

            if result.get('code') != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"CDN上传失败: {result.get('msg', '未知错误')}"
                )

            # 返回成功结果
            return {
                "success": True,
                "message": "上传成功",
                "data": {
                    "url": result['data']['url'],
                    "id": result['data']['id'],
                    "name": result['data']['name'],
                    "size": result['data']['size'],
                    "mime": result['data']['mime']
                }
            }

    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail="无效的Base64数据")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"网络请求失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
