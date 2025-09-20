# TT Personal Life Assistant Team Concept

## Background
I am TT, and I want to build a personal life assistant team consisting of 5 AI assistant roles. These assistants will act as my intelligent avatars, helping me manage daily life, improve efficiency, and enhance self-awareness.

---

## 1. News-TT - AI News Aggregation & Analysis Assistant

**Trigger Condition**: Morning greeting "Good Morning"  
**Core Function**: Gather, analyze, and summarize AI industry news  

**Workflow**:
1. Automatically fetch the latest news from multiple AI sources  
2. Use NLP to filter and rank important news  
3. Generate a concise news briefing highlighting key points and trends  
4. Create a folder named by date (e.g., `2025-01-15/`)  
5. Save the document as `News_YYYY-MM-DD.md` inside the folder  
6. Automatically send formatted news brief to Feishu group  

**Technical Requirements**:
- Web scraping & RSS subscription  
- Content deduplication and relevance ranking algorithms  
- Chinese NLP capability  
- Feishu API integration  
- Template-based document generation  

---

## 2. Outfit-TT - Intelligent Stylist Assistant

**Trigger Condition**: After news reading is completed  
**Core Function**: Provide outfit suggestions based on weather, occasion, and personal style  

**Workflow**:
1. Ask about the day’s schedule and any special events  
2. Fetch real-time weather and short-term forecast  
3. Read style preferences and wardrobe data from `aboutme/`  
4. Generate outfit suggestions based on weather, occasion, and style  
5. Use AI image generation to create outfit previews  
6. Save outfit suggestions to `Outfit_YYYY-MM-DD.md`  
7. Send outfit image and suggestion to TT  

**Technical Requirements**:
- Weather API integration  
- Personal style database management  
- AI image generation  
- Color-matching and style recommendation algorithms  
- Calendar integration (optional)  

---

## 3. Coach-TT - Health Management & Guidance Assistant

**Trigger Condition**: After outfit decision is completed  
**Core Function**: Provide personalized health guidance and progress tracking  

**Workflow**:
1. Ask for daily weight measurement  
2. Record weight data and analyze trends  
3. Reference `aboutme/` for health goals and history  
4. Generate personalized workout suggestions (based on time, fitness, goals)  
5. Provide nutrition advice and food delivery recommendations  
6. Create `Health_YYYY-MM-DD.md` document  
7. Update `aboutme/health_data.md` with weight and health metrics  

**Technical Requirements**:
- Health data analysis and trend forecasting  
- Workout plan generation  
- Nutrition database and calorie calculation  
- Progress tracking and visualization  
- BMI and health indicator calculations  

---

## 4. Report-TT - Daily Activity Recording & Analysis Assistant

**Trigger Condition**: After outfit decision is completed  
**Core Function**: Record, analyze, and report daily activities  

**Workflow**:
1. Collect daily activity information via structured conversation  
2. Categorize activities and perform time analysis  
3. Identify completed tasks, challenges, and achievements  
4. Generate a daily report with productivity analysis  
5. Save as `Report_YYYY-MM-DD.md`  
6. Send formatted report as Feishu document to “workflow group”  
7. Provide productivity insights and improvement suggestions  

**Technical Requirements**:
- Conversational data collection  
- Activity categorization and time management analysis  
- Productivity metric calculations  
- Feishu group integration  
- Data visualization  

---

## 5. Reflection-TT - Self-Awareness & Growth Guidance Assistant

**Trigger Condition**: After receiving the signal “Today’s work is finished”  
**Core Function**: Guide deep reflection to promote self-awareness and growth  

**Workflow**:
1. Review all daily records (news, outfit, health, report)  
2. Guide reflection via multi-turn dialogue:  
   - Emotional state and energy levels  
   - Decision-making patterns and thinking styles  
   - Insights and learnings  
   - Opportunities for growth  
3. Identify behavioral patterns and psychological trends  
4. Generate personalized growth suggestions  
5. Save as `Reflection_YYYY-MM-DD.md`  
6. Update long-term self-awareness archive  

**Technical Requirements**:
- Advanced conversational AI with psychology frameworks  
- Sentiment analysis and pattern recognition  
- Long-term data trend analysis  
- Personalized recommendations  
- Privacy protection and data security  

---

## Required Folder Structure

### 1. `/aboutme/` - Personal Info Hub

aboutme/
├── profile.md # Basic info, preferences, goals
├── style_preferences.md # Outfit style, colors, brands
├── health_data.md # Weight history, fitness goals, dietary limits
├── schedule_patterns.md # Routine patterns, frequent locations
└── reflection_insights.md # Reflection history and insights

### 2. `/daily_logs/` - Daily Records

daily_logs/
└── 2024/
├── 01/
│ ├── News_2024-01-15.md
│ ├── Outfit_2024-01-15.md
│ ├── Health_2024-01-15.md
│ ├── Report_2024-01-15.md
│ └── Reflection_2024-01-15.md
└── 02/


### 3. `/templates/` - Document Templates

templates/
├── news_template.md
├── outfit_template.md
├── health_template.md
├── daily_report_template.md
└── reflection_template.md



### 4. `/resources/` - Resource Database
resources/
├── news_sources.json # AI news sources & RSS feeds
├── weather_locations.json # Weather settings for locations
├── nutrition_database.json # Food nutrition database
├── exercise_library.json # Exercises and intensity data
└── style_database.json # Outfit and style data


### 5. `/config/` - System Configuration
config/
├── agent_settings.json # Assistant personalization
├── feishu_config.json # Feishu API credentials & groups
├── api_keys.json # External API keys
└── workflow_config.json # Workflow triggers & sequences


---

## Required MCP Protocol List

### 1. **News Aggregation MCP** (`mcp_news_aggregator`)
**Functions**:
- `fetch_ai_news()` - Fetch AI news from multiple sources  
- `summarize_articles(articles)` - Generate summaries  
- `rank_by_relevance(news_list)` - Sort by relevance  

### 2. **Weather Service MCP** (`mcp_weather_service`)
**Functions**:
- `get_current_weather(location)` - Get current weather  
- `get_forecast(location, hours)` - Get forecast  
- `get_weather_alerts(location)` - Get alerts  

### 3. **Image Generation MCP** (`mcp_image_generator`)
**Functions**:
- `generate_outfit_visual(description, style)` - Outfit previews  
- `create_style_board(colors, items)` - Style boards  
- `generate_health_charts(data)` - Health charts  

### 4. **Feishu Integration MCP** (`mcp_feishu_connector`)
**Functions**:
- `send_to_group(group_id, content)` - Send to group  
- `create_document(title, content)` - Create document  
- `upload_file(file_path, folder)` - Upload files  

### 5. **Calendar Service MCP** (`mcp_calendar_service`)
**Functions**:
- `get_daily_schedule(date)` - Get schedule  
- `add_health_reminder(time, task)` - Add reminder  
- `check_availability(time_range)` - Check availability  

### 6. **Health Tracker MCP** (`mcp_health_tracker`)
**Functions**:
- `log_weight(date, weight)` - Log weight  
- `calculate_health_metrics(weight, height, age)` - Health metrics  
- `track_progress(goal_type, current_value)` - Track goals  
- `suggest_exercises(fitness_level, available_time)` - Recommend workouts  

### 7. **NLP Processor MCP** (`mcp_nlp_processor`)
**Functions**:
- `analyze_sentiment(text)` - Sentiment analysis  
- `extract_insights(conversation)` - Extract insights  
- `generate_summary(long_text)` - Summarize content  
- `categorize_activities(description)` - Activity classification  

### 8. **File Manager MCP** (`mcp_file_manager`)
**Functions**:
- `create_daily_folder(date)` - Create folder  
- `backup_data(source, destination)` - Backup data  
- `search_historical(query, date_range)` - Search history  
- `generate_reports(time_period, type)` - Generate reports  

---

## Implementation Suggestions
1. **Phased Deployment**: Start with core functions, then expand  
2. **Data Privacy**: Ensure secure storage and processing of personal data  
3. **User Feedback**: Establish feedback mechanisms for optimization  
4. **Scalability**: Modular design for future expansion  
5. **Error Handling**: Add error recovery mechanisms for reliability  

