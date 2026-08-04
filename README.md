# 晋江水务 (jjwater) Home Assistant 集成

这是一个为**晋江市水务集团**（微信小程序）开发的 Home Assistant 自定义集成插件。支持多户号同步接入，并将各个户号独立呈现为独立设备，原生支持 HA 能源面板（Energy Dashboard）。

---

## 📁 目录结构

```text
custom_components/jjwater/
├── brand/               # 品牌图标 (icon.png / logo.png)
├── translations/        # 中文语言包 (zh-Hans.json)
├── __init__.py          # 主入口与初始化
├── api.py               # API 传输层
├── config_flow.py       # UI 配置流
├── const.py             # 常量配置
├── coordinator.py       # 定时协调刷新
├── manifest.json        # 插件元数据
├── sensor.py            # 传感器实体定义
└── README.md            # 项目说明
