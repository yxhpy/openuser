# OpenUser User Guide

Welcome to OpenUser - an intelligent digital human system that enables you to create personalized AI avatars with your own voice, images, and videos.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your First Digital Human](#creating-your-first-digital-human)
3. [Generating Videos](#generating-videos)
4. [Managing Plugins](#managing-plugins)
5. [Scheduling Tasks](#scheduling-tasks)
6. [Platform Integrations](#platform-integrations)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Redis server
- (Optional) CUDA-capable GPU for faster processing

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yxhpy/openuser.git
cd openuser
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python -m src.models.db_init
```

6. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`.

### First-Time Setup

1. **Register an account**: Visit `http://localhost:8000/docs` and use the `/api/v1/auth/register` endpoint
2. **Login**: Use `/api/v1/auth/login` to get your access token
3. **Access the dashboard**: Open the web interface (if frontend is running)

### Starting the Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The web interface will be available at `http://localhost:3000`.

## Using the Web Interface

### User Authentication

#### Registration
1. Open `http://localhost:3000` in your browser
2. Click **"Sign up"** on the login page
3. Fill in the registration form:
   - **Username**: Choose a unique username (3-50 characters)
   - **Email**: Enter a valid email address
   - **Password**: Create a strong password (min 8 characters, must include uppercase, lowercase, number, and special character)
4. Click **"Sign Up"** to create your account
5. You'll be automatically logged in and redirected to the dashboard

#### Login
1. Open `http://localhost:3000`
2. Enter your **username** and **password**
3. Click **"Sign In"**
4. You'll be redirected to the dashboard upon successful login

### Dashboard Overview

The dashboard provides a real-time overview of your OpenUser system:

- **Digital Humans**: Total number of digital humans you've created
- **Plugins**: Number of installed plugins
- **Agents**: Number of configured AI agents
- **Scheduled Tasks**: Number of active scheduled tasks

All statistics are fetched in real-time from the API and update automatically.

### Navigation

Use the sidebar menu to navigate between sections:
- **Dashboard** - System overview with statistics
- **Digital Humans** - Create and manage AI avatars
- **Agents** - Configure AI agents with custom prompts
- **Plugins** - Install and manage plugins
- **Scheduler** - Create and manage scheduled tasks

### Managing Agents (Web Interface)

#### Creating an Agent
1. Navigate to **Agents** in the sidebar
2. Click **"Create Agent"** button
3. Fill in the agent details:
   - **Name**: Unique identifier (e.g., "assistant", "researcher")
   - **System Prompt**: Define the agent's behavior and personality
   - **Capabilities**: Comma-separated list (e.g., "plugin-install, self-update")
4. Click **"Create"** to save

#### Example System Prompts
- **General Assistant**: "You are a helpful AI assistant. Provide clear, concise, and accurate responses."
- **Code Reviewer**: "You are an expert code reviewer. Analyze code for bugs, security issues, and best practices."
- **Content Writer**: "You are a creative content writer. Generate engaging, well-structured content."

#### Editing an Agent
1. Navigate to **Agents**
2. Find the agent in the table
3. Click **"Edit"** button
4. Modify the system prompt or capabilities
5. Click **"Update"** to save changes

#### Deleting an Agent
1. Navigate to **Agents**
2. Find the agent in the table
3. Click **"Delete"** button
4. Confirm the deletion in the popup

### Managing Plugins (Web Interface)

#### Viewing Installed Plugins
1. Navigate to **Plugins** in the sidebar
2. View the list of installed plugins with:
   - Plugin name and version
   - Dependencies
   - Status (Active)
   - Actions (Reload button)

#### Installing a Plugin
1. Navigate to **Plugins**
2. Click **"Install Plugin"** button
3. Enter the plugin name in the modal
4. Click **"Install"**
5. Wait for installation to complete
6. The plugin list will refresh automatically

#### Hot-Reloading a Plugin
1. Navigate to **Plugins**
2. Find the plugin you want to reload
3. Click the **"Reload"** button
4. The plugin will be reloaded without system restart
5. A success message will confirm the reload

### Managing Scheduled Tasks (Web Interface)

#### Creating a Task
1. Navigate to **Scheduler** in the sidebar
2. Click **"Create Task"** button
3. Fill in the task details:
   - **Task Name**: Descriptive name
   - **Description**: Optional task description
   - **Task Type**: Select from dropdown (Video Generation, Voice Synthesis, etc.)
   - **Schedule**: Cron expression (e.g., `0 0 * * *` for daily at midnight)
   - **Parameters**: JSON object with task-specific parameters
4. Click **"Create"** to save

#### Cron Expression Examples
- `0 0 * * *` - Daily at midnight
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1-5` - Weekdays at 9 AM
- `*/30 * * * *` - Every 30 minutes

#### Viewing Task Status
The task list shows:
- **ID**: Task identifier
- **Name**: Task name
- **Type**: Task type (Video Generation, Voice Synthesis, etc.)
- **Status**: Current status with color coding:
  - **Pending** (gray): Waiting to run
  - **Running** (blue): Currently executing
  - **Completed** (green): Successfully finished
  - **Failed** (red): Encountered an error
  - **Cancelled** (orange): Manually stopped
- **Schedule**: Cron expression
- **Created**: Creation timestamp

#### Filtering Tasks
Use the filter dropdowns above the table:
- **Filter by Status**: Show only tasks with a specific status
- **Filter by Type**: Show only tasks of a specific type
- Click **"Refresh"** to reload the task list

#### Editing a Task
1. Navigate to **Scheduler**
2. Find the task in the table
3. Click **"Edit"** button
4. Modify the task details (name, description, schedule, parameters, status)
5. Click **"Update"** to save changes

**Note**: Task type cannot be changed after creation.

#### Deleting a Task
1. Navigate to **Scheduler**
2. Find the task in the table
3. Click **"Delete"** button
4. Confirm the deletion in the popup

### Statistics and Monitoring

The dashboard and individual pages show real-time statistics:
- **Dashboard**: Overall system statistics
- **Plugins Page**: Total plugins and active plugins count
- **Scheduler Page**: Task statistics by status (Total, Pending, Running, Completed, Failed)

All statistics update automatically when you perform actions (create, update, delete).

## Creating Your First Digital Human

### Step 1: Prepare Your Assets

You'll need:
- **Image**: A clear photo of the person (JPG, PNG)
- **Voice samples** (optional): 3-5 audio clips for voice cloning (WAV, MP3)
- **Description**: A brief description of your digital human

### Step 2: Create the Digital Human

Using the API:

```bash
curl -X POST "http://localhost:8000/api/v1/digital-human/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=My Digital Human" \
  -F "description=A friendly AI assistant" \
  -F "image=@/path/to/photo.jpg"
```

Using the web interface:
1. Navigate to "Digital Humans" page
2. Click "Create New"
3. Fill in the form and upload your image
4. Click "Create"

### Step 3: Set Up Voice Profile (Optional)

If you want voice cloning:

```bash
curl -X POST "http://localhost:8000/api/v1/voice/profiles" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=my-voice" \
  -F "samples=@sample1.wav" \
  -F "samples=@sample2.wav" \
  -F "samples=@sample3.wav"
```

## Generating Videos

### Generation Modes

OpenUser supports four video generation modes:

1. **lipsync**: Basic lip-sync using Wav2Lip
2. **talking_head**: Advanced talking head with natural movements (SadTalker)
3. **enhanced_lipsync**: Wav2Lip + GFPGAN face enhancement
4. **enhanced_talking_head**: SadTalker + GFPGAN (highest quality)

### Generate from Text

```bash
curl -X POST "http://localhost:8000/api/v1/digital-human/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "digital_human_id=1" \
  -F "text=Hello, welcome to OpenUser!" \
  -F "mode=enhanced_talking_head"
```

### Generate from Audio

```bash
curl -X POST "http://localhost:8000/api/v1/digital-human/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "digital_human_id=1" \
  -F "audio=@speech.wav" \
  -F "mode=enhanced_talking_head"
```

### Using Voice Cloning

```bash
curl -X POST "http://localhost:8000/api/v1/digital-human/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "digital_human_id=1" \
  -F "text=Hello, this is my cloned voice!" \
  -F "mode=enhanced_talking_head" \
  -F "speaker_wav=my-voice"
```

## Managing Plugins

### List Available Plugins

```bash
curl -X GET "http://localhost:8000/api/v1/plugins/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Install a Plugin

```bash
curl -X POST "http://localhost:8000/api/v1/plugins/install" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "image-processor"}'
```

### Reload a Plugin

Hot-reload a plugin without restarting the server:

```bash
curl -X POST "http://localhost:8000/api/v1/plugins/reload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "image-processor"}'
```

### Built-in Plugins

- **image-processor**: Image preprocessing and enhancement
- **video-editor**: Video editing utilities (trim, concat, format conversion)
- **audio-enhancer**: Audio enhancement and noise reduction
- **model-downloader**: Auto-download AI models
- **cache-manager**: Cache management with TTL and size limits

## Scheduling Tasks

### Create a Scheduled Task

```bash
curl -X POST "http://localhost:8000/api/v1/scheduler/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Video Generation",
    "description": "Generate a daily greeting video",
    "task_type": "video_generation",
    "schedule": "0 9 * * *",
    "params": {
      "digital_human_id": 1,
      "text": "Good morning! Have a great day!",
      "mode": "enhanced_talking_head"
    }
  }'
```

### Schedule Format

Uses cron syntax:
- `0 9 * * *` - Every day at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Every Sunday at midnight
- `*/30 * * * *` - Every 30 minutes

### Task Types

- `video_generation`: Generate digital human videos
- `voice_synthesis`: Synthesize speech
- `face_animation`: Animate faces
- `report_generation`: Generate reports
- `batch_processing`: Batch process multiple items
- `custom`: Custom task with your own logic

### List Scheduled Tasks

```bash
curl -X GET "http://localhost:8000/api/v1/scheduler/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update a Task

```bash
curl -X PUT "http://localhost:8000/api/v1/scheduler/{task_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 10 * * *",
    "status": "pending"
  }'
```

## Platform Integrations

### Feishu (Lark) Integration

See [Feishu Integration Guide](integrations/FEISHU.md) for detailed setup instructions.

Quick setup:
1. Create a Feishu app
2. Configure webhook URL
3. Set environment variables:
```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
```

### WeChat Work Integration

See [WeChat Work Integration Guide](integrations/WECHAT.md) for detailed setup instructions.

Quick setup:
1. Create a WeChat Work app
2. Configure webhook URL
3. Set environment variables:
```bash
WECHAT_CORP_ID=your_corp_id
WECHAT_CORP_SECRET=your_corp_secret
```

## Troubleshooting

### Common Issues

#### Video Generation Fails

**Problem**: Video generation returns an error

**Solutions**:
1. Check if models are downloaded: `ls models/`
2. Verify GPU/CPU settings in `.env`
3. Check disk space for output videos
4. Review logs: `tail -f logs/app.log`

#### Voice Synthesis Not Working

**Problem**: Voice synthesis fails or produces poor quality

**Solutions**:
1. Check TTS backend: `pyttsx3`, `gTTS`, or `Coqui TTS`
2. For Coqui TTS, ensure Python < 3.12
3. Verify audio sample quality (16kHz, mono recommended)
4. Check available disk space

#### Plugin Installation Fails

**Problem**: Plugin installation returns 404 or fails

**Solutions**:
1. Check plugin name spelling
2. Verify plugin exists in registry
3. Check network connectivity
4. Review plugin dependencies

#### Authentication Errors

**Problem**: 401 Unauthorized errors

**Solutions**:
1. Verify token is valid: check expiration
2. Use refresh token to get new access token
3. Re-login if refresh token expired
4. Check Authorization header format: `Bearer YOUR_TOKEN`

### Performance Optimization

#### GPU Acceleration

For faster video generation, use GPU:

```bash
# In .env
DEVICE=cuda
```

Verify GPU is available:
```python
import torch
print(torch.cuda.is_available())
```

#### Batch Processing

Process multiple videos efficiently:
1. Use scheduled tasks for batch jobs
2. Set appropriate batch sizes in config
3. Monitor GPU memory usage

#### Caching

Enable caching for frequently used models:
```bash
# In .env
CACHE_ENABLED=true
CACHE_SIZE_MB=2048
```

### Getting Help

- **Documentation**: Check [docs/](../docs/)
- **Known Issues**: See [KNOWN_ISSUES.md](troubleshooting/KNOWN_ISSUES.md)
- **GitHub Issues**: https://github.com/yxhpy/openuser/issues
- **API Reference**: http://localhost:8000/docs

## Best Practices

### Image Quality

- Use high-resolution images (at least 512x512)
- Ensure good lighting and clear facial features
- Avoid heavy makeup or accessories that obscure the face
- Front-facing photos work best

### Voice Cloning

- Provide 3-5 clear audio samples
- Each sample should be 5-10 seconds long
- Use consistent recording environment
- Avoid background noise
- Speak naturally and clearly

### Video Generation

- Start with `lipsync` mode for testing
- Use `enhanced_talking_head` for production
- Consider processing time vs quality trade-offs
- Monitor GPU memory for large batches

### Security

- Keep your `.env` file secure
- Use strong passwords
- Rotate access tokens regularly
- Enable HTTPS in production
- Restrict API access with firewall rules

## Next Steps

- Explore the [Developer Guide](DEVELOPER_GUIDE.md) to extend OpenUser
- Check out [Integration Guides](integrations/) for platform integrations
- Review [API Documentation](api/INDEX.md) for detailed API reference
- Join the community and contribute!

## License

See [LICENSE](../LICENSE) for details.
