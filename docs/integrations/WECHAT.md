# WeChat Work Integration Guide

This guide explains how to integrate OpenUser with WeChat Work (企业微信), enabling your digital humans to interact with users through WeChat Work's enterprise messaging platform.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Configuration](#configuration)
5. [Features](#features)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

## Overview

The WeChat Work integration allows you to:

- Receive messages from WeChat Work users
- Send responses using digital humans
- Generate and send videos
- Handle interactive messages
- Process commands
- Schedule automated messages
- Integrate with enterprise workflows

### Architecture

```
┌──────────────────┐
│ WeChat Work User │
└────────┬─────────┘
         │ Message
         ▼
┌──────────────────┐
│ WeChat Work Bot  │
└────────┬─────────┘
         │ Webhook
         ▼
┌────────────────────────────────────┐
│ OpenUser WeChat Work Integration   │
│  ┌────────────┐  ┌───────────────┐ │
│  │  Webhook   │  │    Message    │ │
│  │  Handler   │  │   Processor   │ │
│  └────────────┘  └───────────────┘ │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ Digital Human Engine               │
│  ┌────────────┐  ┌───────────────┐ │
│  │   Video    │  │     Voice     │ │
│  │ Generation │  │   Synthesis   │ │
│  └────────────┘  └───────────────┘ │
└────────┬───────────────────────────┘
         │ Response
         ▼
┌──────────────────┐
│ WeChat Work Bot  │
└────────┬─────────┘
         │ Message
         ▼
┌──────────────────┐
│ WeChat Work User │
└──────────────────┘
```

## Prerequisites

### WeChat Work Requirements

1. **WeChat Work Account**: You need a WeChat Work enterprise account
2. **Admin Access**: Administrator privileges to create applications
3. **Verified Enterprise**: Your enterprise must be verified

### OpenUser Requirements

1. OpenUser installed and running
2. Public URL for webhook (use ngrok for local development)
3. SSL certificate (WeChat Work requires HTTPS)
4. Valid domain name (IP addresses not supported)

## Setup

### Step 1: Create WeChat Work Application

1. Log in to [WeChat Work Admin Console](https://work.weixin.qq.com/)
2. Navigate to **Applications** → **Create Application**
3. Fill in application information:
   - **Application Name**: OpenUser Bot
   - **Application Logo**: Upload your logo
   - **Application Description**: AI-powered digital human assistant
   - **Visible Range**: Select departments/users who can access the bot

4. Note down your credentials:
   - **Corp ID**: `ww1234567890abcdef`
   - **Agent ID**: `1000001`
   - **Secret**: `xxxxxxxxxxxxxxxxxx`

### Step 2: Configure Callback URL

1. In your application settings, go to **Receive Messages**
2. Set up callback configuration:
   - **URL**: `https://your-domain.com/api/v1/integrations/wechat/webhook`
   - **Token**: Generate a random token (save this)
   - **EncodingAESKey**: Generate or use provided key (save this)

3. Click **Save** and verify the URL

### Step 3: Configure OpenUser

1. Set environment variables in `.env`:

```bash
# WeChat Work Configuration
WECHAT_CORP_ID=ww1234567890abcdef
WECHAT_AGENT_ID=1000001
WECHAT_CORP_SECRET=xxxxxxxxxxxxxxxxxx
WECHAT_TOKEN=your_callback_token
WECHAT_ENCODING_AES_KEY=your_encoding_aes_key

# Webhook URL (for local development with ngrok)
WECHAT_WEBHOOK_URL=https://your-domain.com/api/v1/integrations/wechat/webhook
```

2. Restart OpenUser:

```bash
# Stop the server
# Restart with new configuration
uvicorn src.api.main:app --reload
```

### Step 4: Test the Integration

1. Open WeChat Work mobile app
2. Find your application in the **Workbench**
3. Send a test message: "Hello"
4. You should receive a response from your digital human

## Configuration

### Basic Configuration

```python
# src/integrations/wechat/config.py
from pydantic import BaseSettings

class WeChatWorkConfig(BaseSettings):
    corp_id: str
    agent_id: int
    corp_secret: str
    token: str
    encoding_aes_key: str
    webhook_url: str

    class Config:
        env_prefix = "WECHAT_"
```

### Advanced Configuration

```python
# Custom message handlers
from src.integrations.wechat.bot import WeChatWorkBot

bot = WeChatWorkBot()

@bot.on_message("text")
async def handle_text_message(message):
    """Handle text messages"""
    user_text = message.content
    # Process with digital human
    response = await generate_response(user_text)
    return response

@bot.on_message("image")
async def handle_image_message(message):
    """Handle image messages"""
    image_url = message.pic_url
    # Process image
    return "Image received and processed"

@bot.on_event("enter_agent")
async def handle_enter_agent(event):
    """Handle user entering the application"""
    return "Welcome to OpenUser! How can I help you today?"
```

## Features

### 1. Text Message Handling

Send and receive text messages:

```python
from src.integrations.wechat.bot import send_text_message

# Send text message
await send_text_message(
    user_id="UserID",
    content="Hello from OpenUser!"
)
```

### 2. Rich Media Messages

Send images, videos, and files:

```python
# Send image
await send_image_message(
    user_id="UserID",
    media_id="MEDIA_ID"
)

# Send video
await send_video_message(
    user_id="UserID",
    media_id="VIDEO_MEDIA_ID",
    title="Generated Video",
    description="Digital human video"
)

# Send file
await send_file_message(
    user_id="UserID",
    media_id="FILE_MEDIA_ID"
)
```

### 3. Interactive Cards

Send interactive message cards:

```python
await send_text_card(
    user_id="UserID",
    title="Digital Human Options",
    description="Choose an action:",
    url="https://your-domain.com/actions",
    btn_text="View Options"
)
```

### 4. Digital Human Integration

Generate and send digital human videos:

```python
from src.integrations.wechat.handlers import generate_and_send_video

# Generate video from text
await generate_and_send_video(
    user_id="UserID",
    digital_human_id=1,
    text="Hello! This is a message from your digital human.",
    mode="enhanced_talking_head"
)
```

### 5. Command Processing

Handle custom commands:

```python
@bot.on_command("/help")
async def help_command(message):
    """Handle /help command"""
    return """
    Available commands:
    /help - Show this help message
    /video <text> - Generate a video
    /status - Check system status
    """

@bot.on_command("/video")
async def video_command(message):
    """Handle /video command"""
    text = message.get_command_args()
    # Generate video
    video_url = await generate_video(text)
    return f"Video generated: {video_url}"
```

### 6. Event Handling

Handle WeChat Work events:

```python
@bot.on_event("subscribe")
async def handle_subscribe(event):
    """Handle user subscription"""
    return "Thank you for subscribing to OpenUser!"

@bot.on_event("unsubscribe")
async def handle_unsubscribe(event):
    """Handle user unsubscription"""
    # Log unsubscription
    pass

@bot.on_event("click")
async def handle_menu_click(event):
    """Handle menu button clicks"""
    key = event.event_key
    if key == "GENERATE_VIDEO":
        return "Please send me the text for video generation"
```

## Usage Examples

### Example 1: Simple Text Response

```python
# User sends: "Hello"
# Bot responds with digital human greeting

@bot.on_message("text")
async def handle_greeting(message):
    if "hello" in message.content.lower():
        return "Hello! I'm your AI digital human assistant. How can I help you today?"
    return await process_with_ai(message.content)
```

### Example 2: Video Generation Workflow

```python
# User sends: "/video Tell me about OpenUser"
# Bot generates and sends video

@bot.on_command("/video")
async def video_workflow(message):
    text = message.get_command_args()

    if not text:
        return "Please provide text for the video. Usage: /video <your text>"

    # Send processing message
    await send_text_message(
        user_id=message.from_user_id,
        content="Generating video... This may take a moment."
    )

    # Generate video
    video_path = await generate_digital_human_video(
        digital_human_id=1,
        text=text,
        mode="enhanced_talking_head"
    )

    # Upload to WeChat Work
    media_id = await upload_video(video_path)

    # Send video
    await send_video_message(
        user_id=message.from_user_id,
        media_id=media_id,
        title="Your Digital Human Video",
        description=text[:50]
    )

    return "Video sent successfully!"
```

### Example 3: Scheduled Messages

```python
from src.scheduler.tasks import schedule_wechat_message

# Schedule daily greeting
schedule_wechat_message(
    user_id="UserID",
    message="Good morning! Have a great day!",
    schedule="0 9 * * *"  # Every day at 9 AM
)

# Schedule weekly report
schedule_wechat_message(
    user_id="UserID",
    message_type="video",
    digital_human_id=1,
    text="Here's your weekly summary...",
    schedule="0 10 * * 1"  # Every Monday at 10 AM
)
```

### Example 4: Interactive Workflow

```python
# Multi-step conversation
user_states = {}

@bot.on_message("text")
async def interactive_workflow(message):
    user_id = message.from_user_id
    state = user_states.get(user_id, "idle")

    if state == "idle":
        if "create video" in message.content.lower():
            user_states[user_id] = "awaiting_text"
            return "Great! Please send me the text for your video."

    elif state == "awaiting_text":
        # Store text and ask for mode
        user_states[user_id] = {
            "state": "awaiting_mode",
            "text": message.content
        }
        return "Choose video quality:\n1. Basic\n2. Enhanced\n3. High Quality"

    elif isinstance(state, dict) and state["state"] == "awaiting_mode":
        mode_map = {"1": "lipsync", "2": "enhanced_lipsync", "3": "enhanced_talking_head"}
        mode = mode_map.get(message.content, "enhanced_talking_head")

        # Generate video
        await generate_and_send_video(
            user_id=user_id,
            digital_human_id=1,
            text=state["text"],
            mode=mode
        )

        user_states[user_id] = "idle"
        return "Video generated and sent!"

    return "I'm not sure what you mean. Type 'help' for assistance."
```

## Troubleshooting

### Common Issues

#### 1. Webhook Verification Fails

**Problem**: WeChat Work cannot verify your webhook URL

**Solutions**:
- Ensure your URL is publicly accessible (use ngrok for local testing)
- Verify SSL certificate is valid
- Check that token and encoding AES key match
- Ensure webhook handler returns correct verification response

```python
# Correct verification response
def verify_url(msg_signature, timestamp, nonce, echostr):
    wxcpt = WXBizMsgCrypt(token, encoding_aes_key, corp_id)
    ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
    if ret != 0:
        raise Exception("Verification failed")
    return sEchoStr
```

#### 2. Messages Not Received

**Problem**: Bot doesn't receive messages from users

**Solutions**:
- Verify application is visible to users
- Check webhook URL is correctly configured
- Ensure OpenUser server is running
- Review server logs for errors
- Verify Corp ID and Agent ID are correct

#### 3. Cannot Send Messages

**Problem**: Bot cannot send messages to users

**Solutions**:
- Verify access token is valid (tokens expire after 2 hours)
- Check Corp Secret is correct
- Ensure user is in the application's visible range
- Verify API rate limits haven't been exceeded

```python
# Refresh access token
from src.integrations.wechat.auth import get_access_token

access_token = await get_access_token(corp_id, corp_secret)
```

#### 4. Video Upload Fails

**Problem**: Cannot upload videos to WeChat Work

**Solutions**:
- Check video file size (max 10MB)
- Verify video format (MP4 recommended)
- Ensure video duration is within limits
- Check available storage quota

```python
# Upload with error handling
try:
    media_id = await upload_video(video_path)
except Exception as e:
    logger.error(f"Video upload failed: {e}")
    # Fallback to text message
    await send_text_message(user_id, "Video generation completed but upload failed")
```

### Debugging

Enable debug logging:

```python
# In .env
WECHAT_DEBUG=true
LOG_LEVEL=DEBUG
```

Check logs:

```bash
# View WeChat Work integration logs
tail -f logs/wechat_integration.log

# View all logs
tail -f logs/app.log
```

### Testing

Test webhook locally with ngrok:

```bash
# Start ngrok
ngrok http 8000

# Use ngrok URL in WeChat Work configuration
# Example: https://abc123.ngrok.io/api/v1/integrations/wechat/webhook
```

Test message sending:

```python
# Test script
import asyncio
from src.integrations.wechat.bot import send_text_message

async def test_send():
    await send_text_message(
        user_id="YourUserID",
        content="Test message from OpenUser"
    )

asyncio.run(test_send())
```

## Security Best Practices

1. **Keep Credentials Secure**
   - Never commit credentials to version control
   - Use environment variables
   - Rotate secrets regularly

2. **Validate Webhooks**
   - Always verify message signatures
   - Check timestamp to prevent replay attacks
   - Validate message format

3. **Rate Limiting**
   - Implement rate limiting for API calls
   - Handle rate limit errors gracefully
   - Cache access tokens

4. **Error Handling**
   - Don't expose internal errors to users
   - Log errors for debugging
   - Provide user-friendly error messages

5. **Data Privacy**
   - Don't log sensitive user data
   - Comply with data protection regulations
   - Implement data retention policies

## API Reference

### Send Messages

```python
# Text message
await send_text_message(user_id, content)

# Image message
await send_image_message(user_id, media_id)

# Video message
await send_video_message(user_id, media_id, title, description)

# File message
await send_file_message(user_id, media_id)

# Text card
await send_text_card(user_id, title, description, url, btn_text)
```

### Upload Media

```python
# Upload image
media_id = await upload_image(file_path)

# Upload video
media_id = await upload_video(file_path)

# Upload file
media_id = await upload_file(file_path)
```

### User Management

```python
# Get user info
user_info = await get_user_info(user_id)

# Get department users
users = await get_department_users(department_id)
```

## Resources

- [WeChat Work API Documentation](https://developer.work.weixin.qq.com/document/)
- [WeChat Work Admin Console](https://work.weixin.qq.com/)
- [OpenUser Documentation](../INDEX.md)
- [GitHub Issues](https://github.com/yxhpy/openuser/issues)

## Next Steps

- Explore [Feishu Integration](FEISHU.md) for Lark/Feishu platform
- Review [API Documentation](../api/INDEX.md) for more integration options
- Check [Developer Guide](../DEVELOPER_GUIDE.md) for custom integrations

---

**Version**: 1.0.0
**Last Updated**: 2026-02-03
**Feedback**: [GitHub Issues](https://github.com/yxhpy/openuser/issues)
