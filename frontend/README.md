# Dynamic Railway ETA Prediction System — Frontend Foundation

This directory contains the React 19 + Vite frontend foundation for the **Dynamic Railway ETA Prediction System**.

## Tech Stack

- **React 19**: Modern UI component library.
- **Vite**: Ultra-fast next-generation frontend build tool and development server.
- **Tailwind CSS v4**: Utility-first CSS framework for clean, responsive styling.
- **Axios**: Promised-based HTTP client pre-configured to communicate with the FastAPI backend.
- **Lucide React**: Modern, consistent iconography.

## Project Structure

```text
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Top navigation, logo, and system status indicators
│   │   └── Footer.jsx          # Bottom layout bar with architecture badges
│   ├── pages/
│   │   └── Home.jsx            # Train search placeholder & architecture overview
│   ├── services/
│   │   └── api.js              # Centralized Axios API service with VITE_API_BASE_URL
│   ├── hooks/
│   │   └── useTrain.js         # Custom hook for train search & ETA state management
│   ├── utils/
│   │   └── formatters.js       # Formatting utilities for delays and timestamps
│   ├── App.jsx                 # Application shell assembling Header, Main, and Footer
│   ├── main.jsx                # React root mount
│   └── index.css               # Tailwind CSS imports and base typography
├── public/                     # Static assets
├── .env                        # Environment variables (git-ignored)
├── .gitignore                  # Git ignore rules
├── package.json                # Project dependencies and npm scripts
├── vite.config.js              # Vite configuration with React and Tailwind plugins
└── README.md                   # Frontend documentation
```

## Environment Configuration

The frontend connects exclusively to the FastAPI backend proxy:

```env
VITE_API_BASE_URL=http://localhost:8000
```

> **Security Guardrail**: The frontend never holds credentials for or connects directly to the RailRadar API. All data requests pass through FastAPI on port 8000.

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

The frontend will run at `http://localhost:5173`.
The backend runs at `http://localhost:8000`.

### 3. Build for Production

```bash
npm run build
```
