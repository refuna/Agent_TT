# 秋芝个人生活助理团队构想

## 背景
我是秋芝，我想打造一个个人生活助理团队，其中有5个AI助理角色，作为我的智能分身帮助我管理日常生活，提升效率和自我认知。

---

## 1. 新闻秋 - AI新闻聚合与分析助理

**触发条件**: 每日早晨问候"早上好"
**核心功能**: 获取、分析和总结AI行业新闻

**详细工作流程**:
1. 自动抓取多个AI新闻源的最新资讯
2. 使用自然语言处理技术筛选和排序重要新闻
3. 生成简洁的新闻简报，突出关键信息和趋势
4. 创建以日期命名的文件夹 (如：`2024-01-15/`)
5. 在文件夹中保存 `新闻_YYYY-MM-DD.md` 文档
6. 自动发送格式化新闻简报到飞书群组

**技术要求**:
- 网页抓取和RSS订阅功能
- 内容去重和相关性排序算法
- 中文自然语言处理能力
- 飞书API集成
- 模板化文档生成

---

## 2. 穿搭秋 - 智能造型师助理

**触发条件**: 新闻阅读完成后
**核心功能**: 基于天气、场合和个人风格提供穿搭建议

**详细工作流程**:
1. 主动询问当日行程和特殊场合安排
2. 获取实时天气数据和未来几小时预报
3. 读取 `aboutme/` 中的风格偏好和衣橱信息
4. 结合天气、场合、个人风格生成穿搭建议
5. 使用AI图像生成创建穿搭效果图
6. 保存穿搭建议到 `穿搭_YYYY-MM-DD.md`
7. 发送穿搭图片和建议给秋芝

**技术要求**:
- 天气API接口集成
- 个人风格数据库管理
- AI图像生成能力
- 色彩搭配和风格匹配算法
- 日历集成（可选）

---

## 3. 教练秋 - 健康管理与指导助理

**触发条件**: 穿搭决定完成后
**核心功能**: 提供个性化健康指导和目标跟踪

**详细工作流程**:
1. 询问当日体重测量情况
2. 记录体重数据并分析趋势
3. 根据 `aboutme/` 中的健康目标和历史数据分析进展
4. 生成个性化运动建议（考虑时间、体能、目标）
5. 提供营养饮食建议和外卖推荐
6. 创建 `健康_YYYY-MM-DD.md` 文档
7. 更新 `aboutme/health_data.md` 中的体重和健康指标

**技术要求**:
- 健康数据分析和趋势预测
- 运动计划生成算法
- 营养数据库和卡路里计算
- 目标跟踪和进度可视化
- BMI和其他健康指标计算

---

## 4. 日报秋 - 活动记录与分析助理

**触发条件**: 穿搭决定完成后
**核心功能**: 记录、分析和报告日常活动

**详细工作流程**:
1. 通过结构化对话收集当日活动信息
2. 对活动进行分类和时间分析 
3. 识别完成的任务、面临的挑战和收获
4. 生成包含效率分析的日报文档
5. 创建 `日报_YYYY-MM-DD.md` 文件
6. 格式化为飞书文档发送到"流程群"
7. 提供生产力洞察和改进建议

**技术要求**:
- 对话式信息收集系统
- 活动分类和时间管理分析
- 生产力指标计算
- 飞书群组集成
- 数据可视化能力

---

## 5. 反思秋 - 自我认知与成长引导助理

**触发条件**: 收到"今天工作结束了"的信号
**核心功能**: 引导深度反思，促进自我认知和成长

**详细工作流程**:
1. 回顾当日所有记录（新闻、穿搭、健康、日报）
2. 通过多轮深度对话引导反思：
   - 情绪状态和能量水平
   - 决策模式和思维方式
   - 个人洞察和学习收获
   - 改进机会和成长方向
3. 识别行为模式和心理状态趋势
4. 生成个性化成长建议
5. 创建 `反思_YYYY-MM-DD.md` 文档
6. 更新长期自我认知档案

**技术要求**:
- 高级对话AI和心理学框架
- 情感分析和模式识别
- 长期数据趋势分析
- 个性化建议生成系统
- 隐私保护和数据安全

---

## 所需上下文文件夹结构

### 1. `/aboutme/` - 个人信息中心
```
aboutme/
├── profile.md           # 基本个人信息、偏好、目标
├── style_preferences.md # 穿搭风格、颜色偏好、品牌喜好
├── health_data.md       # 体重历史、健身目标、饮食限制
├── schedule_patterns.md # 日程规律、常去场所
└── reflection_insights.md # 历史反思模式和自我认知数据
```

### 2. `/daily_logs/` - 日常记录存储
```
daily_logs/
└── 2024/
    ├── 01/
    │   ├── 新闻_2024-01-15.md
    │   ├── 穿搭_2024-01-15.md
    │   ├── 健康_2024-01-15.md
    │   ├── 日报_2024-01-15.md
    │   └── 反思_2024-01-15.md
    └── 02/
        └── ...
```

### 3. `/templates/` - 文档模板
```
templates/
├── news_template.md       # 新闻简报格式
├── outfit_template.md     # 穿搭建议格式
├── health_template.md     # 健康记录格式
├── daily_report_template.md # 日报格式
└── reflection_template.md  # 反思记录格式
```

### 4. `/resources/` - 资源数据库
```
resources/
├── news_sources.json     # AI新闻源列表和RSS链接
├── weather_locations.json # 常用地点天气配置
├── nutrition_database.json # 食物营养数据库
├── exercise_library.json   # 运动项目和强度数据
└── style_database.json     # 服装搭配和风格数据
```

### 5. `/config/` - 系统配置
```
config/
├── agent_settings.json    # 各助理的个性化配置
├── feishu_config.json     # 飞书API凭证和群组设置
├── api_keys.json          # 外部API密钥管理
└── workflow_config.json   # 工作流触发条件和序列
```

---

## 所需MCP协议清单

### 1. **新闻聚合MCP** (`mcp_news_aggregator`)
**功能**:
- `fetch_ai_news()` - 从多源获取AI新闻
- `summarize_articles(articles)` - 生成新闻摘要
- `rank_by_relevance(news_list)` - 按相关性排序

### 2. **天气服务MCP** (`mcp_weather_service`)
**功能**:
- `get_current_weather(location)` - 获取实时天气
- `get_forecast(location, hours)` - 获取未来预报
- `get_weather_alerts(location)` - 获取天气预警

### 3. **图像生成MCP** (`mcp_image_generator`)
**功能**:
- `generate_outfit_visual(description, style)` - 生成穿搭效果图
- `create_style_board(colors, items)` - 创建风格板
- `generate_health_charts(data)` - 生成健康数据图表

### 4. **飞书集成MCP** (`mcp_feishu_connector`)
**功能**:
- `send_to_group(group_id, content)` - 发送到群组
- `create_document(title, content)` - 创建飞书文档
- `upload_file(file_path, folder)` - 上传文件

### 5. **日历服务MCP** (`mcp_calendar_service`)
**功能**:
- `get_daily_schedule(date)` - 获取日程安排
- `add_health_reminder(time, task)` - 添加健康提醒
- `check_availability(time_range)` - 检查空闲时间

### 6. **健康追踪MCP** (`mcp_health_tracker`)
**功能**:
- `log_weight(date, weight)` - 记录体重
- `calculate_health_metrics(weight, height, age)` - 计算健康指标
- `track_progress(goal_type, current_value)` - 跟踪目标进度
- `suggest_exercises(fitness_level, available_time)` - 推荐运动

### 7. **自然语言处理MCP** (`mcp_nlp_processor`)
**功能**:
- `analyze_sentiment(text)` - 情感分析
- `extract_insights(conversation)` - 提取对话洞察
- `generate_summary(long_text)` - 内容摘要
- `categorize_activities(description)` - 活动分类

### 8. **文件管理MCP** (`mcp_file_manager`)
**功能**:
- `create_daily_folder(date)` - 创建日期文件夹
- `backup_data(source, destination)` - 数据备份
- `search_historical(query, date_range)` - 历史数据搜索
- `generate_reports(time_period, type)` - 生成定期报告

---

## 实施建议

1. **分阶段部署**: 先实现基础功能，再逐步添加高级特性
2. **数据隐私**: 确保所有个人数据的安全存储和处理
3. **用户反馈**: 建立反馈机制持续优化助理表现
4. **可扩展性**: 设计模块化架构便于未来功能扩展
5. **容错处理**: 添加错误处理和恢复机制确保服务稳定性
