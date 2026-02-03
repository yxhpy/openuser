# OpenUser Frontend

React-based web interface for the OpenUser digital human system.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Ant Design 5** - UI component library
- **Zustand** - State management
- **Axios** - HTTP client
- **React Router v6** - Routing

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

The API proxy is configured to forward `/api` requests to http://localhost:8000

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Environment Variables

Create a `.env.development` file for local development:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

For production, create a `.env.production` file:

```bash
VITE_API_BASE_URL=https://api.openuser.com
VITE_WS_URL=wss://api.openuser.com
```

## Project Structure

```
src/
├── api/                    # API client layer
├── components/             # Reusable components
│   ├── common/            # Common components (Layout, ProtectedRoute)
│   ├── auth/              # Authentication components
│   ├── digitalHuman/      # Digital human components
│   ├── plugins/           # Plugin components
│   ├── agents/            # Agent components
│   └── scheduler/         # Scheduler components
├── hooks/                 # Custom React hooks
├── pages/                 # Page components
├── store/                 # Zustand stores
├── types/                 # TypeScript types
├── utils/                 # Utility functions
├── App.tsx               # Root component
├── main.tsx              # Entry point
└── router.tsx            # Route configuration
```

## Features

- User authentication (login/register)
- Protected routes with automatic token refresh
- Digital human management
- Plugin management
- Agent management
- Task scheduler
- Real-time WebSocket updates

## Development Notes

- All API calls use JWT Bearer token authentication
- Tokens are stored in localStorage
- Axios interceptor handles automatic token refresh on 401 errors
- Protected routes redirect to login if not authenticated
