# 晋江水务 (Jinjiang Water) for Home Assistant

<!-- Logos & Badges 区块 -->
![Logo](custom_components/jjwater/brand/logo.png)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home_Assistant-2024.1+-blue.svg?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-yellow.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.0.0-success.svg?style=for-the-badge)](#)

这是一个为**晋江市水务集团**（微信小程序）开发的 Home Assistant 自定义集成插件。支持多水费户号同步接入，并将各个户号独立呈现为独立设备，原生支持 HA 能源面板（Energy Dashboard）。

---

## ✨ 核心特性

- **多户号独立管理**：一次配置即可支持追踪多个分开的水务账号（例如家庭、父母家等），系统自动隔离生成独立设备。
- **HA 能源仪表盘支持**：水表总读数传感器原生支持 `device_class: water`，完美融入 HA 的用水量统计分析图表。
- **全状态监控**：实时获取最新总抄表数、当月累计用量（m³）、账单缴费状态及本期金额。
- **免重启热更新**：支持通过“选项”直接更新过期的 Token，无需删减设备或重启系统。

---

## 🚀 安装指南

### 方法一：通过 HACS 安装 (推荐)
1. 打开 HACS -> **集成 (Integrations)** -> 右上角三个点 -> **自定义存储库 (Custom repositories)**。
2. 填入本仓库 URL，类别选择 **集成 (Integration)**。
3. 搜索 `Jinjiang Water` 并点击下载。
4. **重启 Home Assistant**。

### 方法二：手动安装
1. 下载本仓库，将 `custom_components/jjwater` 整个文件夹复制到你的 HA 配置目录下的 `custom_components/` 文件夹中。
2. **重启 Home Assistant**。

---

## ⚙️ 配置方法

1. 抓包获取 Token：在手机上对微信小程序**“晋江水务”**进行抓包，提取 `wwt.jinjiangwater.com` 请求头中的 `Authorization` 值。
2. 进入 HA **设置 -> 设备与服务 -> 添加集成**，搜索 **晋江水务**。
3. 填入 Token 及需要监控的水费户号（如：`0xxxx,0xxxxx`）。

---

## 🐛 开启调试日志 (Debug Logs)

如果在运行过程中抓取不到数据或出现异常，可以在 HA 配置文件 `configuration.yaml` 中开启本组件的专属 Debug 日志进行排错：

```yaml
logger:
  default: info
  logs:
    custom_components.jjwater: debug
