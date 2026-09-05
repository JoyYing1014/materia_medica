# 本草识别（中药知多少）

一个面向中医药文化学习的 Django Web 项目。项目将药材图片识别、受限范围的知识问答，以及中药历史、典籍、养生等内容放在同一学习入口中，帮助用户从一张图片或一个问题开始了解本草知识。

> 本项目用于中医药文化科普与学习，不提供诊断、处方、用药剂量或个体化医疗建议。如有健康问题，请咨询医生或药师。

## 功能概览

- **图片识别**：上传图片后，使用本地 ResNet50 模型进行 102 类图像分类。
- **中药知识问答**：使用本地 BERT + LSTM 分类模型识别问题类型，并结合 Neo4j 知识图谱回答受限范围内的问题。
- **文化学习内容**：提供中药历史、典籍、人物、养生、中药食材等主题页面。
- **用户功能**：提供注册、登录和退出登录页面。
- **产品方案页**：在 `/case-study/` 展示产品定位、能力边界与后续规划。

## 技术栈

| 范畴       | 使用技术                                                     |
| ---------- | ------------------------------------------------------------ |
| Web 框架   | Django 4.2、Django REST framework                            |
| 图像识别   | PyTorch、Torchvision、Pillow、ResNet50                       |
| 知识问答   | Transformers、本地 `bert-base-chinese`、PyTorch、Pandas、PyAhoCorasick |
| 知识图谱   | Neo4j、py2neo                                                |
| 开发数据库 | SQLite                                                       |

## 快速开始

### 1. 准备环境

- Python 3 与 `pip`
- Neo4j（仅使用中药知识问答功能时需要）
- 完整的本地 `bert-base-chinese` 模型目录（仅使用中药知识问答功能时需要）

在 Windows PowerShell 中创建并激活虚拟环境，然后安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 下载并放置模型权重

模型权重不随仓库提交。请从夸克网盘下载：

- 链接：[模型权重下载](https://pan.quark.cn/s/b30e6e393a83?pwd=G8b9)
- 提取码：`G8b9`

下载后请保留文件名，并放到项目根目录的对应位置：

| 文件        | 目标路径            | 用途                       |
| ----------- | ------------------- | -------------------------- |
| `good.bin`  | `chat/good.bin`     | 聊天问答的问题分类模型权重 |
| `model.pth` | `predict/model.pth` | 图片识别模型权重           |

聊天问答还需要将完整的 `bert-base-chinese` 模型放到 `models/bert-base-chinese`。如果模型放在其他目录，可通过下方环境变量指定路径。

> `chat/good.bin` 约 438 MiB，超过 GitHub 普通 Git 单文件限制；请保持其作为网盘、对象存储或 Git LFS 资产，而不是普通 Git 提交内容。

### 3. 配置环境变量

项目提供了 [`.env.example`](.env.example) 作为配置参考，但 Django **不会自动读取**该文件。请在启动前将所需值设置为进程环境变量，或由部署平台的环境变量/密钥管理功能提供。

本地开发至少应确认以下配置：

| 变量                                | 默认值                     | 说明                                  |
| ----------------------------------- | -------------------------- | ------------------------------------- |
| `DJANGO_SECRET_KEY`                 | 项目内置开发值             | 生产环境必须替换为随机密钥            |
| `DJANGO_DEBUG`                      | `true`                     | 生产环境必须设为 `false`              |
| `DJANGO_ALLOWED_HOSTS`              | 空                         | 以逗号分隔的允许访问域名              |
| `DJANGO_CSRF_TRUSTED_ORIGINS`       | 空                         | 生产环境的可信 HTTPS 来源，以逗号分隔 |
| `CHAT_MODEL_DIR`                    | `models/bert-base-chinese` | 完整 BERT 本地模型目录                |
| `CHAT_MODEL_WEIGHTS`                | `chat/good.bin`            | 聊天分类模型权重路径                  |
| `PREDICT_MODEL_WEIGHTS`             | `predict/model.pth`        | 图片识别模型权重路径                  |
| `NEO4J_URI`                         | `bolt://localhost:7687`    | Neo4j 连接地址                        |
| `NEO4J_USERNAME` / `NEO4J_PASSWORD` | `neo4j` / 空               | Neo4j 账号与密码                      |
| `NEO4J_DATABASE`                    | `neo4j`                    | Neo4j 数据库名称                      |

示例（Windows PowerShell）：

```powershell
$env:DJANGO_SECRET_KEY = 'replace-with-a-long-random-secret'
$env:DJANGO_DEBUG = 'true'
$env:DJANGO_ALLOWED_HOSTS = '127.0.0.1,localhost'
$env:NEO4J_URI = 'bolt://localhost:7687'
$env:NEO4J_USERNAME = 'neo4j'
$env:NEO4J_PASSWORD = 'your-neo4j-password'
```

### 4. 初始化并启动

```powershell
python manage.py migrate
python manage.py runserver
```

启动后访问 <http://127.0.0.1:8000/>。

## 主要页面

| 地址                    | 说明           |
| ----------------------- | -------------- |
| `/`                     | 首页           |
| `/case-study/`          | 产品方案页     |
| `/predict/predictindex` | 图片上传与识别 |
| `/chat/chatindex`       | 中药知识问答   |
| `/user/register`        | 用户注册       |
| `/user/login`           | 用户登录       |

若缺少 `model.pth`，图片识别功能无法加载；若缺少 `good.bin`、BERT 本地模型或 Neo4j 配置，知识问答服务不可用。

## 项目结构

```text
zhongYao/
├── chat/              # 问题分类、知识图谱问答与训练数据
├── predict/           # 图片上传、ResNet50 分类与类别索引
├── user/              # 用户注册、登录及文化内容页面
├── zhongyao/          # Django 项目配置与路由
├── templates/         # 页面模板
├── static/            # 静态资源
├── .env.example       # 环境变量示例
├── DEPLOYMENT.md      # 更完整的部署说明
└── requirements.txt   # Python 依赖
```

## 部署说明

生产部署前，请阅读 [DEPLOYMENT.md](DEPLOYMENT.md)。至少需要完成以下事项：

- 设置新的 `DJANGO_SECRET_KEY`，并将 `DJANGO_DEBUG=false`。
- 设置生产域名到 `DJANGO_ALLOWED_HOSTS` 和 `DJANGO_CSRF_TRUSTED_ORIGINS`，配置 HTTPS、反向代理和静态文件服务。
- 将上传文件目录 `MEDIA_ROOT` 放在持久化存储中，并限制上传文件的类型和大小。
- 将 BERT 模型和两个权重文件作为只读部署资产预置；不要让 Web 进程在启动或请求时下载模型。
- 为生产环境使用 PostgreSQL 或 MySQL，不要以 SQLite 作为多进程或多实例部署的数据库。
- 将 Neo4j、应用数据库和 Web 服务分开运行，并通过环境变量或密钥管理服务提供凭据。
