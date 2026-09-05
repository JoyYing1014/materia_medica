# 配置与部署说明

## 本地运行

1. 激活虚拟环境：`./.venv/Scripts/Activate.ps1`。
2. 复制 `.env.example` 中的值到当前进程环境（该文件只作示例，Django 不会自动读取它）。
3. 将完整的 `bert-base-chinese` 模型目录放到 `CHAT_MODEL_DIR` 指向的位置；默认位置是 `models/bert-base-chinese`。
4. 启动 Neo4j 并导入与问答词表匹配的知识图谱，设置 `NEO4J_*`。
5. 执行 `python manage.py migrate`，然后执行 `python manage.py runserver`。

默认模型设备是 `cpu`，因此 Windows、Linux 和 macOS 都不会尝试使用 macOS 专用的 MPS。具备 NVIDIA 驱动与对应 PyTorch 的服务器可将 `CHAT_MODEL_DEVICE` 和 `PREDICT_MODEL_DEVICE` 设为 `cuda`。

## 部署前必须调整

- 设置随机的 `DJANGO_SECRET_KEY`，并将 `DJANGO_DEBUG=false`。
- 设置实际域名到 `DJANGO_ALLOWED_HOSTS`，同时配置反向代理的 HTTPS 与静态文件服务。
- 不要把 SQLite 用于多进程或多实例生产部署；迁移到 PostgreSQL 或 MySQL，并改为用环境变量提供数据库连接。
- 将 `MEDIA_ROOT` 放入持久化存储，并限制上传文件的类型与大小。
- 将 BERT 模型和两个 PyTorch 权重文件预置为只读部署资产；不要让 Web 进程在启动或请求时联网下载模型。
- 将 Neo4j、应用数据库和 Web 服务分开运行，使用环境变量或密钥管理服务提供认证信息，并为问答服务设置超时、健康检查和监控。
- 使用生产 WSGI/ASGI 服务与反向代理，不使用 Django 的 `runserver`。
