# Feishu (Lark) Integration Guide

This guide explains how to integrate OpenUser with Feishu (also known as Lark outside China), enabling your digital humans to interact with users through Feishu's messaging platform.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Configuration](#configuration)
5. [Features](#features)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

## Overview

The Feishu integration allows you to:

- Receive messages from Feishu users
- Send responses using digital humans
- Generate and send videos
- Handle interactive cards
- Process commands
- Schedule automated messages

### Architecture

```
┌──────────────┐
│ Feishu User  │
└──────┬───────┘
       │ Message
       ▼
┌──────────────┐
│ Feishu Bot   │
└──────┬───────┘
       │ Webhook
       ▼
┌──────────────────────────────────┐
│ OpenUser Feishu Integration      │
│  ┌────────────┐  ┌─────────────┐ │
│  │  Webhook   │  │   Message   │ │
│  │  Handler   │  │  Processor  │ │
│  └────────────┘  └─────────────┘ │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Digital Human Engine             │
│  ┌────────────┐  ┌─────────────┐ │
│  │   Video    │  │    Voice    │ │
│  │ Generation │  │  Synthesis  │ │
│  └────────────┘  └─────────────┘ │
└──────────┬───────────────────────┘
           │ Response
           ▼
┌──────────────┐
│ Feishu Bot   │
└──────┬───────┘
       │ Message
       ▼
┌──────────────┐
│ Feishu User  │
└──────────────┘
```

## Prerequisites

### Feishu Requirements

1. **Feishu Account**: You need a Feishu account
2. **Developer Account**: Register at [Feishu Open Platform](https://open.feishu.cn/)
3. **App Creation**: Create a custom app in the developer console

### OpenUser Requirements

1. OpenUser installed and running
2. Public URL for webhook (use ngrok for local development)
3. SSL certificate (Feishu requires HTTPS)

## Setup

### Step 1: Create Feishu App

1. Go to [Feishu Open Platform](https://open.feishu.cn/)
2. Click "Create Custom App"
3. Fill in app information:
   - **App Name**: OpenUser Bot
   - **App Description**: AI-powered digital human assistant
   - **App Icon**: Upload your logo

4. Note down your credentials:
   - **App ID**: `cli_xxxxxxxxxx`
   - **App Secret**: `xxxxxxxxxx`

### Step 2: Configure App Permissions

1. Go to "Permissions & Scopes"
2. Add required permissions:
   - `im:message` - Send and receive messages
   - `im:message.group_at_msg` - Receive group @ messages
   - `im:message.p2p_msg` - Receive private messages
   - `im:resource` - Upload images and files

3. Click "Save" and wait for approval

### Step 3: Set Up Webhook

1. Go to "Event Subscriptions"
2. Enable "Event Subscriptions"
3. Set webhook URL:
   ```
   https://your-domain.com/api/v1/integrations/feishu/webhook
   ```

4. Add event subscriptions:
   - `im.message.receive_v1` - Receive messages
   - `im.message.message_read_v1` - Message read status

5. Set encryption key (optional but recommended)

6. Click "Save" and verify the webhook

### Step 4: Configure OpenUser

1. Edit your `.env` file:

```bash
# Feishu Integration
FEISHU_APP_ID=cli_xxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxx  # Optional
FEISHU_WEBHOOK_URL=https://your-domain.com/api/v1/integrations/feishu/webhook
```

2. Restart OpenUser:

```bash
uvicorn src.api.main:app --reload
```

### Step 5: Test Integration

1. Add the bot to a Feishu group or chat
2. Send a message: `@OpenUser Bot Hello!`
3. The bot should respond

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FEISHU_APP_ID` | Yes | Your Feishu app ID |
| `FEISHU_APP_SECRET` | Yes | Your Feishu app secret |
| `FEISHU_VERIFICATION_TOKEN` | Yes | Webhook verification token |
| `FEISHU_ENCRYPT_KEY` | No | Message encryption key |
| `FEISHU_WEBHOOK_URL` | Yes | Your webhook URL |
| `FEISHU_DEFAULT_DIGITAL_HUMAN_ID` | No | Default digital human for responses |

### Advanced Configuration

Create `config/feishu.yaml`:

```yaml
feishu:
  # Bot behavior
  auto_reply: true
  reply_delay: 1  # seconds

  # Digital human settings
  default_digital_human_id: 1
  video_mode: "enhanced_talking_head"

  # Message handling
  max_message_length: 1000
  command_prefix: "/"

  # Rate limiting
  rate_limit:
    enabled: true
    max_requests: 60
    window: 60  # seconds

  # Features
  features:
    video_generation: true
    voice_synthesis: true
    interactive_cards: true
    file_upload: true
```

## Features

### 1. Message Handling

The integration automatically handles:

- **Text messages**: Process and respond to text
- **@ mentions**: Respond when bot is mentioned
- **Private messages**: Handle 1-on-1 conversations
- **Group messages**: Participate in group chats

### 2. Command System

Built-in commands:

- `/help` - Show help message
- `/video <text>` - Generate video with text
- `/voice <text>` - Synthesize voice
- `/status` - Check bot status
- `/settings` - View/change settings

### 3. Video Generation

Generate and send videos directly in Feishu:

```python
# User sends: /video Hello, welcome to our company!
# Bot generates video and sends it back
```

### 4. Interactive Cards

Send rich interactive cards:

```python
from src.integrations.feishu import send_card

card = {
    "header": {
        "title": {"content": "Digital Human Options"}
    },
    "elements": [
        {
            "tag": "div",
            "text": {"content": "Choose a digital human:"}
        },
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"content": "Human 1"},
                    "value": {"digital_human_id": 1}
                },
                {
                    "tag": "button",
                    "text": {"content": "Human 2"},
                    "value": {"digital_human_id": 2}
                }
            ]
        }
    ]
}

await send_card(chat_id, card)
```

### 5. File Handling

Upload and send files:

```python
from src.integrations.feishu import upload_file, send_file

# Upload video
file_key = await upload_file("/path/to/video.mp4", "video")

# Send to user
await send_file(chat_id, file_key, "video")
```

## Usage Examples

### Example 1: Simple Text Response

```python
from src.integrations.feishu import FeishuIntegration

feishu = FeishuIntegration()

@feishu.on_message
async def handle_message(event):
    """Handle incoming messages"""
    message = event.message.content
    chat_id = event.message.chat_id

    # Generate response
    response = f"You said: {message}"

    # Send response
    await feishu.send_text(chat_id, response)
```

### Example 2: Video Generation

```python
@feishu.on_command("/video")
async def generate_video(event, args):
    """Generate video from text"""
    text = " ".join(args)
    chat_id = event.message.chat_id

    # Send processing message
    await feishu.send_text(chat_id, "Generating video...")

    # Generate video
    from src.models.digital_human import generate_video
    video_path = await generate_video(
        digital_human_id=1,
        text=text,
        mode="enhanced_talking_head"
    )

    # Upload and send video
    file_key = await feishu.upload_file(video_path, "video")
    await feishu.send_file(chat_id, file_key, "video")
```

### Example 3: Interactive Card

```python
@feishu.on_command("/choose")
async def show_options(event):
    """Show digital human options"""
    chat_id = event.message.chat_id

    card = {
        "header": {
            "title": {"content": "Choose Digital Human"}
        },
        "elements": [
            {
                "tag": "div",
                "text": {"content": "Select a digital human for your video:"}
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"content": "Professional"},
                        "value": {"id": 1, "name": "professional"}
                    },
                    {
                        "tag": "button",
                        "text": {"content": "Friendly"},
                        "value": {"id": 2, "name": "friendly"}
                    },
                    {
                        "tag": "button",
                        "text": {"content": "Formal"},
                        "value": {"id": 3, "name": "formal"}
                    }
                ]
            }
        ]
    }

    await feishu.send_card(chat_id, card)

@feishu.on_card_action
async def handle_card_action(event):
    """Handle card button clicks"""
    action_value = event.action.value
    digital_human_id = action_value["id"]

    # Store user's choice
    await store_user_preference(event.user_id, digital_human_id)

    # Send confirmation
    await feishu.send_text(
        event.message.chat_id,
        f"Selected: {action_value['name']}"
    )
```

### Example 4: Scheduled Messages

```python
from src.integrations.feishu import schedule_message

# Schedule daily greeting
await schedule_message(
    chat_id="oc_xxxxxxxxxx",
    schedule="0 9 * * *",  # Every day at 9 AM
    message_type="video",
    content={
        "digital_human_id": 1,
        "text": "Good morning! Have a great day!",
        "mode": "enhanced_talking_head"
    }
)
```

## Troubleshooting

### Webhook Not Receiving Events

**Problem**: Webhook URL is not receiving events from Feishu

**Solutions**:
1. Verify webhook URL is publicly accessible
2. Check SSL certificate is valid
3. Ensure webhook verification is implemented correctly
4. Check Feishu app event subscriptions are enabled
5. Review webhook logs for errors

### Authentication Errors

**Problem**: 401 or 403 errors when calling Feishu API

**Solutions**:
1. Verify `FEISHU_APP_ID` and `FEISHU_APP_SECRET` are correct
2. Check app permissions are granted
3. Ensure access token is not expired
4. Refresh access token if needed

### Message Not Sent

**Problem**: Bot doesn't send messages

**Solutions**:
1. Check bot has `im:message` permission
2. Verify chat_id is correct
3. Check message format is valid
4. Review API response for errors
5. Check rate limits

### Video Upload Fails

**Problem**: Video upload returns error

**Solutions**:
1. Check file size (max 200MB)
2. Verify file format (MP4 recommended)
3. Ensure `im:resource` permission is granted
4. Check network connectivity
5. Try uploading smaller file

### Rate Limiting

**Problem**: Too many requests error

**Solutions**:
1. Implement rate limiting in your code
2. Use exponential backoff for retries
3. Cache responses when possible
4. Batch requests if applicable

## API Reference

### Send Text Message

```python
await feishu.send_text(chat_id: str, text: str) -> dict
```

### Send Card

```python
await feishu.send_card(chat_id: str, card: dict) -> dict
```

### Upload File

```python
await feishu.upload_file(file_path: str, file_type: str) -> str
```

### Send File

```python
await feishu.send_file(chat_id: str, file_key: str, file_type: str) -> dict
```

### Get User Info

```python
await feishu.get_user_info(user_id: str) -> dict
```

## Best Practices

1. **Error Handling**: Always handle API errors gracefully
2. **Rate Limiting**: Implement rate limiting to avoid hitting limits
3. **Logging**: Log all webhook events for debugging
4. **Security**: Validate webhook signatures
5. **Testing**: Test with different message types
6. **Monitoring**: Monitor webhook health and response times

## Resources

- [Feishu Open Platform](https://open.feishu.cn/)
- [Feishu API Documentation](https://open.feishu.cn/document/)
- [OpenUser Documentation](../INDEX.md)
- [GitHub Issues](https://github.com/yxhpy/openuser/issues)

## Support

For issues or questions:
- Check [Known Issues](../troubleshooting/KNOWN_ISSUES.md)
- Open a GitHub issue
- Contact support

## License

See [LICENSE](../../LICENSE) for details.
