# CampusLink Render 与 Supabase 部署

2026-10-31：新增个人中心“我参与的讨论”，直接查询现有评论，无数据库迁移、回填或环境变量变更。

2026-10-30：固定网站已上线。消息与点赞更新仅新增 `notifications`、`product_likes`、`post_likes` 表；原有账号、商品、帖子、交易、图片不清空，环境变量不变。保持 `CAMPUSLINK_INITIALIZE_SCHEMA=true`，启动时自动创建缺失表。新提醒只针对新版上线后发生的操作。

新版验收补充：双账号预订/处理通知、帖子评论通知、两种点赞与取消、消息权限、未读数量、已读保留和消息详情跳转。网页可见时每 30 秒检查新消息，当前不提供网页关闭后的系统推送。

这是配套前后端的部署源码，基于 Aurowisp/Frontend、Aurowisp/Backend 的原交付成果以及后续集成和论坛开发。具体来源版本记录在 `UPSTREAM.json`。原开发仓库分别维护；这个仓库用于统一部署，不包含本机数据库、上传文件、私密配置或 Git 历史。

## Render 页面选择

选择 Web Service，连接本仓库，分支 `main`。运行环境选择 **Docker**，Dockerfile Path 为 `deploy/Dockerfile`，构建上下文为仓库根目录。不要设置 Root Directory 为 backend；前端也需要参与构建。

Region 可选 Singapore，实例选 **Free**。Health Check Path 为 `/api/health`。Docker Command、Build Command、Start Command 使用 Dockerfile 默认值。若使用 Blueprint，可读取根目录 `render.yaml`，但不要再另建重复服务。

## 环境变量

以下设置只填在 Render 的 Environment 中，不写到 GitHub 文件。数据库 URI 和密码可以分开填写，启动程序负责正确编码特殊字符。

| 名称 | 值 |
| --- | --- |
| `CAMPUSLINK_APP_ENV` | `production` |
| `CAMPUSLINK_DEBUG` | `false` |
| `CAMPUSLINK_AUTO_CREATE_TABLES` | `false` |
| `CAMPUSLINK_SEED_DEMO_DATA` | `false` |
| `CAMPUSLINK_INITIALIZE_SCHEMA` | `true`，在启动阶段单独新增缺失表；不改已有字段和行 |
| `CAMPUSLINK_UPLOAD_STORAGE` | `supabase` |
| `CAMPUSLINK_SUPABASE_STORAGE_BUCKET` | `campuslink-images` |
| `CAMPUSLINK_JWT_SECRET_KEY` | 在本机生成至少 32 字符的随机密钥，或使用 Render 自动生成；不是平台密钥，也不是网站登录密码 |
| `CAMPUSLINK_DATABASE_URL` | 从 Supabase Connect 复制的 Session pooler URI，可保留 `[YOUR-PASSWORD]`；端口为 5432 |
| `CAMPUSLINK_DATABASE_PASSWORD` | 创建 Supabase 项目时保存的数据库密码，原样填写 |
| `CAMPUSLINK_SUPABASE_URL` | 项目 `https://<项目标识>.supabase.co` 地址 |
| `CAMPUSLINK_SUPABASE_STORAGE_KEY` | Supabase 的服务端 Secret key（`sb_secret_…`）；也兼容 legacy `service_role`，不可使用 publishable/anon key |

Dockerfile 已设置编译网页路径。所有网页请求同源访问 `/api`，密钥不会进入前端构建。数据库连接强制使用 TLS（sslmode=require）。Supabase Data API 可以继续关闭，应用通过自己的后端直接连接 PostgreSQL。

启动时会检查或创建私有的 `campuslink-images` 存储桶。若已有桶为公开状态，启动会停止并要求人工确认，不会悄悄修改现有访问权限。新上传图片经格式验证、去元数据、缩放和 WebP 编码后才写入云存储。浏览器通过 `/api/uploads/<随机文件名>.webp` 读取，由后端使用服务端密钥取回图片，不向浏览器发送密钥。

## 数据和免费方案边界

新云数据库初始为空，需要自行注册并发布内容。原电脑的数据和临时公网副本不会自动迁移，也不会被本次部署覆盖；若需要迁移，应单独安排经过备份的数据迁移，不要把本机数据库上传到 GitHub。

Render Free 可能休眠，唤醒需要等待；Supabase Free 有存储和流量额度，也可能因不活跃暂停。实际创建时确认仍为 Free，不开启付费升级。固定平台网址不等于全天候可用保证，课程展示前需人工验证网站能正常打开。

本机目录备份命令不适用于远程存储，会明确拒绝生成不完整备份。云端应分别备份 PostgreSQL 与 Supabase Storage；本轮不声称已经建立云端自动备份。

## 验收

部署完成后检查：健康接口、首页和子路径刷新、注册登录、上传图片、发布商品、收藏预订、论坛与评论。重启 Render 服务后再次读取此前的图片，以验证云端持久化。不能只以首页可打开判断完成。

本机已覆盖上传权限、云存储请求、存储失败、不回退临时磁盘、私有桶、密钥不进入响应、密码特殊字符编码和 TLS 配置。真正的 Docker Linux 构建及真实 Supabase 接口仍须在 Render 首次部署时验证；未取得密钥前不得标记公网部署完成。

来源：[Render Docker](https://render.com/docs/docker)、[Render Free](https://render.com/docs/free)、[Supabase API Keys](https://supabase.com/docs/guides/getting-started/api-keys)、[Supabase Database Connections](https://supabase.com/docs/guides/database/connecting-to-postgres)。
