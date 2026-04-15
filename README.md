# 基于YOLO的水果识别称重系统

## 项目简介

本项目是一个面向水果零售场景的自动化识别与结算系统，通过结合目标检测（YOLO）与重量传感器，实现水果的自动识别、称重及价格计算，并通过Web界面进行展示与交互。

系统整体采用“图像识别 + 重量检测 + Web服务”的设计思路，能够模拟真实购物流程，包括识别商品、加入购物列表、结算与数据记录等功能。

---

## 功能特点

* 🍎 基于YOLO模型的水果类别识别
* ⚖️ 实时重量读取与价格计算
* 🛒 支持购物流程（添加、删除、结算）
* 📊 交易数据记录（SQLite数据库）
* 🌐 基于Flask的Web可视化界面
* 🔐 简单后台管理功能

---

## 项目结构

```
.
├── config.py              # 系统配置文件（模型路径、参数等）
├── main.py                # 项目主入口
│
├── core/                  # 核心功能模块
│   ├── all_hardware.py    # 硬件统一调度
│   ├── device_service.py  # 设备服务层（封装识别与硬件调用）
│   ├── weight_engine.py   # 重量数据处理逻辑
│
├── data/                  # 数据与状态管理
│   ├── best.pt            # YOLO权重文件（需自行提供）
│   ├── datas.db           # SQLite数据库
│   ├── my_sql.py          # 数据库操作封装
│   ├── runtime_state.py   # 运行时状态管理
│   ├── session_data.py    # 会话/购物流程数据
│   ├── test.jpg           # 测试图片
│   ├── 数据库初始化.py     # 数据库初始化脚本
│
├── static/                # 静态资源
│   └── fake_qr.jpg        # 模拟支付二维码
│
├── templates/             # 前端页面模板（Flask）
│   ├── index.html         # 主页面
│   ├── login.html         # 登录页面
│   ├── pay.html           # 支付页面
│   ├── admin_menu.html    # 后台菜单
│   ├── admin_data.html    # 数据管理页面
│   ├── admin_price.html   # 价格管理页面
│
└── web/                   # Web层（路由 + 业务逻辑）
    ├── web_routes.py      # 前端路由
    ├── web_service.py     # 前端业务逻辑
    ├── admin_routes.py    # 后台路由
    ├── admin_service.py   # 后台业务逻辑
```

---

## 运行说明

### 1. 环境要求
- Python 3.8 及以上

### 2. 依赖说明
本项目未提供 `requirements.txt`，需要根据代码自行安装依赖。

已知核心依赖如下：

```bash
pip install flask opencv-python torch numpy ultralytics
````

说明：

* `ultralytics`：用于加载YOLO模型（.pt）
* `opencv-python`：用于图像处理
* `flask`：Web框架
* `torch`：模型推理依赖

> 若运行报错，请根据 `import` 缺失提示补充安装

### 3. 启动项目

```bash
python main.py
```

启动后，在浏览器访问：

```
http://127.0.0.1:5000
```

---

## 模型说明

本项目使用YOLO模型进行水果识别。

* 使用的是训练得到的 `.pt` 权重文件（在 `config.py` 中配置）
* 未导出为ONNX格式（实际测试中两者推理速度差异不明显，因此直接使用 `.pt`）

### 权重文件放置说明

请将 `best.pt` 放置在如下位置（或与配置文件保持一致）：

```
/data/best.pt
```

并在 `config.py` 中确认或修改对应路径（按照规则一版无需修改），例如：

```python
MODEL_PATH = os.path.join(DATA_DIR, r"best.pt")
```

---

### 切换为ONNX模型（可选）

如果需要使用ONNX模型，需要进行以下修改：

1. 将模型导出为 `.onnx`
2. 修改 `config.py` 中的模型路径，例如：

```python
MODEL_PATH = os.path.join(DATA_DIR, r"best.onnx")
```

3. 修改模型加载方式（通常在识别相关代码中，如 `device_service.py` 或检测模块）

   * `.pt`：使用 `ultralytics` 加载
   * `.onnx`：如使用YOLO模型导出的onnx可直接使用 `ultralytics` 加载，其他类型请自行测试


---

## 电子秤数据接口说明

由于硬件设备环境限制，本项目未提供电子秤具体驱动代码，但对数据格式有如下约定：

* 启动后需进行初始化与去皮操作
* 初始化完成后输出：

```
OK
```

* 随后持续输出重量数据，每行一个数值
* 数据格式示例：

```
123.45
98.2
150
```

* 单位：克（g）
* 不包含单位字符或其他内容（必须为纯数字）

系统会按行读取串口/输入流数据并进行解析。

---

## 数据库说明

系统使用SQLite进行数据存储，主要包括：

* 用户数据（user_data）
* 交易数据（transaction_data）
* 水果信息（fruit_data）
* 管理员数据（admin_data）

支持记录完整购物流程，包括每次识别、重量、价格及最终结算信息。

### 数据库初始化说明

项目在 `data` 目录下提供了数据库初始化脚本（如：`数据库初始化.py`）：

* 直接运行该脚本可生成作者使用的数据库结构与初始数据
* 若需要适配自己的项目（如修改水果种类或价格），可以编辑脚本中的建表或插入数据部分

示例：

```bash
python data/数据库初始化.py
```

建议根据实际需求调整初始数据内容，以匹配自己的训练模型类别。

---

### 其他说明

config中硬件设备编号管理根据实际情况修改

```bash
CAMERA_NO = 0           # 相机编号
SERIAL_PORT = "COM3"    # 电子秤串口编号
```

其他业务参数均在注释中说明

```bash
SAME_WEIGHT_TIMES = 3   # 称重时相同重量次数
WEIGHT_THRESHOLD = 25   # 重量阈值（超过或恢复才开始后续称重）
TIMEOUT_SECONDS = 60    # 超时时间
PAGE_SIZE = 10          # 数据显示界面一页显示数量
```

---

## 注意事项

* 本项目为毕业设计项目，主要用于学习与分享
* 硬件相关部分需根据实际设备进行适配
* 模型与电子秤代码未提供，仅保留接口规范

---

## 后续优化方向

* 提升模型识别精度
* 增加更多水果类别
* 优化前端交互体验
* 接入真实支付系统

---

## License

本项目仅供学习交流使用。
如有疑问，暂无联系方式
