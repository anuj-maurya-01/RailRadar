# Production Deployment Guide

This guide walks you through deploying **YatriRail** ("Live Indian Railway Intelligence") to the cloud:
- **Backend (FastAPI + Machine Learning)** &rarr; [Render](https://render.com)
- **Frontend (React + Vite + Leaflet)** &rarr; [Vercel](https://vercel.com)

---

## Architecture Overview

```text
┌─────────────────────────────────┐
│     Vercel (React Frontend)     │
│   https://yatrirail.vercel.app  │
└────────────────┬────────────────┘
                 │
                 │ HTTPS API Calls (VITE_API_BASE_URL)
                 ▼
┌─────────────────────────────────┐
│     Render (FastAPI Backend)    │
│  https://yatrirail.onrender.com │
└────────────────┬────────────────┘
                 │
                 ├─► HistGradientBoostingRegressor ML Model (backend/model/)
                 ├─► RailRadar API (Live GPS telemetry)
                 └─► Background Periodic Scheduler (APScheduler)
```

---

## Part 1: Deploy Backend to Render

You can deploy the backend using either **Method A (Render Blueprint - Recommended)** or **Method B (Manual Dashboard Setup)**.

### Method A: Render Blueprint (`render.yaml` - 1-Click)

1. Log in to [Render](https://dashboard.render.com/).
2. Click **New +** in the top navigation and select **Blueprint**.
3. Connect your GitHub repository (`YatriRail`).
4. Render will automatically detect [`render.yaml`](render.yaml) in your repository root.
5. In the configuration prompt, provide your environment variables:
   - `RAILRADAR_API_KEY`: Your RailRadar API key (e.g. `rg_...`).
   - `FRONTEND_URL`: Set to `https://*.vercel.app` (or leave default to allow all Vercel deployments).
6. Click **Apply**. Render will automatically build the service and deploy it.

---

### Method B: Manual Web Service Setup on Render

If you prefer to configure manually via the Render Dashboard:

1. Log in to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** &rarr; **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your repository (`YatriRail`).
4. Configure the service settings:
   - **Name**: `yatrirail-backend` (or your preferred name)
   - **Region**: Choose the region closest to your users (e.g., `Singapore` or `Oregon`)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free`

5. Open **Advanced** &rarr; **Health Check Path**:
   - Set **Health Check Path** to `/api/health`.

6. Add **Environment Variables**:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Ensures compatible Linux wheels for scikit-learn & numpy |
   | `RAILRADAR_API_KEY` | `your_railradar_api_key` | RailRadar telemetry authentication key |
   | `RAILRADAR_API_BASE_URL` | `https://api.railradar.in` | RailRadar base API URL |
   | `RAILRADAR_API_ENDPOINT` | `/v1/trains/{number}/live` | Upstream live endpoint |
   | `FRONTEND_URL` | `https://*.vercel.app` | Allowed CORS origin (comma-separated list supported) |
   | `TRACKED_TRAIN_NUMBERS` | `11013,11014` | Trains tracked by background scheduler |
   | `COLLECTION_INTERVAL_MINUTES` | `15` | Periodic telemetry poll interval |

7. Click **Create Web Service**.

> [!NOTE]
> Once deployment completes, note down your Render Web Service URL (e.g. `https://yatrirail-backend.onrender.com`). You will need this URL for the frontend configuration.

---

## Part 2: Deploy Frontend to Vercel

### Method A: Vercel Dashboard (Recommended)

1. Log in to [Vercel](https://vercel.com/dashboard).
2. Click **Add New...** &rarr; **Project**.
3. Import your GitHub repository (`YatriRail`).
4. In the **Configure Project** screen:
   - **Project Name**: `yatrirail` (or your preferred name)
   - **Framework Preset**: `Vite` (automatically detected)
   - **Root Directory**: Click **Edit** and select **`frontend`** &rarr; click **Continue**.
   - **Build and Output Settings**:
     - Build Command: `npm run build` (default)
     - Output Directory: `dist` (default)
     - Install Command: `npm install` (default)
5. Under **Environment Variables**, add:
   | Name | Value | Description |
   | :--- | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://yatrirail-backend.onrender.com` | **Your Render backend URL** (without trailing slash) |
6. Click **Deploy**.

Vercel will build the frontend and assign a live production URL (e.g. `https://yatrirail.vercel.app`).

---

### Method B: Vercel CLI

If you have Node.js installed locally, you can deploy directly using `npx vercel`:

```bash
cd frontend
npx vercel
```
1. Follow the interactive prompts to link or create a project.
2. When asked for settings, select Vite and `dist` output.
3. Set your production environment variable:
   ```bash
   npx vercel env add VITE_API_BASE_URL production
   # Enter your Render URL: https://yatrirail-backend.onrender.com
   ```
4. Deploy to production:
   ```bash
   npx vercel --prod
   ```

---

## Part 3: Verify the Deployment

1. **Verify Backend Health**:
   - Open `https://<YOUR-RENDER-BACKEND>.onrender.com/` &rarr; Returns JSON status:
     ```json
     {
       "service": "YatriRail API",
       "status": "online",
       "version": "1.0.0",
       "docs": "/docs",
       "health": "/api/health"
     }
     ```
   - Open `https://<YOUR-RENDER-BACKEND>.onrender.com/docs` to view the interactive Swagger OpenAPI UI.

2. **Verify Frontend**:
   - Open your Vercel deployment URL (e.g. `https://yatrirail.vercel.app`).
   - Enter a train number (e.g., `11013` or `11014`) into the search bar and press **Track Train**.
   - The interactive Leaflet route map, ML delay prediction cards, and live route timeline should load.

---

## Free-Tier Notes & Troubleshooting

### 1. Render Free Tier Spin-Down ("Cold Start")
- Render's free tier services spin down into a sleep state after 15 minutes of inactivity.
- When an initial request is made, the service may take 30 to 50 seconds to boot up.
- **Handled**: The frontend Axios client is configured with a 60-second timeout (`timeout: 60000`) so user searches won't fail prematurely during cold starts.

### 2. CORS Errors
- The backend dynamically allows:
  - Any URL ending in `.vercel.app` (covers production and preview deployments)
  - Any domain explicitly configured in the `FRONTEND_URL` environment variable
- If you use a custom domain on Vercel (e.g. `https://yatrirail.mycustomdomain.com`), add it to `FRONTEND_URL` in your Render Environment Variables (separate multiple URLs with commas):
  ```env
  FRONTEND_URL=https://yatrirail.mycustomdomain.com,https://yatrirail.vercel.app
  ```

### 3. Missing API Key Fallback
- If `RAILRADAR_API_KEY` is not provided or upstream services are unavailable, the backend automatically falls back to bundled historical route datasets (`Dataset_1`) so the platform remains fully functional for demonstration.
