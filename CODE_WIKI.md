# FastAPI Beyond CRUD - Code Wiki

## 1. 项目概览

FastAPI Beyond CRUD 是一个基于 FastAPI 框架开发的书籍评论 Web 服务，专注于超越基本 CRUD 操作的高级开发概念。

**主要功能：**
- 书籍管理（创建、读取、更新、删除）
- 用户认证与授权（注册、登录、密码重置、邮箱验证）
- 评论管理（添加、删除评论）
- 标签管理（创建标签、为书籍添加标签）
- 异步任务处理（邮件发送）

**技术栈：**
- Python 3.10+
- FastAPI
- PostgreSQL
- Redis
- Celery
- SQLModel

## 2. 目录结构

```
├── migrations/              # 数据库迁移文件
│   ├── versions/            # 迁移版本
│   ├── README
│   ├── env.py
│   └── script.py.mako
├── src/                     # 源代码目录
│   ├── auth/                # 认证模块
│   │   ├── __init__.py
│   │   ├── dependencies.py  # 依赖注入
│   │   ├── routes.py        # 路由
│   │   ├── schemas.py       # 数据模型
│   │   ├── service.py       # 业务逻辑
│   │   └── utils.py         # 工具函数
│   ├── books/               # 书籍模块
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── db/                  # 数据库模块
│   │   ├── __init__.py
│   │   ├── main.py          # 数据库连接
│   │   ├── models.py        # 数据库模型
│   │   └── redis.py         # Redis 连接
│   ├── reviews/             # 评论模块
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── tags/                # 标签模块
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── tests/               # 测试模块
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   └── test_book.py
│   ├── __init__.py          # 应用入口
│   ├── celery_tasks.py      # Celery 任务
│   ├── config.py            # 配置文件
│   ├── errors.py            # 错误处理
│   ├── mail.py              # 邮件服务
│   └── middleware.py        # 中间件
├── .env.example             # 环境变量示例
├── .gitignore
├── Dockerfile               # Docker 配置
├── README.md
├── alembic.ini              # Alembic 配置
├── compose.yml              # Docker Compose 配置
├── requirements.txt         # 依赖文件
└── runworker.sh             # Celery  worker 启动脚本
```

## 3. 系统架构

### 3.1 架构概览

本项目采用分层架构设计，主要包括以下层次：

1. **API 层**：处理 HTTP 请求和响应，定义路由和端点
2. **服务层**：实现业务逻辑，处理数据操作
3. **数据层**：定义数据模型和数据库操作
4. **基础设施层**：提供配置、认证、邮件等基础服务

### 3.2 核心流程

**用户认证流程：**
1. 用户注册 → 邮箱验证 → 登录获取令牌
2. 访问受保护资源 → 令牌验证 → 授权检查

**书籍管理流程：**
1. 创建书籍 → 关联用户 → 存储数据库
2. 查询书籍 → 应用过滤和排序 → 返回结果
3. 更新/删除书籍 → 权限检查 → 执行操作

**评论流程：**
1. 添加评论 → 验证用户和书籍 → 存储评论
2. 删除评论 → 权限检查 → 执行删除

**标签流程：**
1. 创建标签 → 验证唯一性 → 存储标签
2. 为书籍添加标签 → 验证书籍存在 → 关联标签

## 4. 核心模块

### 4.1 认证模块 (auth)

**功能：**
- 用户注册与邮箱验证
- 用户登录与令牌生成
- 密码重置
- 令牌管理与验证
- 权限控制

**主要组件：**
- `UserService`：处理用户相关业务逻辑
- `AccessTokenBearer`：访问令牌验证
- `RefreshTokenBearer`：刷新令牌验证
- `RoleChecker`：角色权限检查

### 4.2 书籍模块 (books)

**功能：**
- 书籍的 CRUD 操作
- 按用户查询书籍
- 书籍详情查询

**主要组件：**
- `BookService`：处理书籍相关业务逻辑

### 4.3 评论模块 (reviews)

**功能：**
- 为书籍添加评论
- 查询评论
- 删除评论

**主要组件：**
- `ReviewService`：处理评论相关业务逻辑

### 4.4 标签模块 (tags)

**功能：**
- 创建标签
- 为书籍添加标签
- 更新和删除标签

**主要组件：**
- `TagService`：处理标签相关业务逻辑

### 4.5 数据库模块 (db)

**功能：**
- 数据库连接管理
- 数据模型定义
- Redis 连接管理

**主要组件：**
- `get_session`：获取数据库会话
- 数据模型：`User`, `Book`, `Review`, `Tag`, `BookTag`

### 4.6 任务队列模块 (celery_tasks)

**功能：**
- 异步邮件发送

**主要组件：**
- `send_email`：异步发送邮件任务

## 5. 数据库模型

### 5.1 User 模型

```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False), exclude=True
    )
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
```

### 5.2 Book 模型

```python
class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List[Tag] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
```

### 5.3 Review 模型

```python
class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(lt=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")
```

### 5.4 Tag 模型

```python
class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
```

### 5.5 BookTag 模型 (关联表)

```python
class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)
```

## 6. API 接口

### 6.1 认证接口

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/v1/auth/signup` | POST | 用户注册 | 无 |
| `/api/v1/auth/verify/{token}` | GET | 邮箱验证 | 无 |
| `/api/v1/auth/login` | POST | 用户登录 | 无 |
| `/api/v1/auth/refresh_token` | GET | 刷新访问令牌 | 刷新令牌 |
| `/api/v1/auth/me` | GET | 获取当前用户信息 | 访问令牌 |
| `/api/v1/auth/logout` | GET | 登出（使令牌失效） | 访问令牌 |
| `/api/v1/auth/password-reset-request` | POST | 密码重置请求 | 无 |
| `/api/v1/auth/password-reset-confirm/{token}` | POST | 确认密码重置 | 无 |
| `/api/v1/auth/send_mail` | POST | 发送邮件 | 无 |

### 6.2 书籍接口

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/v1/books/` | GET | 获取所有书籍 | 访问令牌 |
| `/api/v1/books/user/{user_uid}` | GET | 获取用户提交的书籍 | 访问令牌 |
| `/api/v1/books/` | POST | 创建书籍 | 访问令牌 |
| `/api/v1/books/{book_uid}` | GET | 获取书籍详情 | 访问令牌 |
| `/api/v1/books/{book_uid}` | PATCH | 更新书籍 | 访问令牌 |
| `/api/v1/books/{book_uid}` | DELETE | 删除书籍 | 访问令牌 |

### 6.3 评论接口

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/v1/reviews/` | GET | 获取所有评论 | 管理员 |
| `/api/v1/reviews/{review_uid}` | GET | 获取评论详情 | 访问令牌 |
| `/api/v1/reviews/book/{book_uid}` | POST | 为书籍添加评论 | 访问令牌 |
| `/api/v1/reviews/{review_uid}` | DELETE | 删除评论 | 访问令牌 |

### 6.4 标签接口

| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/api/v1/tags/` | GET | 获取所有标签 | 访问令牌 |
| `/api/v1/tags/` | POST | 创建标签 | 访问令牌 |
| `/api/v1/tags/book/{book_uid}/tags` | POST | 为书籍添加标签 | 访问令牌 |
| `/api/v1/tags/{tag_uid}` | PUT | 更新标签 | 访问令牌 |
| `/api/v1/tags/{tag_uid}` | DELETE | 删除标签 | 访问令牌 |

## 7. 关键类与函数

### 7.1 UserService 类

**功能**：处理用户相关的业务逻辑

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `get_user_by_email` | 通过邮箱获取用户 | email: str, session: AsyncSession | User 对象或 None |
| `user_exists` | 检查用户是否存在 | email: str, session: AsyncSession | bool |
| `create_user` | 创建新用户 | user_data: UserCreateModel, session: AsyncSession | User 对象 |
| `update_user` | 更新用户信息 | user: User, user_data: dict, session: AsyncSession | User 对象 |

### 7.2 BookService 类

**功能**：处理书籍相关的业务逻辑

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `get_all_books` | 获取所有书籍 | session: AsyncSession | List[Book] |
| `get_user_books` | 获取用户的书籍 | user_uid: str, session: AsyncSession | List[Book] |
| `get_book` | 获取单个书籍 | book_uid: str, session: AsyncSession | Book 对象或 None |
| `create_book` | 创建书籍 | book_data: BookCreateModel, user_uid: str, session: AsyncSession | Book 对象 |
| `update_book` | 更新书籍 | book_uid: str, update_data: BookUpdateModel, session: AsyncSession | Book 对象或 None |
| `delete_book` | 删除书籍 | book_uid: str, session: AsyncSession | dict 或 None |

### 7.3 ReviewService 类

**功能**：处理评论相关的业务逻辑

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `add_review_to_book` | 为书籍添加评论 | user_email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession | Review 对象 |
| `get_review` | 获取单个评论 | review_uid: str, session: AsyncSession | Review 对象或 None |
| `get_all_reviews` | 获取所有评论 | session: AsyncSession | List[Review] |
| `delete_review_to_from_book` | 删除评论 | review_uid: str, user_email: str, session: AsyncSession | None |

### 7.4 TagService 类

**功能**：处理标签相关的业务逻辑

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `get_tags` | 获取所有标签 | session: AsyncSession | List[Tag] |
| `add_tags_to_book` | 为书籍添加标签 | book_uid: str, tag_data: TagAddModel, session: AsyncSession | Book 对象 |
| `get_tag_by_uid` | 通过 UID 获取标签 | tag_uid: str, session: AsyncSession | Tag 对象或 None |
| `add_tag` | 创建标签 | tag_data: TagCreateModel, session: AsyncSession | Tag 对象 |
| `update_tag` | 更新标签 | tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession | Tag 对象 |
| `delete_tag` | 删除标签 | tag_uid: str, session: AsyncSession | None |

### 7.5 认证工具函数

| 函数 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `create_access_token` | 创建访问令牌 | user_data: dict, refresh: bool = False, expiry: timedelta = None | str (JWT 令牌) |
| `verify_password` | 验证密码 | password: str, password_hash: str | bool |
| `generate_passwd_hash` | 生成密码哈希 | password: str | str |
| `create_url_safe_token` | 创建 URL 安全令牌 | data: dict | str |
| `decode_url_safe_token` | 解码 URL 安全令牌 | token: str | dict |

## 8. 依赖关系

### 8.1 核心依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| fastapi[standard] | 0.111.0 | Web 框架 |
| sqlmodel | 0.0.18 | ORM 框架 |
| alembic | 1.13.1 | 数据库迁移 |
| celery | 5.4.0 | 任务队列 |
| redis | 5.0.7 | 缓存和消息代理 |
| fastapi-mail | 1.4.1 | 邮件发送 |
| PyJWT | 2.8.0 | JWT 令牌处理 |
| passlib | 1.7.4 | 密码哈希 |
| pydantic-settings | 2.4.0 | 配置管理 |

### 8.2 开发依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| pytest | - | 测试框架 |
| ruff | 0.4.8 | 代码检查 |
| isort | 5.13.2 | 导入排序 |

## 9. 运行与部署

### 9.1 本地开发

1. **克隆项目**：
   ```bash
   git clone https://github.com/jod35/fastapi-beyond-CRUD.git
   cd fastapi-beyond-CRUD/
   ```

2. **创建虚拟环境**：
   ```bash
   python3 -m venv env
   source env/bin/activate  # Linux/Mac
   # 或
   env\Scripts\activate  # Windows
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写必要的配置
   ```

5. **运行数据库迁移**：
   ```bash
   alembic upgrade head
   ```

6. **启动 Celery worker**：
   ```bash
   sh runworker.sh  # Linux/Mac
   # 或
   celery -A src.celery_tasks.c_app worker --loglevel=INFO  # Windows
   ```

7. **启动应用**：
   ```bash
   fastapi dev src/
   ```

### 9.2 Docker 部署

1. **配置环境变量**：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写必要的配置
   ```

2. **启动服务**：
   ```bash
   docker compose up -d
   ```

3. **运行数据库迁移**：
   ```bash
   docker exec -it fastapi-beyond-crud-web-1 alembic upgrade head
   ```

## 10. 测试

### 10.1 运行测试

```bash
pytest
```

### 10.2 测试结构

- `conftest.py`：测试配置和 fixtures
- `test_auth.py`：认证模块测试
- `test_book.py`：书籍模块测试

## 11. 配置

### 11.1 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库连接 URL | - |
| JWT_SECRET | JWT 签名密钥 | - |
| JWT_ALGORITHM | JWT 算法 | - |
| REDIS_URL | Redis 连接 URL | redis://localhost:6379/0 |
| MAIL_USERNAME | 邮件服务用户名 | - |
| MAIL_PASSWORD | 邮件服务密码 | - |
| MAIL_FROM | 发件人邮箱 | - |
| MAIL_PORT | 邮件服务端口 | - |
| MAIL_SERVER | 邮件服务服务器 | - |
| MAIL_FROM_NAME | 发件人名称 | - |
| MAIL_STARTTLS | 是否使用 STARTTLS | True |
| MAIL_SSL_TLS | 是否使用 SSL/TLS | False |
| USE_CREDENTIALS | 是否使用凭据 | True |
| VALIDATE_CERTS | 是否验证证书 | True |
| DOMAIN | 应用域名 | - |
| POSTGRES_USER | PostgreSQL 用户名 | - |
| POSTGRES_PASSWORD | PostgreSQL 密码 | - |
| POSTGRES_DB | PostgreSQL 数据库名 | - |

## 12. 常见问题

### 12.1 邮件发送失败

**原因**：邮件配置不正确或邮件服务不可用

**解决方案**：
- 检查 `.env` 文件中的邮件配置
- 确保邮件服务可用
- 检查网络连接

### 12.2 数据库连接失败

**原因**：数据库配置不正确或数据库服务不可用

**解决方案**：
- 检查 `.env` 文件中的数据库配置
- 确保 PostgreSQL 服务正在运行
- 检查网络连接

### 12.3 令牌验证失败

**原因**：令牌过期或无效

**解决方案**：
- 重新登录获取新令牌
- 检查 JWT 配置

### 12.4 权限错误

**原因**：用户没有足够的权限执行操作

**解决方案**：
- 检查用户角色
- 确保用户已登录
- 检查 API 端点的权限要求

## 13. 总结

FastAPI Beyond CRUD 是一个功能完整的书籍评论 Web 服务，展示了 FastAPI 框架的高级特性和最佳实践。项目采用分层架构设计，包含用户认证、书籍管理、评论管理和标签管理等核心功能，并使用 Celery 处理异步任务。

通过本项目，开发者可以学习到：
- FastAPI 框架的高级用法
- 异步编程模式
- 数据库关系模型设计
- 认证和授权实现
- 任务队列的使用
- Docker 容器化部署

该项目为构建类似的 Web 应用提供了一个良好的参考和起点。