# Automated Microwave Scatterometer & Digital Twin
# 自动化微波散射计与数字孪生平台

---

**Language / 语言**
- [English](#english)
  - [Part I – User Guide](#part-i--user-guide)
  - [Part II – Developer Guide](#part-ii--developer-guide)
- [中文](#中文)
  - [第一部分 – 用户手册](#第一部分--用户手册)
  - [第二部分 – 开发文档](#第二部分--开发文档)

---

# English

## Overview

This project implements an Automated Microwave Scatterometer with a cloud-based Digital Twin platform. The system enables fully unattended microwave scattering measurements using a PTZ-controlled antenna platform and a Vector Network Analyzer (VNA). Users can remotely configure measurement tasks, monitor execution, visualize results, and interact with a real-time 3D model through a web interface.

**System components:**
- Command Server (Render Cloud)
- Data Server (Render Cloud)
- Instrument Controller (Windows PC)
- PTZ Rotation Platform
- Vector Network Analyzer (VNA)
- Interactive Web Interface
- 3D Digital Twin Visualization

---

## Part I – User Guide

### 1. Accessing the Web Interface

Open the scatterometer web dashboard in a browser.

**Website Address: https://render-a2mh.onrender.com**

The interface contains three major sections:

#### Control Panel

Used to submit measurement commands.

| Parameter | Range | Increment | Description |
|-----------|-------|-----------|-------------|
| VRS | 0°–180° | 10° | Vertical Rotation Steps |
| HRS | 0°–180° | 10° | Horizontal Rotation Steps |
| Auto Shutdown | ON / OFF | — | Power off automatically after measurement |

---

### 2. Starting a Measurement

1. Enter desired VRS value.
2. Enter desired HRS value.
3. Select Auto Shutdown option.
4. Click **Start Measurement**.

The command will be uploaded to the cloud Command Server and automatically downloaded by the instrument controller.

The uploaded command is available at https://render-er7w.onrender.com/data.

**Example:**
```
VRS = 40
HRS = 30
Auto Shutdown = OFF
```
This will perform measurements from (0°, 0°) to (30°, 40°) using the predefined angular step size.

---

### 3. Monitoring Progress

The measurement system automatically:

1. Downloads the command.
2. Rotates antennas to each angle position.
3. Performs S21 measurement.
4. Performs S11 measurement.
5. Saves measurement logs.
6. Uploads processed data to the cloud Data Server.

No user intervention is required once the task starts.

---

### 4. Viewing Measurement Data

The center panel displays:

**Command Parameters**
- Commanded HRS
- Commanded VRS

**Measured Angles**
- Actual H angle
- Actual V angle

**S-Parameter Data**
- S11 Magnitude & Phase
- S21 Magnitude & Phase

**Frequency Response Plots**

Two charts are generated automatically:
- S11 vs Frequency
- S21 vs Frequency

The displayed data updates automatically when new measurement results are uploaded.

Data is also available at https://render-a2mh.onrender.com/data.

---

### 5. Downloading Data

Click **Download Data**.

The system exports all currently stored measurement records from the Data Server. The downloaded file can be opened in Excel, MATLAB, Python, or Origin.

---

### 6. Clearing Data

Before starting a new experiment:

1. Verify that all previous data have been downloaded.
2. Click **Clear Data**.

> ⚠️ This removes all stored measurement records from the Data Server and resets the dashboard.

---

### 7. Digital Twin Visualization

The right-side panel contains a 3D model of the scatterometer. The model updates automatically according to the current horizontal and vertical angles, allowing users to remotely observe antenna orientation during operation.

---

## Part II – Developer Guide

### 1. System Architecture

The project uses a dual-cloud architecture. Separating command and data channels improves reliability and prevents traffic contention.

**Command Path:**
```
User Interface → Command Server → Instrument Controller → Measurement Execution
```

**Data Path:**
```
Instrument Controller → Data Server → User Interface
```

---

### 2. Software Components

#### Cloud Side

**Command Server**
- Receive measurement commands
- Store command file (`command.csv`)
- Provide download API

**Data Server**
- Receive uploaded measurement data
- Store CSV records (`data.csv`)
- Provide data retrieval, clear-data, and download-data APIs

#### Instrument Side

**`download.py`**
Downloads latest command file from Command Server.

**`toplevel1.py`** — Persistent daemon
- Poll Command Server every few seconds
- Detect new commands
- Launch `final.c`

**`final.c`** — Core measurement program
- Control PTZ platform
- Communicate with VNA
- Execute measurement grid
- Generate log files

Main parameters: `vrs`, `hrs`, `shutdown`

```bash
final.exe -vrs 40 -hrs 30
```

**`toplevel2.py`** — Persistent daemon
- Monitor log directory
- Detect new measurement files
- Trigger data processing

**`trans.py`**
Converts raw logs into structured CSV format. Output columns:
```
Target_H, Target_V, H, V, Frequency_Hz, S11_Mag_dB, S11_Phase, S21_Mag_dB, S21_Phase
```

**`upload.py`**
Uploads processed CSV files to Data Server.

---

### 3. Deploying the Render Servers

#### Step 1: Create Render Account

Create an account at https://render.com.

#### Step 2: Create Command Server

Create a new Web Service from your GitHub repository.

- **Runtime:** Python
- **Start Command:**
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

Deploy and record the URL (e.g. `https://render-er7w.onrender.com`).

#### Step 3: Create Data Server

Create another Web Service with the same start command. Deploy and record the URL (e.g. `https://render-a2mh.onrender.com`).

---

### 4. Modifying Server Addresses

Update the URLs in each of the following files:

**`download.py`**
```python
COMMAND_SERVER_URL = "https://your-command-server.onrender.com"
```

**`upload.py`**
```python
DATA_SERVER_URL = "https://your-data-server.onrender.com"
```

**Web Interface (`index.html`)**
```javascript
fetch("https://your-data-server.onrender.com/data")
fetch("https://your-command-server.onrender.com/upload")
```

---

### 5. Running the Instrument Controller

Install Python 3.10+ and required packages:

```bash
pip install requests pandas
```

Run the daemons:

```bash
python toplevel1.py
python toplevel2.py
```

These processes should remain running continuously. For production deployment, configure them as Windows Services or Task Scheduler background tasks.

---

### 6. Directory Structure

```
project/
├── final.c
├── download.py
├── upload.py
├── trans.py
├── toplevel1.py
├── toplevel2.py
├── output.csv
├── log/
├── templates/
│   └── index.html
└── static/
```

---

### 7. Changing Measurement Parameters

Frequency settings are defined as constants in `final.c`:

```c
#define VNA_START_FREQ  5e9   // 5 GHz
#define VNA_STOP_FREQ   8e9   // 8 GHz
#define VNA_NOP         25    // Points
```

To modify: edit the constants, recompile `final.c`, and replace the executable.

---

### 8. Potential Improvements

- **Extended VNA measurement support** — Add support for additional measurement parameters and configurations. Refer to the [Measurement Guide for Anritsu RF and Microwave Handheld VNA Master Instruments](https://dl.cdn-anritsu.com/en-us/test-measurement/files/Manuals/Measurement-Guide/10580-00289N.pdf) for available options.

- **Flexible scan modes** — Replace the fixed grid scan with more general measurement strategies, such as targeting a specific set of angles directly rather than sweeping a rectangular grid.

- **Dwell time before recording** — Allow the antenna to settle at each position for a configurable period before triggering the VNA measurement, reducing the effect of mechanical vibration on data quality.

- **Complex S-parameter output** — Record full complex-valued S-parameters (real and imaginary components) in addition to the current magnitude and phase representation.

---

### Troubleshooting

**No Measurement Starts**
- Check Command Server is reachable
- Check `toplevel1.py` is running
- Check command file was updated

**No Data Appears**
- Check `final.c` generated logs
- Check `trans.py` generated `output.csv`
- Check `upload.py` successfully uploaded data

**Web Dashboard Empty**
- Verify Data Server URL
- Check browser developer console
- Verify Render service status

**3D Model Not Updating**
- Check latest H/V values are uploaded
- Check frontend fetch interval
- Check Three.js rendering errors in console

---

# 中文

## 概述

本项目实现了一套自动化微波散射计与云端数字孪生平台。系统通过 PTZ 云台天线和矢量网络分析仪（VNA），支持全自动无人值守的微波散射测量。用户可通过 Web 界面远程配置测量任务、监控执行状态、查看测量结果，并实时与三维模型交互。

**系统组成：**
- 指令服务器（Render 云端）
- 数据服务器（Render 云端）
- 仪器控制器（Windows PC）
- PTZ 旋转云台
- 矢量网络分析仪（VNA）
- 交互式 Web 界面
- 三维数字孪生可视化

---

## 第一部分 – 用户手册

### 1. 访问 Web 界面

在浏览器中打开散射计 Web 控制台。

**网址：https://render-a2mh.onrender.com**

界面分为三大区域：

#### 控制面板

用于提交测量指令。

| 参数 | 范围 | 步进 | 说明 |
|------|------|------|------|
| VRS | 0°–180° | 10° | 垂直旋转步数 |
| HRS | 0°–180° | 10° | 水平旋转步数 |
| Auto Shutdown | ON / OFF | — | 测量完成后自动关机 |

---

### 2. 启动测量

1. 输入所需的 VRS 值。
2. 输入所需的 HRS 值。
3. 选择 Auto Shutdown 选项。
4. 点击 **Start Measurement**（开始测量）。

指令将上传至云端指令服务器，并由仪器控制器自动下载执行。

已上传的指令可在以下地址查看：https://render-er7w.onrender.com/data

**示例：**
```
VRS = 40
HRS = 30
Auto Shutdown = OFF
```
系统将以预设步长从 (0°, 0°) 扫描至 (30°, 40°)。

---

### 3. 监控进度

测量系统将自动完成以下步骤：

1. 从服务器下载指令。
2. 将天线旋转到每个角度位置。
3. 执行 S21 测量。
4. 执行 S11 测量。
5. 保存测量日志。
6. 将处理后的数据上传至云端数据服务器。

任务启动后无需用户干预。

---

### 4. 查看测量数据

中央面板显示以下内容：

**指令参数**
- 指令 HRS
- 指令 VRS

**实测角度**
- 实际水平角 H
- 实际垂直角 V

**S 参数数据**
- S11 幅度与相位
- S21 幅度与相位

**频率响应图**

系统自动生成两张图表：
- S11 随频率变化
- S21 随频率变化

有新测量结果上传时，数据自动刷新。

数据也可直接访问：https://render-a2mh.onrender.com/data

---

### 5. 下载数据

点击 **Download Data**（下载数据）。

系统将导出数据服务器中所有已存储的测量记录，文件兼容 Excel、MATLAB、Python 和 Origin。

---

### 6. 清除数据

开始新实验前：

1. 确认已下载所有需要保留的历史数据。
2. 点击 **Clear Data**（清除数据）。

> ⚠️ 此操作将永久删除数据服务器中所有已存储记录，并重置仪表板。

---

### 7. 数字孪生可视化

右侧面板包含散射计的实时三维模型，根据当前水平角和垂直角自动更新，便于用户远程观察运行期间的天线朝向。

---

## 第二部分 – 开发文档

### 1. 系统架构

本项目采用双云架构，指令通道与数据通道相互独立，提升可靠性并避免流量竞争。

**指令路径：**
```
Web 界面 → 指令服务器 → 仪器控制器 → 测量执行
```

**数据路径：**
```
仪器控制器 → 数据服务器 → Web 界面
```

---

### 2. 软件组件

#### 云端组件

**指令服务器（Command Server）**
- 接收测量指令
- 存储指令文件（`command.csv`）
- 提供下载 API

**数据服务器（Data Server）**
- 接收上传的测量数据
- 存储 CSV 记录（`data.csv`）
- 提供数据查询、清除和下载 API

#### 仪器端组件

**`download.py`**
从指令服务器下载最新指令文件。

**`toplevel1.py`** — 持久化守护进程
- 每隔数秒轮询指令服务器
- 检测到新指令后启动 `final.c`

**`final.c`** — 核心测量程序
- 控制 PTZ 云台
- 与 VNA 通信
- 执行测量网格
- 生成日志文件

主要参数：`vrs`、`hrs`、`shutdown`

```bash
final.exe -vrs 40 -hrs 30
```

**`toplevel2.py`** — 持久化守护进程
- 监控日志目录
- 检测到新测量文件后触发数据处理

**`trans.py`**
将原始日志转换为结构化 CSV 格式，输出列：
```
Target_H, Target_V, H, V, Frequency_Hz, S11_Mag_dB, S11_Phase, S21_Mag_dB, S21_Phase
```

**`upload.py`**
将处理后的 CSV 文件上传至数据服务器。

---

### 3. 部署 Render 服务器

#### 第一步：创建 Render 账户

在 https://render.com 注册账户。

#### 第二步：创建指令服务器

从 GitHub 仓库创建新的 Web Service。

- **运行时：** Python
- **启动命令：**
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

部署完成后记录 URL（例如 `https://render-er7w.onrender.com`）。

#### 第三步：创建数据服务器

使用相同的启动命令创建另一个 Web Service，部署后记录其 URL（例如 `https://render-a2mh.onrender.com`）。

---

### 4. 修改服务器地址

部署自己的服务器后，在以下文件中更新 URL：

**`download.py`**
```python
COMMAND_SERVER_URL = "https://your-command-server.onrender.com"
```

**`upload.py`**
```python
DATA_SERVER_URL = "https://your-data-server.onrender.com"
```

**Web 界面（`index.html`）**
```javascript
fetch("https://your-data-server.onrender.com/data")
fetch("https://your-command-server.onrender.com/upload")
```

---

### 5. 运行仪器控制器

安装 Python 3.10+ 及依赖包：

```bash
pip install requests pandas
```

运行守护进程：

```bash
python toplevel1.py
python toplevel2.py
```

这两个进程需持续运行。生产环境中，建议将其配置为 Windows 服务或任务计划程序后台任务，以实现自动重启。

---

### 6. 目录结构

```
project/
├── final.c
├── download.py
├── upload.py
├── trans.py
├── toplevel1.py
├── toplevel2.py
├── output.csv
├── log/
├── templates/
│   └── index.html
└── static/
```

---

### 7. 修改测量参数

频率设置以常量形式定义在 `final.c` 中：

```c
#define VNA_START_FREQ  5e9   // 5 GHz
#define VNA_STOP_FREQ   8e9   // 8 GHz
#define VNA_NOP         25    // 采样点数
```

修改方法：编辑常量 → 重新编译 `final.c` → 替换可执行文件。

---

### 8. 新增功能建议

- **扩展 VNA 测量参数支持** — 增加对更多测量参数和配置选项的支持。可参考 [Anritsu RF 和微波手持 VNA Master 仪器测量指南](https://dl.cdn-anritsu.com/en-us/test-measurement/files/Manuals/Measurement-Guide/10580-00289N.pdf) 了解可用的测量选项。

- **灵活的扫描模式** — 将固定的网格扫描替换为更通用的测量策略，例如直接指定目标角度列表进行测量，而非扫描整个矩形网格。

- **测量前驻留等待** — 支持在每个角度位置等待一段可配置的时间后再触发 VNA 测量，以减少机械振动对数据质量的影响。

- **复数 S 参数输出** — 在现有幅度和相位数据的基础上，支持输出完整的复数 S 参数（实部与虚部）。

---

### 故障排查

**测量未启动**
- 确认指令服务器可访问
- 确认 `toplevel1.py` 正在运行
- 确认指令文件已更新

**无数据显示**
- 确认 `final.c` 已生成日志
- 确认 `trans.py` 已生成 `output.csv`
- 确认 `upload.py` 成功上传数据

**Web 仪表板为空**
- 核对数据服务器 URL 是否正确
- 检查浏览器开发者控制台
- 确认 Render 服务运行正常

**三维模型未更新**
- 确认最新 H/V 值已上传
- 确认前端 fetch 定时器正在运行
- 在控制台检查 Three.js 渲染错误
