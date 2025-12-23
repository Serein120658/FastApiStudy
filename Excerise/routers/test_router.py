from fastapi import APIRouter

router = APIRouter(
    prefix="/api",  # 路由前缀
    tags=["测试APIRouter"],  # 标签 作用主要是 在接口文档中显示
)

@router.get("/test/apirouter")
async def test_apirouter():
    return {"message": "Hello World"}


@router.get("/test/apirouter/{id}")
async def test_apirouter_id(id: int):
    return {"id": id}


# 使用prefix 前缀     /api/test/apirouter
# 在上面注册路由的时候可以添加