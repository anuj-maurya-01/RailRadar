# 🚆 YatriRail — Frontend Application

[![React](https://img.shields.io/badge/React-19.2+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0+-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9+-199900?style=flat-square&logo=leaflet&logoColor=white)](https://leafletjs.com/)

A modern, responsive, transportation intelligence dashboard for **YatriRail** ("Live Indian Railway Intelligence"), featuring interactive railway route mapping, live operational KPIs, real-time delay alerts, and dynamic ML arrival forecasts.

---

## 🛠️ Tech Stack

- **React 19**: Ultra-responsive UI rendering with concurrent capabilities.
- **Vite 8**: Lightning-fast bundler with Hot Module Replacement (HMR).
- **Tailwind CSS v4**: High-performance modern CSS engine for transportation dashboard design.
- **Leaflet & React-Leaflet**: Hardware-accelerated map rendering with custom SVG locomotive markers and route polylines.
- **Axios**: Promised-based HTTP client communicating with the FastAPI proxy.
- **Lucide React**: Modern iconography.

---

## 📁 Component Architecture

```text
frontend/src/
├── components/
│   ├── KpiCards.jsx            # Real-time operational metric counters (Active, On Time, Delayed, Cancelled)
│   ├── LiveIndicator.jsx       # Pulsing live telemetry sync badge with countdown & manual refresh
│   ├── TrainMap.jsx            # 60% operational map with animated route tracing & pulsing train marker
│   ├── SelectedTrainPanel.jsx  # 40% active train telemetry, speed, corridor & ML delay forecast
│   ├── AlertsCard.jsx          # Live delay alerts banner for active network disruptions
│   ├── TrainTable.jsx          # Searchable, sortable, paginated station operations table with filter pills
│   ├── RouteTimeline.jsx       # Space-efficient bounded timeline with auto-scroll & "Jump to Live"
│   ├── ETADelayChart.jsx       # Journey delay and station dwell visualization
│   └── Header.jsx              # Navigation bar with smart train search autocomplete & theme toggle
├── pages/
│   └── Home.jsx                # Main YatriRail intelligence dashboard assembling all panels
├── services/
│   └── apiClient.js            # Axios client with fallback endpoints and error handling
├── utils/
│   └── formatters.js           # Formatter helpers for delay minutes, distance, and timestamps
├── App.jsx                     # Root application wrapper with dark/light theme context
└── main.jsx                    # React 19 mount point
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Node.js `18.x`, `20.x`, or `22.x` (with `npm`).

### 2. Installation

```bash
cd frontend
npm install
```

### 3. Environment Configuration

Create a `.env` file in `frontend/`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

> **Architecture Security**: The frontend communicates exclusively with the local FastAPI backend. No external third-party API keys are ever stored or bundled into the client application.

### 4. Run Development Server

```bash
npm run dev
```

The application will be live at `http://localhost:5173`.

### 5. Build for Production

```bash
npm run build
```

Production build artifacts will be generated in `frontend/dist/`.
