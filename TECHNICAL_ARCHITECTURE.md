# 技术架构文档 - 秋芝个人生活助理团队

## 🏗️ 系统整体架构

### 核心技术栈
```
Frontend Layer    │ Claude Desktop Application
                  │ ├── Agent Interface (daily-news-briefer, daily-report-qiu, etc.)
                  │ └── User Interaction Layer
                  │
Protocol Layer    │ MCP (Model Context Protocol)
                  │ ├── JSON-RPC 2.0 Communication
                  │ ├── Standardized Tool Definitions
                  │ └── Server Discovery & Capability Exchange
                  │
Server Layer      │ Python MCP Servers
                  │ ├── feishu_mcp_server.py (Communication)
                  │ ├── news_mcp_server.py (Information Gathering)
                  │ ├── weather_mcp_server.py (Environmental Data)
                  │ ├── jimeng_mcp_server.py (AI Image Generation)
                  │ └── health_mcp_server.py (Health Management) [Planned]
                  │
Data Layer        │ Local File System + External APIs
                  │ ├── aboutme/ (Personal Data)
                  │ ├── daily_logs/ (Time-series Data)
                  │ ├── config/ (System Configuration)
                  │ └── External Services (Feishu, News APIs, Weather APIs)
```

## 🔌 MCP协议集成详解

### 1. MCP服务器实现模式

#### 标准服务器结构
```python
class BaseMCPServer:
    def __init__(self):
        self.server = Server("server-name")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [...]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            return [...]
```

#### 工具定义标准
```python
Tool(
    name="tool_name",
    description="功能描述",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数说明"},
            "param2": {"type": "number", "default": 0}
        },
        "required": ["param1"]
    }
)
```

### 2. 已实现的MCP服务器

#### feishu_mcp_server.py
**核心功能**: 飞书平台集成
```python
工具列表:
├── send_feishu_message    # 发送消息到群组
├── create_feishu_document # 创建飞书文档
├── upload_file_to_feishu  # 上传文件
└── get_feishu_groups      # 获取群组列表

认证机制:
├── OAuth 2.0 流程
├── App ID + App Secret
├── Access Token 自动刷新
└── 错误重试机制
```

#### news_mcp_server.py
**核心功能**: 新闻聚合与分析
```python
工具列表:
├── fetch_ai_news          # 获取AI新闻
├── search_news            # 搜索特定新闻
├── summarize_news         # 新闻摘要生成
└── categorize_news        # 新闻分类

数据源:
├── RSS订阅源
├── 新闻API (NewsAPI等)
├── 网页爬虫
└── 社交媒体API
```

#### weather_mcp_server.py
**核心功能**: 天气数据服务
```python
工具列表:
├── get_current_weather    # 当前天气
├── get_weather_forecast   # 天气预报
├── get_weather_alerts     # 天气预警
└── get_air_quality        # 空气质量

数据源:
├── OpenWeatherMap API
├── WeatherAPI
├── 高德天气API
└── 中国天气网API
```

#### jimeng_mcp_server.py
**核心功能**: AI图像生成
```python
工具列表:
├── generate_image         # 生成图像
└── get_models            # 获取可用模型

配置:
├── 会话令牌认证
├── 样式参数配置
├── 分辨率选择
└── 错误处理机制
```

### 3. Claude Desktop配置集成

#### claude_desktop_config.json结构
```json
{
  "mcp": {
    "servers": {
      "server_name": {
        "command": "python",
        "args": ["path/to/server.py"],
        "env": {
          "API_KEY": "your_api_key",
          "CONFIG_VAR": "value"
        }
      }
    }
  }
}
```

## 🤖 五大代理系统架构

### 代理定义系统
```markdown
位置: .claude/agents/
结构:
├── daily-news-briefer.md    # 新闻秋代理
├── outfit-advisor-qiu.md    # 穿搭秋代理
├── health-coach-qiu.md      # 教练秋代理
├── daily-report-qiu.md      # 日报秋代理
└── reflection-qiu.md        # 反思秋代理
```

### 代理配置格式
```yaml
---
name: agent-name
description: 代理功能描述和触发条件
model: sonnet
---

# 代理提示词和工作流程定义
```

### 工作流程编排

#### 1. 线性工作流
```
触发信号 → 新闻秋 → 穿搭秋 → 教练秋 → 完成信号
```

#### 2. 并行工作流
```
穿搭秋完成 → ┬→ 日报秋
              └→ 教练秋
```

#### 3. 条件工作流
```
工作结束信号 → 反思秋 (等待其他代理完成)
```

## 📊 数据管理架构

### 1. 个人数据存储 (aboutme/)
```
aboutme/
├── profile.md              # 基本信息
│   ├── 姓名、年龄、职业
│   ├── 基本偏好设置
│   └── 联系方式信息
├── style_preferences.md    # 穿搭偏好
│   ├── 颜色偏好
│   ├── 风格类型
│   ├── 品牌喜好
│   └── 场合着装规则
├── health_data.md          # 健康数据
│   ├── 基础生理指标
│   ├── 健康目标设定
│   ├── 运动偏好
│   └── 饮食限制
├── schedule_patterns.md    # 日程模式
│   ├── 工作时间规律
│   ├── 常去地点
│   ├── 重要会议模式
│   └── 休息时间安排
└── reflection_insights.md  # 反思洞察
    ├── 个人成长记录
    ├── 行为模式分析
    ├── 决策模式识别
    └── 长期趋势观察
```

### 2. 时间序列数据 (daily_logs/)
```
daily_logs/
└── YYYY/
    └── MM/
        ├── 新闻_YYYY-MM-DD.md
        │   ├── 新闻摘要
        │   ├── 重要资讯
        │   ├── 行业趋势
        │   └── 个人关注点
        ├── 穿搭_YYYY-MM-DD.md
        │   ├── 天气情况
        │   ├── 穿搭建议
        │   ├── 搭配图片
        │   └── 场合考虑
        ├── 健康_YYYY-MM-DD.md
        │   ├── 体重记录
        │   ├── 运动计划
        │   ├── 饮食建议
        │   └── 健康指标
        ├── 日报_YYYY-MM-DD.md
        │   ├── 任务完成情况
        │   ├── 时间分配分析
        │   ├── 效率评估
        │   └── 改进建议
        └── 反思_YYYY-MM-DD.md
            ├── 情绪状态
            ├── 行为模式
            ├── 学习收获
            └── 成长洞察
```

### 3. 配置系统 (config/)
```
config/
├── agent_settings.json     # 代理个性化配置
│   ├── 个性化参数
│   ├── 工作时间窗口
│   ├── 触发条件设置
│   └── 输出格式定义
├── feishu_config.json      # 飞书API配置
│   ├── 应用凭证
│   ├── 群组ID映射
│   ├── 消息模板
│   └── 权限设置
├── mcp_config.json         # MCP服务配置
│   ├── 服务器列表
│   ├── 认证配置
│   ├── 健康检查设置
│   └── 错误处理策略
├── workflow_config.json    # 工作流配置
│   ├── 代理执行顺序
│   ├── 依赖关系定义
│   ├── 触发条件设置
│   └── 错误恢复机制
└── .env                    # 环境变量
    ├── API密钥
    ├── 数据库连接
    ├── 外部服务配置
    └── 调试开关
```

## 🔐 安全与隐私架构

### 1. 数据保护措施
```
本地存储优先:
├── 所有个人数据本地化存储
├── 无云端个人数据传输
├── 加密存储敏感信息
└── 定期数据备份

API密钥管理:
├── 环境变量存储
├── 配置文件加密
├── 访问权限控制
└── 密钥轮换机制
```

### 2. 网络安全
```
通信加密:
├── HTTPS强制使用
├── TLS 1.3协议
├── 证书验证
└── 请求签名验证

访问控制:
├── IP白名单
├── 服务特定密钥
├── 权限矩阵管理
└── 审计日志记录
```

## ⚡ 性能优化架构

### 1. 并发处理
```python
异步架构:
├── asyncio事件循环
├── 并发请求处理
├── 非阻塞I/O操作
└── 连接池管理

资源管理:
├── 内存限制: 512MB
├── CPU限制: 2核
├── 网络超时: 30秒
└── 请求队列管理
```

### 2. 缓存策略
```
数据缓存:
├── 天气数据: 1小时
├── 新闻数据: 30分钟
├── 风格偏好: 24小时
├── 健康基线: 7天
└── 用户会话: 实时

缓存实现:
├── 内存缓存 (Redis)
├── 文件缓存
├── 数据库缓存
└── CDN缓存
```

### 3. 错误处理与恢复
```
错误处理策略:
├── 指数退避重试
├── 最大重试次数: 3
├── 熔断器机制
└── 优雅降级

恢复机制:
├── 状态持久化
├── 断点续传
├── 事务回滚
└── 数据一致性检查
```

## 📈 监控与分析架构

### 1. 系统监控
```
性能指标:
├── 响应时间监控
├── 内存使用率
├── CPU占用率
└── 网络延迟

业务指标:
├── 代理完成率
├── 用户满意度
├── 错误频率
└── 功能使用统计
```

### 2. 数据分析
```
用户行为分析:
├── 使用模式识别
├── 高峰时间分析
├── 功能偏好统计
└── 效率提升追踪

系统优化:
├── 瓶颈识别
├── 性能调优
├── 功能改进建议
└── 资源分配优化
```

## 🔄 扩展性设计

### 1. 模块化架构
```
水平扩展:
├── 新代理类型添加
├── 新MCP服务器集成
├── 新数据源接入
└── 新输出格式支持

垂直扩展:
├── 功能深度增强
├── 算法模型升级
├── 数据处理能力提升
└── 用户体验优化
```

### 2. API设计
```
RESTful API:
├── 标准HTTP方法
├── 状态码规范
├── JSON数据格式
└── 版本控制机制

GraphQL支持:
├── 灵活查询能力
├── 类型安全
├── 实时订阅
└── 前端优化
```

## 🚀 部署架构

### 1. 开发环境
```
本地开发:
├── Python 3.13.2+
├── Virtual Environment
├── Git版本控制
└── IDE配置 (VS Code)

依赖管理:
├── pip + requirements.txt
├── 环境变量管理
├── 配置文件模板
└── 开发脚本自动化
```

### 2. 生产环境
```
容器化部署:
├── Docker镜像构建
├── Docker Compose编排
├── 环境变量注入
└── 健康检查配置

服务管理:
├── 自动重启机制
├── 日志管理
├── 备份策略
└── 更新部署流程
```

---

**文档版本**: v1.0.0
**最后更新**: 2025-09-19
**维护者**: 秋芝
**技术栈**: Python 3.13, MCP Protocol, Claude Desktop, Feishu API

*此技术架构文档详细描述了秋芝个人生活助理团队项目的技术实现细节，为开发、部署和维护提供全面的技术指导。*