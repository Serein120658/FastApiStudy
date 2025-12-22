from fastapi import FastAPI, Depends, Query, HTTPException, Header, Form
import secrets
from datetime import datetime, timedelta
app = FastAPI()

# 这是一个依赖函数
def get_current_user():
    return {"username": "张三", "id": 1}

# 在路径操作中使用依赖
@app.get("/user")
def read_user(user: dict = Depends(get_current_user)):
    return {"message": f"你好, {user['username']}"}


# 依赖函数可以接收参数
def pagination(page:int = Query(1, title="页码", ge = 1), size:int = Query(10, title="每页数量", ge=1, le=100)):
    skip = (page - 1) * size
    return {"skip": skip, "size": size}

# 依赖也带参数
@app.get("/items/depends")
async def list_items(pagination_params: dict = Depends(pagination)):
    return {
        "page": pagination_params,
        "data": [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
            {"id": 3, "name": "item3"},
        ]
    }




# ========== 基础依赖示例 ==========

# 这是一个依赖函数
def get_current_user():
    return {"username": "张三", "id": 1}


# 在路径操作中使用依赖
@app.get("/user")
def read_user(user: dict = Depends(get_current_user)):
    return {"message": f"你好, {user['username']}"}


# 依赖函数可以接收参数
def pagination(page: int = Query(1, title="页码", ge=1), size: int = Query(10, title="每页数量", ge=1, le=100)):
    skip = (page - 1) * size
    return {"skip": skip, "size": size}


# 依赖也带参数
@app.get("/items/depends")
async def list_items(pagination_params: dict = Depends(pagination)):
    return {
        "page": pagination_params,
        "data": [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
            {"id": 3, "name": "item3"},
        ]
    }


# ========== Token 认证系统 ==========

# 模拟用户数据库
fake_users_db = {
    "zhangsan": {
        "username": "zhangsan",
        "password": "password123",  # 实际项目中应该存储加密后的密码
        "email": "zhangsan@example.com",
        "full_name": "张三",
        "id": 1
    },
    "lisi": {
        "username": "lisi",
        "password": "123456",
        "email": "lisi@example.com",
        "full_name": "李四",
        "id": 2
    }
}

# 模拟 token 存储
# 格式: {token: {"username": xxx, "expires": xxx}}
active_tokens = {}


def generate_token() -> str:
    """生成随机 token"""
    return secrets.token_urlsafe(32)


def create_token(username: str) -> str:
    """创建并存储 token"""
    token = generate_token()
    expires = datetime.now() + timedelta(minutes=30)  # 30分钟过期

    active_tokens[token] = {
        "username": username,
        "expires": expires
    }

    return token


def verify_token(token: str) -> dict:
    """验证 token 并返回用户信息"""
    token_data = active_tokens.get(token)

    if not token_data:
        raise HTTPException(status_code=401, detail="Token 无效")

    # 检查是否过期
    if datetime.now() > token_data["expires"]:
        del active_tokens[token]
        raise HTTPException(status_code=401, detail="Token 已过期")

    # 返回用户信息
    username = token_data["username"]
    user = fake_users_db.get(username)

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


# 创建接口生成 token
@app.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    登录接口 - 生成 token

    测试账号:
    - zhangsan / password123
    - lisi / 123456
    """
    # 验证用户是否存在
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    if user["password"] != password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成 token
    token = create_token(username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": username,
        "message": "登录成功"
    }


# ========== 嵌套依赖练习 ==========

# 第一层依赖：获取 token
def get_token(authorization: str = Header(..., alias="Authorization")):
    """
    从 Authorization header 中提取 token
    注意: alias="Authorization" 确保匹配标准的 HTTP header 名称
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    return authorization[7:]  # 去掉 "Bearer " 前缀

# 第二层依赖：验证 token 并返回用户
def verify_current_user(token: str = Depends(get_token)):
    # 使用我们的 verify_token 函数验证
    user = verify_token(token)
    return user

# 第三层依赖：验证是否是管理员
def is_admin(user: dict = Depends(verify_current_user)):
    if user["id"] != 1:  # 只有 zhangsan (id=1) 是管理员
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return user

# 路径中使用
@app.get("/admin/dashboard")
async def admin_dashboard(user: dict = Depends(is_admin)):
    return {
        "message": f"欢迎管理员 {user['full_name']}",
        "username": user["username"],
        "email": user["email"]
    }


# ========== 其他受保护的接口 ==========

@app.get("/profile")
async def get_profile(user: dict = Depends(verify_current_user)):
    """获取当前用户信息 - 需要登录"""
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"]
    }


@app.post("/logout")
async def logout(token: str = Depends(get_token)):
    """登出 - 使 token 失效"""
    if token in active_tokens:
        del active_tokens[token]
        return {"message": "登出成功"}
    else:
        raise HTTPException(status_code=401, detail="Token 无效")



# 类依赖
class CommonQueryParams:
    def __init__(
        self,
        q: str = Query(None, description="搜索关键词"),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
    ):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/search")
def search_items(commons: CommonQueryParams = Depends()):
    response = {
        "query": commons.q,
        "skip": commons.skip,
        "limit": commons.limit
    }
    return response
