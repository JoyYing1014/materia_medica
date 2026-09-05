# 配置与部署说明

## 本地运行

1. 激活虚拟环境：`./.venv/Scripts/Activate.ps1`。
2. 复制 `.env.example` 中的值到当前进程环境（该文件只作示例，Django 不会自动读取它）。
3. 将完整的 `bert-base-chinese` 模型目录放到 `CHAT_MODEL_DIR` 指向的位置；默认位置是 `models/bert-base-chinese`。
4. 启动 Neo4j 并导入与问答词表匹配的知识图谱，设置 `NEO4J_*`。
5. 执行 `python manage.py migrate`，然后执行 `python manage.py runserver`。

默认模型设备是 `cpu`，因此 Windows、Linux 和 macOS 都不会尝试使用 macOS 专用的 MPS。具备 NVIDIA 驱动与对应 PyTorch 的服务器可将 `CHAT_MODEL_DEVICE` 和 `PREDICT_MODEL_DEVICE` 设为 `cuda`。

## 模型权重文件

`chat/good.bin` 与 `predict/model.pth` 不随代码仓库提供。请从夸克网盘下载：[模型权重下载链接](https://pan.quark.cn/s/b30e6e393a83?pwd=G8b9)，提取码：`G8b9`。

下载后保留文件名，并放到项目根目录下的以下位置：

| 文件 | 放置位置 | 用途 |
| --- | --- | --- |
| `good.bin` | `chat/good.bin` | 聊天问答的问题分类模型权重 |
| `model.pth` | `predict/model.pth` | 图片识别模型权重 |

如需放在其他位置，可分别通过环境变量 `CHAT_MODEL_WEIGHTS` 和 `PREDICT_MODEL_WEIGHTS` 指定绝对或相对路径。聊天问答还需要上述完整的 `bert-base-chinese` 本地模型目录；仅下载 `good.bin` 不足以启用该功能。

缺少 `good.bin` 时聊天问答服务不可用；缺少 `model.pth` 时图片识别功能不可用。建议将这两个二进制权重文件保留在网盘、对象存储或 Git LFS 中，不要作为普通 Git 文件提交到 GitHub。

## 部署前必须调整

- 设置随机的 `DJANGO_SECRET_KEY`，并将 `DJANGO_DEBUG=false`。
- 设置实际域名到 `DJANGO_ALLOWED_HOSTS`，同时配置反向代理的 HTTPS 与静态文件服务。
- 不要把 SQLite 用于多进程或多实例生产部署；迁移到 PostgreSQL 或 MySQL，并改为用环境变量提供数据库连接。
- 将 `MEDIA_ROOT` 放入持久化存储，并限制上传文件的类型与大小。
- 将 BERT 模型和两个 PyTorch 权重文件预置为只读部署资产；不要让 Web 进程在启动或请求时联网下载模型。
- 将 Neo4j、应用数据库和 Web 服务分开运行，使用环境变量或密钥管理服务提供认证信息，并为问答服务设置超时、健康检查和监控。
- 使用生产 WSGI/ASGI 服务与反向代理，不使用 Django 的 `runserver`。
