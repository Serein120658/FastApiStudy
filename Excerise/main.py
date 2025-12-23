from fastapi import FastAPI,APIRouter
from fastapi import Path
from routers import test_router


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# 多个路径参数
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# 路径参数
@app.get("/items/{item_id}")
async def get_item(
        item_id: int = Path(
            ...,  # ... 表示必填
            title="商品ID",
            description="The ID of the item",
            ge=1, # 大于等于1
            le=1000  #小于等于1000
        )
):
    return {"item_id": item_id}

@app.get("/products")
async def list_products(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# 引入test_router.py中的路由模块  后续的路由都会被添加到app中
# 有点类似java中的controller   这样的好处就是 路由模块可以抽离出来，避免main.py中的路由代码过多
app.router.include_router(test_router.router)
