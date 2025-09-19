# Feishu MCP Server Setup Guide

## Step 1: Enable Bot in Feishu Developer Console

1. **Go to Feishu Open Platform**: https://open.feishu.cn/
2. **Find Your App**:
   - Your App ID: `cli_a84142e570f89e1b`
   - Look for this app in your developer console
3. **Enable Bot Feature**:
   - Go to "Features" → "Bot"
   - Click "Add Bot" or "Enable Bot"
   - Configure bot permissions:
     - ✅ Send messages to groups
     - ✅ Receive group messages
     - ✅ Send private messages
     - ✅ Create documents
     - ✅ Upload files
4. **Get Bot Token**:
   - After enabling bot, you'll get a Bot Token
   - Update your `.env` file with the new token if different

## Step 2: Configure Bot Permissions

Required permissions for your use case:
- `im:message` (Send and receive messages)
- `im:message.group_at_msg` (Group @ messages)
- `im:chat` (Chat management)
- `docs:doc` (Document creation)
- `drive:drive` (File operations)

## Step 3: Set Webhook URL (Optional)

If you want to receive messages:
- Set webhook URL to your server endpoint
- Example: `https://your-domain.com/webhook/feishu`