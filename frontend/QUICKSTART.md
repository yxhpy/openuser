# OpenUser Frontend - Quick Start Guide

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## Installation

```bash
cd /Users/yxhpy/PycharmProjects/openuser/frontend
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## Features Available

### ✅ Authentication
- **Login**: http://localhost:3000/login
  - Username and password authentication
  - Automatic token storage
  - Redirects to dashboard on success

- **Register**: http://localhost:3000/register
  - Username, email, password fields
  - Strong password validation (min 8 chars, uppercase, lowercase, digit)
  - Email validation
  - Password confirmation

### ✅ Protected Routes
All routes below require authentication:

- **Dashboard**: http://localhost:3000/dashboard
  - Statistics overview
  - Quick access cards

- **Digital Humans**: http://localhost:3000/digital-humans
  - (Placeholder - Phase 5)

- **Plugins**: http://localhost:3000/plugins
  - (Placeholder - Phase 6)

- **Agents**: http://localhost:3000/agents
  - (Placeholder - Phase 7)

- **Scheduler**: http://localhost:3000/scheduler
  - (Placeholder - Phase 8)

## Testing Authentication Flow

1. Start the backend API server (port 8000)
2. Start the frontend dev server (port 3000)
3. Navigate to http://localhost:3000
4. You'll be redirected to /login
5. Register a new account or login with existing credentials
6. Upon successful login, you'll be redirected to /dashboard
7. Try navigating between pages using the sidebar menu
8. Click on your username in the header to logout

## API Integration

The frontend is configured to proxy API requests to the backend:

- API Base URL: `http://localhost:8000`
- All `/api/*` requests are proxied to the backend
- WebSocket connections: `ws://localhost:8000`

### API Endpoints Used

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user

## Token Management

- Access token and refresh token are stored in localStorage
- Axios interceptor automatically adds Bearer token to all requests
- On 401 error, the interceptor attempts to refresh the token
- If refresh fails, user is redirected to login

## Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Troubleshooting

### Port 3000 already in use
```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9
```

### Backend not responding
Make sure the backend API is running on port 8000:
```bash
cd /Users/yxhpy/PycharmProjects/openuser
uvicorn src.api.main:app --reload
```

### CORS errors
The Vite proxy should handle CORS. If you see CORS errors, check:
1. Backend is running on port 8000
2. Vite config proxy is correct
3. Backend CORS settings allow localhost:3000

## Next Steps

Continue with Phase 5: Digital Human Management
- Implement digital human list page
- Create multi-step creation wizard
- Add file upload for images
- Implement video generation

See `IMPLEMENTATION_STATUS.md` for detailed progress.
