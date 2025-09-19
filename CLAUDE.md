# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个个人AI助理团队系统，名为"秋芝个人生活助理团队"，包含5个专门的AI助理角色：新闻秋、穿搭秋、教练秋、日报秋和反思秋。该系统基于MCP (Model Context Protocol) 架构，提供智能化的日常生活管理服务。

## 核心架构

### 项目结构
```
project/
├── core/                    # 核心基础类
│   ├── base_server.py      # MCP服务器基类
│   └── __init__.py
├── utils/                   # 共享工具模块
│   ├── config.py           # 配置管理
│   ├── logging_setup.py    # 日志配置
│   └── __init__.py
├── servers/                 # 重构后的MCP服务器
│   ├── feishu_server.py    # 飞书集成服务
│   ├── news_server.py      # 新闻聚合服务
│   ├── weather_server.py   # 天气信息服务
│   └── __init__.py
├── config/                  # 配置文件
│   ├── config.json         # 简化的统一配置
│   └── .env               # 环境变量（需要创建）
└── run_server.py          # 统一服务器启动脚本
```

### MCP服务器
- **servers/feishu_server.py**: 飞书集成服务，处理群组消息发送等操作
- **servers/news_server.py**: 新闻聚合服务，从多个新闻源获取和处理AI相关新闻
- **servers/weather_server.py**: 天气信息服务，提供天气数据和穿搭建议
- **jimeng_mcp_server.py**: 图像生成服务（保持原有结构）

### 配置和测试
- **claude_desktop_config.json**: Claude Desktop MCP服务器配置
- **test_servers.py**: 统一的服务器测试脚本

### 数据组织结构
```
claud/
├── aboutme/                  # 个人信息和偏好数据
│   ├── profile.md           # 基本信息
│   ├── style_preferences.md # 穿搭风格偏好
│   ├── health_data.md       # 健康数据历史
│   ├── schedule_patterns.md # 日程规律
│   └── reflection_insights.md # 反思洞察
├── daily_logs/              # 每日记录存储
│   └── [YYYY/MM格式的日期文件夹]
├── templates/               # 文档模板
├── resources/               # 资源数据库
└── config/                  # 系统配置
```

## 常用命令

### 运行MCP服务器
```bash
# 启动特定MCP服务器
python run_server.py feishu    # 飞书服务器
python run_server.py news     # 新闻服务器
python run_server.py weather  # 天气服务器
python run_server.py jimeng   # 图像生成服务器
```

### 测试命令
```bash
# 运行所有服务器测试
python test_servers.py
```

## AI助理工作流

### 触发机制和执行顺序
1. **新闻秋** - 触发：每日早晨问候"早上好"
2. **穿搭秋** - 触发：新闻阅读完成后
3. **教练秋** - 触发：穿搭决定完成后
4. **日报秋** - 触发：穿搭决定完成后（并行）
5. **反思秋** - 触发：收到"今天工作结束了"的信号

### 数据流和文档生成
- 每个助理生成对应的日期文档（如：新闻_2024-09-18.md）
- 所有文档按年/月结构存储在daily_logs中
- 飞书集成自动发送格式化内容到相应群组

## 环境配置

### 必需的环境变量
```bash
FEISHU_APP_ID=cli_a84142e570f89e1b
FEISHU_APP_SECRET=[App Secret]
FEISHU_BOT_TOKEN=[Bot Token]
NEWSAPI_KEY=[可选，用于新闻API]
```

### MCP客户端集成
配置文件位于claude_desktop_config.json，已包含飞书服务器配置。添加新的MCP服务器时，需要更新此配置文件。

## 开发指导

### 添加新的助理角色
1. 在构想.md中定义助理的功能和工作流程
2. 创建对应的模板文件在templates/目录
3. 更新aboutme/中的相关偏好数据
4. 如需特殊功能，开发对应的MCP服务器

### 数据持久化
- 使用标准化的日期命名格式：YYYY-MM-DD
- 中文文件名便于识别：新闻_、穿搭_、健康_、日报_、反思_
- 所有个人数据存储在aboutme/目录，支持助理个性化

### 飞书集成开发
- 使用feishu_mcp_server.py中的FeishuAPI类
- 支持的功能：发送消息到群组、创建文档、上传文件
- 错误处理和令牌刷新已集成

### 测试方法
- 使用test_news_agent.py测试完整的新闻工作流
- 使用test_mcp_server.py验证MCP服务器功能
- 集成测试包括API调用、文档生成和飞书发送

## 特殊注意事项

- 所有API密钥和敏感信息存储在环境变量中，不要硬编码
- 中文是主要工作语言，所有文档和交互使用中文
- 系统设计为个人使用，注重隐私保护和数据安全
- MCP协议确保了模块化和可扩展性