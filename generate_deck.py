import os
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

def create_presentation_deck(output_path="YatriRail_Presentation_Deck.pdf"):
    # 16:9 Widescreen dimensions (960 x 540 points)
    width = 960
    height = 540
    c = canvas.Canvas(output_path, pagesize=(width, height))

    # Color Palette
    bg_dark = HexColor("#090D16")
    card_bg = HexColor("#111827")
    card_border = HexColor("#1F2937")
    card_highlight = HexColor("#1E293B")
    card_inner = HexColor("#162032")
    
    accent_blue = HexColor("#38BDF8")      # Sky blue / Cyan
    accent_indigo = HexColor("#6366F1")    # Indigo
    accent_emerald = HexColor("#10B981")   # Emerald green
    accent_amber = HexColor("#F59E0B")     # Amber warning
    accent_rose = HexColor("#F43F5E")      # Rose alert
    
    text_primary = HexColor("#F8FAFC")     # Off white
    text_secondary = HexColor("#94A3B8")   # Slate 400
    text_muted = HexColor("#64748B")       # Slate 500

    def draw_bullet(x, y, color=accent_blue):
        c.setFillColor(color)
        c.circle(x, y + 3, 2, stroke=0, fill=1)

    def draw_slide_base(eyebrow_text, title_text, subtitle_text, slide_num, total_slides=10):
        """Draw common dark background, top accent bar, slide titles, and footer with clean spacing."""
        # Canvas Background
        c.setFillColor(bg_dark)
        c.rect(0, 0, width, height, stroke=0, fill=1)

        # Top subtle railway track gradient line
        c.setFillColor(accent_blue)
        c.rect(0, height - 4, width, 4, stroke=0, fill=1)

        # Slide Number Badge (Top Right)
        c.setFillColor(card_highlight)
        c.roundRect(width - 105, height - 38, 55, 22, 4, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(accent_blue)
        c.drawCentredString(width - 77, height - 32, f"{slide_num:02d} / {total_slides:02d}")

        # Eyebrow / Category
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(accent_blue)
        c.drawString(50, height - 34, eyebrow_text.upper())

        # Main Title
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(text_primary)
        c.drawString(50, height - 62, title_text)

        # Subtitle
        if subtitle_text:
            c.setFont("Helvetica", 10)
            c.setFillColor(text_secondary)
            c.drawString(50, height - 80, subtitle_text)

        # Footer divider and text
        c.setStrokeColor(HexColor("#1E293B"))
        c.setLineWidth(1)
        c.line(50, 36, width - 50, 36)

        c.setFont("Helvetica", 8)
        c.setFillColor(text_muted)
        c.drawString(50, 20, "YatriRail - Live Indian Railway Intelligence & Dynamic ML ETA Forecasting")
        c.drawRightString(width - 50, 20, "Hackathon 2026 Presentation Deck")

    # =========================================================================
    # SLIDE 1: Title & Hackathon Overview
    # =========================================================================
    c.setFillColor(bg_dark)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Top accent line
    c.setFillColor(accent_blue)
    c.rect(0, height - 5, width, 5, stroke=0, fill=1)

    # Badge: Hackathon Submission
    c.setFillColor(HexColor("#1E293B"))
    c.roundRect(50, height - 55, 215, 24, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(accent_blue)
    c.drawString(62, height - 44, "HACKATHON PROJECT PRESENTATION")

    # Hero Title
    c.setFont("Helvetica-Bold", 38)
    c.setFillColor(text_primary)
    c.drawString(50, height - 105, "YATRI RAIL")

    # Sub-hero Tagline
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(accent_blue)
    c.drawString(50, height - 132, "Live Indian Railway Intelligence & Dynamic Machine Learning ETA Forecasting")

    c.setFont("Helvetica", 11)
    c.setFillColor(text_secondary)
    c.drawString(50, height - 154, "Fusing real-time GPS telemetry, route timetables, and gradient-boosted decision trees to predict arrival shifts.")

    # 3 Cards on Title Slide
    # Card 1: Core Innovation
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.setLineWidth(1)
    c.roundRect(50, 140, 265, 180, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(68, 296, "The Core Innovation")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    bullets1 = [
        "12-Feature Gradient Boosting Regressor",
        "Dynamic arrival delay shifts per halt",
        "Replaces naive static extrapolations",
        "Sub-5ms machine learning inference",
        "Confidence-scored arrival estimates",
    ]
    by = 268
    for b in bullets1:
        draw_bullet(68, by, accent_blue)
        c.drawString(78, by, b)
        by -= 22

    # Card 2: Interactive Operations UI
    c.setFillColor(card_bg)
    c.roundRect(346, 140, 265, 180, 8, stroke=1, fill=1)
    c.setFillColor(accent_emerald)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(364, 296, "Situational Intelligence")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    bullets2 = [
        "60/40 Operational Split Screen layout",
        "Interactive Leaflet map with pulsing train",
        "Real-time network KPIs & delay alerts",
        "8,490 Indian Railways trains searchable",
        "Space-efficient station timeline auto-scroll",
    ]
    by = 268
    for b in bullets2:
        draw_bullet(364, by, accent_emerald)
        c.drawString(374, by, b)
        by -= 22

    # Card 3: Hackathon Team
    c.setFillColor(card_bg)
    c.roundRect(642, 140, 268, 180, 8, stroke=1, fill=1)
    c.setFillColor(accent_indigo)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(660, 296, "The Hackathon Team")
    
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_primary)
    c.drawString(660, 270, "Anuj Maurya")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(660, 258, "Frontend / Map & Dashboard")

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_primary)
    c.drawString(660, 238, "Archita Kesharwani")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(660, 226, "Backend / Real-Time Engine")

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_primary)
    c.drawString(660, 206, "Aru Shubham Singh")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(660, 194, "ML / ETA Prediction")

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_primary)
    c.drawString(660, 174, "Shlok Bhardwaj")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(660, 162, "Data Analytics & Research")

    # Bottom Meta Bar
    c.setFillColor(HexColor("#111827"))
    c.roundRect(50, 50, 860, 68, 8, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(text_primary)
    c.drawString(65, 92, "Live Prototype Status:")
    c.setFont("Helvetica", 10)
    c.setFillColor(accent_emerald)
    c.drawString(195, 92, "Production Ready (Backend on Render | Frontend on Vercel | 59 Passing Tests)")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(65, 72, "Tech Stack: FastAPI (Python 3.11+) | React 19 | Vite 8 | Tailwind CSS 4 | Scikit-learn | Leaflet | Joblib")
    c.drawString(65, 58, "Public GitHub Repository: https://github.com/anuj-maurya-01/YatriRail")

    c.showPage()

    # =========================================================================
    # SLIDE 2: The Problem: Arrival Delay Uncertainty
    # =========================================================================
    draw_slide_base(
        "The Problem Statement",
        "Traditional Train Tracking Fails 24 Million Commuters Daily",
        "Static timetables and crude single-checkpoint extrapolations generate severe information asymmetry.",
        2
    )

    card_w = 266
    card_h = 350
    y_pos = 58

    # Card 1: Static Timetables
    c.setFillColor(card_bg)
    c.setStrokeColor(HexColor("#374151"))
    c.roundRect(50, y_pos, card_w, card_h, 8, stroke=1, fill=1)
    c.setFillColor(accent_rose)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(68, y_pos + card_h - 28, "01. Static Timetable Fiction")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    c.drawString(68, y_pos + card_h - 52, "Traditional rail tracking services assume")
    c.drawString(68, y_pos + card_h - 68, "trains will magically stick to scheduled")
    c.drawString(68, y_pos + card_h - 84, "timetables despite operational disruptions.")
    
    c.setFillColor(card_inner)
    c.roundRect(65, y_pos + 35, card_w - 30, 205, 6, stroke=0, fill=1)
    c.setFillColor(accent_rose)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(78, y_pos + 215, "KEY LIMITATIONS:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    p_bullets1 = [
        "Ignores cumulative network congestion",
        "Cannot foresee junction bottlenecks",
        "Blinds passengers to snowball delays",
        "Leads to missed platform connections",
        "Platform overcrowding & panic",
    ]
    py = y_pos + 190
    for b in p_bullets1:
        draw_bullet(78, py, accent_rose)
        c.drawString(88, py, b)
        py -= 22
    
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(78, y_pos + 60, "Result: High passenger anxiety")

    # Card 2: Naive Extrapolations
    c.setFillColor(card_bg)
    c.roundRect(346, y_pos, card_w, card_h, 8, stroke=1, fill=1)
    c.setFillColor(accent_amber)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(364, y_pos + card_h - 28, "02. Naive Extrapolation")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    c.drawString(364, y_pos + card_h - 52, "Existing tracking applications copy-paste")
    c.drawString(364, y_pos + card_h - 68, "the latest reported station delay across all")
    c.drawString(364, y_pos + card_h - 84, "remaining stops without adjustment.")

    c.setFillColor(card_inner)
    c.roundRect(361, y_pos + 35, card_w - 30, 205, 6, stroke=0, fill=1)
    c.setFillColor(accent_amber)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(374, y_pos + 215, "FLAWED LOGIC:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    p_bullets2 = [
        "If +20 min at Stop 3, assumes exactly",
        "  +20 min at Stop 25 (false assumption)",
        "Misses track speed recovery zones",
        "Overlooks rush-hour congestion dips",
        "Fails to model single-track waits",
    ]
    py = y_pos + 190
    for b in p_bullets2:
        draw_bullet(374, py, accent_amber)
        c.drawString(384, py, b)
        py -= 22
    
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(374, y_pos + 60, "Result: Wildly inaccurate ETAs")

    # Card 3: Economic & Human Impact
    c.setFillColor(card_bg)
    c.roundRect(642, y_pos, card_w, card_h, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(660, y_pos + card_h - 28, "03. Massive National Scale")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    c.drawString(660, y_pos + card_h - 52, "Indian Railways operates 13,000+ trains")
    c.drawString(660, y_pos + card_h - 68, "daily across 68,000+ km of tracks,")
    c.drawString(660, y_pos + card_h - 84, "connecting 7,300+ stations.")

    c.setFillColor(card_inner)
    c.roundRect(657, y_pos + 35, card_w - 30, 205, 6, stroke=0, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(670, y_pos + 215, "SYSTEMIC IMPACT:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    p_bullets3 = [
        "24M+ daily commuters impacted",
        "Station platform overcrowding",
        "Operational friction for crew schedulers",
        "Lack of forward-looking predictions",
        "Zero delay confidence metrics",
    ]
    py = y_pos + 190
    for b in p_bullets3:
        draw_bullet(670, py, accent_blue)
        c.drawString(680, py, b)
        py -= 22
    
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(accent_emerald)
    c.drawString(670, y_pos + 60, "Solution: Machine Learning Engine")

    c.showPage()

    # =========================================================================
    # SLIDE 3: The Solution: YatriRail
    # =========================================================================
    draw_slide_base(
        "Our Solution",
        "YatriRail: Live Indian Railway Intelligence",
        "Replacing guesswork with machine-learning arrival predictions and real-time situational awareness.",
        3
    )

    gw = 415
    gh = 168
    
    # Top-Left: Dynamic ML ETA Engine
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, 240, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(70, 240 + gh - 28, "Dynamic ML Delay & ETA Forecasting")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    s_bullets1 = [
        "Pre-trained HistGradientBoostingRegressor analyzes 12 operational features.",
        "Differentiates between recorded ground delay and predicted corridor delay.",
        "Dynamically calculates expected arrival and departure times per upcoming stop.",
        "Sub-5ms inference enables real-time updates without database slowdowns.",
    ]
    sy = 240 + gh - 54
    for b in s_bullets1:
        draw_bullet(70, sy, accent_blue)
        c.drawString(80, sy, b)
        sy -= 24

    # Top-Right: 60/40 Split Operational UI
    c.setFillColor(card_bg)
    c.roundRect(495, 240, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_emerald)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(515, 240 + gh - 28, "60/40 Operational Split Dashboard")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    s_bullets2 = [
        "60% Interactive Leaflet Map: Polyline route corridors and station halos.",
        "Custom SVG Locomotive Marker with real-time pulsing radar beacon.",
        "40% Selected Train Telemetry: Current speed, delay badges, and ML deltas.",
        "Zero third-party mapping API keys required; OpenStreetMap tiles powered.",
    ]
    sy = 240 + gh - 54
    for b in s_bullets2:
        draw_bullet(515, sy, accent_emerald)
        c.drawString(525, sy, b)
        sy -= 24

    # Bottom-Left: Network KPIs & Alerts
    c.setFillColor(card_bg)
    c.roundRect(50, 58, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_amber)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(70, 58 + gh - 28, "Network KPIs & Critical Delay Alerts")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    s_bullets3 = [
        "4 Clickable Operational KPI Cards: Active Trains, On Time, Delayed, Cancelled.",
        "Real-time automated alert thresholding (>=10m Warning, >=25m Alert).",
        "Station Operations Table with in-table search, sorting, and pagination.",
        "Compact station timeline with auto-scroll to active halt & 'Jump to Live'.",
    ]
    sy = 58 + gh - 54
    for b in s_bullets3:
        draw_bullet(70, sy, accent_amber)
        c.drawString(80, sy, b)
        sy -= 24

    # Bottom-Right: Resilient Offline Fallback
    c.setFillColor(card_bg)
    c.roundRect(495, 58, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_indigo)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(515, 58 + gh - 28, "Enterprise Resilience & Zero Downtime")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    s_bullets4 = [
        "Graceful Fallback Engine: Recovers on HTTP 429 upstream rate limit errors.",
        "Bundled 8,490 Indian Railways train database indexed in-memory.",
        "Mathematical coordinate interpolation fills missing GPS station waypoints.",
        "59 Automated Unit and Integration Tests guarantee operational stability.",
    ]
    sy = 58 + gh - 54
    for b in s_bullets4:
        draw_bullet(515, sy, accent_indigo)
        c.drawString(525, sy, b)
        sy -= 24

    c.showPage()

    # =========================================================================
    # SLIDE 4: System Architecture & End-to-End Data Flow
    # =========================================================================
    draw_slide_base(
        "System Architecture",
        "Modern Three-Tier Architecture & Data Pipeline",
        "Decoupled, high-throughput asynchronous proxy with client security and rapid inference.",
        4
    )

    col_w = 266
    col_h = 350
    col_y = 58

    # Layer 1: Frontend Client
    c.setFillColor(card_bg)
    c.setStrokeColor(accent_blue)
    c.roundRect(50, col_y, col_w, col_h, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(68, col_y + col_h - 26, "1. Frontend Client Tier")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(68, col_y + col_h - 42, "REACT 19 * VITE 8 * TAILWIND 4")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    a_bullets1 = [
        "60/40 Split Operational UI layout",
        "TrainMap (Leaflet hardware accelerated)",
        "Custom SVG Locomotive Pulsing Marker",
        "SelectedTrainPanel live telemetry",
        "Bounded RouteTimeline with auto-scroll",
        "Instant debounced search across 8,490 trains",
        "Non-blocking 30s background sync polling",
        "Dual Light/Dark transportation themes",
    ]
    ay = col_y + col_h - 68
    for b in a_bullets1:
        draw_bullet(68, ay, accent_blue)
        c.drawString(78, ay, b)
        ay -= 20
    
    c.setFillColor(card_inner)
    c.roundRect(65, col_y + 16, col_w - 30, 48, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(75, col_y + 46, "Hosting: Vercel Cloud Edge")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(75, col_y + 30, "HTTPS * Client SPA * Vercel CDN")

    # Layer 2: Backend Proxy & Normalizer
    c.setFillColor(card_bg)
    c.setStrokeColor(accent_emerald)
    c.roundRect(346, col_y, col_w, col_h, 8, stroke=1, fill=1)
    c.setFillColor(accent_emerald)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(364, col_y + col_h - 26, "2. API Gateway & Logic")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(364, col_y + col_h - 42, "FASTAPI * UVICORN * PYTHON 3.11+")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    a_bullets2 = [
        "GET /api/trains/live-summary",
        "GET /api/trains/search-suggestions",
        "GET /api/train/{train_number}",
        "GET /api/health (Uptime Monitor)",
        "Strict CORS & API Key isolation",
        "Data Normalizer & Schema Validator",
        "Mathematical Station Interpolation",
        "12-Feature Engineering Pipeline",
        "Graceful HTTP 429 rate-limit failover",
    ]
    ay = col_y + col_h - 68
    for b in a_bullets2:
        draw_bullet(364, ay, accent_emerald)
        c.drawString(374, ay, b)
        ay -= 18

    c.setFillColor(card_inner)
    c.roundRect(361, col_y + 16, col_w - 30, 48, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(371, col_y + 46, "Hosting: Render Web Service")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(371, col_y + 30, "render.yaml Blueprint * Health Check")

    # Layer 3: ML & Data Layer
    c.setFillColor(card_bg)
    c.setStrokeColor(accent_indigo)
    c.roundRect(642, col_y, col_w, col_h, 8, stroke=1, fill=1)
    c.setFillColor(accent_indigo)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(660, col_y + col_h - 26, "3. ML & Data Fabric")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(660, col_y + col_h - 42, "SCIKIT-LEARN * JOBLIB * PANDAS")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    a_bullets3 = [
        "HistGradientBoostingRegressor",
        "Pre-fitted OneHotEncoder (Categoricals)",
        "Sub-5ms inference per train query",
        "Dual Data Feed Architecture:",
        "  1. Live RailRadar GPS Telemetry",
        "  2. Bundled 8,490-Train Database",
        "APScheduler Background Harvester",
        "JSONL Telemetry Recording",
        "Dynamic arrival delta calculators",
    ]
    ay = col_y + col_h - 68
    for b in a_bullets3:
        draw_bullet(660, ay, accent_indigo)
        c.drawString(670, ay, b)
        ay -= 18

    c.setFillColor(card_inner)
    c.roundRect(657, col_y + 16, col_w - 30, 48, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(667, col_y + 46, "Offline Fallback Database:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(667, col_y + 30, "8,490 Pre-indexed Route Schedules")

    c.showPage()

    # =========================================================================
    # SLIDE 5: Machine Learning Engine & Feature Pipeline
    # =========================================================================
    draw_slide_base(
        "Machine Learning Engine",
        "12-Feature HistGradientBoosting Delay Forecaster",
        "Statistical delay adjustments accounting for non-linear corridor dynamics, speed, and time.",
        5
    )

    # Left Column: Feature Engineering Table
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, 58, 480, 350, 8, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(accent_blue)
    c.drawString(70, 382, "Engineered Input Feature Matrix (12 Variables)")

    headers = [("Feature Name", 70), ("Type", 230), ("Operational Significance", 300)]
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_muted)
    for h, x in headers:
        c.drawString(x, 360, h)
    c.setStrokeColor(HexColor("#1E293B"))
    c.line(70, 352, 510, 352)

    features = [
        ("current_delay_min", "Numeric", "Baseline ground delay at latest halt"),
        ("distance_covered_km", "Numeric", "Track progress from route origin"),
        ("distance_remaining_km", "Numeric", "Remaining distance to final terminus"),
        ("scheduled_travel_time_min", "Numeric", "Total timetable allocated duration"),
        ("time_elapsed_min", "Numeric", "Actual journey operational time elapsed"),
        ("current_speed_kmh", "Numeric", "Instantaneous GPS/segment velocity"),
        ("average_speed_kmh", "Numeric", "Cumulative running velocity with halts"),
        ("station_progress_pct", "Numeric", "Route completion fraction (0.0 - 1.0)"),
        ("day_of_week", "Categoric", "Monday - Sunday (One-Hot Encoded)"),
        ("time_of_day", "Categoric", "Morning, Afternoon, Evening, Night"),
        ("rush_hour", "Categoric", "Peak congestion corridor flag (0 or 1)"),
        ("train_type", "Categoric", "Service priority (RAJ, SHT, SF, EXP)"),
    ]

    c.setFont("Helvetica", 8)
    row_y = 336
    for name, ftype, desc in features:
        c.setFillColor(accent_blue if ftype == "Numeric" else accent_indigo)
        c.drawString(70, row_y, name)
        c.setFillColor(text_secondary)
        c.drawString(230, row_y, ftype)
        c.drawString(300, row_y, desc)
        row_y -= 22

    # Right Column: Model Design & Formula
    c.setFillColor(card_bg)
    c.roundRect(550, 58, 360, 350, 8, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(accent_emerald)
    c.drawString(570, 382, "Mathematical Formulation & Reasoning")

    # Formula Box
    c.setFillColor(card_inner)
    c.roundRect(570, 290, 320, 72, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(585, 344, "DYNAMIC ETA FORMULA:")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(accent_blue)
    c.drawString(585, 324, "ETA = Timetable Arrival + Delay_live + y_ML")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(585, 306, "where y_ML = f(Speed, Distance, RushHour, TrainType)")

    # Why HistGradientBoosting?
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(text_primary)
    c.drawString(570, 264, "Why HistGradientBoostingRegressor?")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    reasons = [
        "Native Binning: Handles continuous spatial & speed features without lag.",
        "Non-Linear Dynamics: Captures how delays compound during rush hours.",
        "Sub-5ms Inference: Essential for real-time live dashboard sync.",
        "Outlier Immunity: Prevents single GPS glitches from skewing predictions.",
        "Missing Data Tolerance: Seamlessly processes partial station reports.",
    ]
    ry = 244
    for r in reasons:
        draw_bullet(570, ry, accent_emerald)
        c.drawString(580, ry, r)
        ry -= 20

    c.setFillColor(HexColor("#1F2937"))
    c.roundRect(570, 72, 320, 34, 4, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(accent_emerald)
    c.drawString(585, 84, "Verified by automated test suite (59 test cases passing)")

    c.showPage()

    # =========================================================================
    # SLIDE 6: Frontend Experience & UI Innovation
    # =========================================================================
    draw_slide_base(
        "Frontend Innovation",
        "60/40 Operational Split Transportation UI",
        "Engineered for cognitive ease, rapid triage, and high-density telemetry scanning.",
        6
    )

    cw = 266
    ch = 350
    cy = 58

    # Column 1: Map
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, cy, cw, ch, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(68, cy + ch - 26, "60% Map Canvas")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(68, cy + ch - 42, "HARDWARE ACCELERATED LEAFLET")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    ui_b1 = [
        "Full-canvas route polyline",
        "Pulsing SVG Locomotive marker",
        "  displaying real-time heading & speed",
        "Waypoint halos distinguishing passed",
        "  stops from upcoming halts",
        "Dynamic bounding box centering",
        "  on train selection",
        "High-contrast OpenStreetMap tiles",
        "  (Zero third-party API keys required)",
    ]
    uy = cy + ch - 66
    for b in ui_b1:
        if b.startswith("  "):
            c.drawString(78, uy, b)
        else:
            draw_bullet(68, uy, accent_blue)
            c.drawString(78, uy, b)
        uy -= 19

    c.setFillColor(card_inner)
    c.roundRect(65, cy + 16, cw - 30, 48, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(75, cy + 46, "Visual Focus:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(75, cy + 32, "Instant corridor orientation without clutter.")

    # Column 2: Selected Train Panel
    c.setFillColor(card_bg)
    c.roundRect(346, cy, cw, ch, 8, stroke=1, fill=1)
    c.setFillColor(accent_emerald)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(364, cy + ch - 26, "40% Telemetry Panel")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(364, cy + ch - 42, "SELECTED TRAIN INTELLIGENCE")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    ui_b2 = [
        "Selected Train telemetry card",
        "Color-coded delay pill:",
        "  (Green <=5m, Yellow <=20m, Red >20m)",
        "Model Delay vs. Live Delay comparison",
        "Next station distance & ETA countdown",
        "Origin-Destination Corridor badge",
        "Space-efficient vertical Timeline:",
        "  - Auto-scrolls to active train halt",
        "  - 'Jump to Live' 1-click focus",
    ]
    uy = cy + ch - 66
    for b in ui_b2:
        if b.startswith("  "):
            c.drawString(374, uy, b)
        else:
            draw_bullet(364, uy, accent_emerald)
            c.drawString(374, uy, b)
        uy -= 19

    c.setFillColor(card_inner)
    c.roundRect(361, cy + 16, cw - 30, 48, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(371, cy + 46, "Space Efficiency:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(371, cy + 32, "Bounded container avoids page bloat.")

    # Column 3: Multi-Train Operations
    c.setFillColor(card_bg)
    c.roundRect(642, cy, cw, ch, 8, stroke=1, fill=1)
    c.setFillColor(accent_amber)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(660, cy + ch - 26, "Multi-Train Operations")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(660, cy + ch - 42, "TRIAGE, SEARCH & CONTROLS")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    ui_b3 = [
        "Smart Autocomplete Search bar:",
        "  Debounced across 8,490+ trains",
        "4 Real-time KPI Metric cards:",
        "  Clickable filtering (All / On Time / Delayed)",
        "High-Severity Delay Alerts Banner:",
        "  Instant notification of 15m+ disruptions",
        "Station Operations Table:",
        "  In-table filter, column sort, pagination",
        "Non-blocking 30s live telemetry sync",
    ]
    uy = cy + ch - 66
    for b in ui_b3:
        if b.startswith("  "):
            c.drawString(670, uy, b)
        else:
            draw_bullet(642 + 18, uy, accent_amber)
            c.drawString(670, uy, b)
        uy -= 19

    c.setFillColor(card_inner)
    c.roundRect(657, cy + 16, cw - 30, 48, 6, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_primary)
    c.drawString(667, cy + 46, "Theme Engine:")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawString(667, cy + 32, "Modern Light & High-Tech Dark modes.")

    c.showPage()

    # =========================================================================
    # SLIDE 7: Technical Resilience & Edge-Case Engineering
    # =========================================================================
    draw_slide_base(
        "Technical Resilience",
        "Engineered for High Concurrency & Fault Tolerance",
        "Resilient architectural patterns ensuring uninterrupted operation under real-world network constraints.",
        7
    )

    gw = 415
    gh = 168

    # Card 1: 429 Failover
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, 240, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(70, 240 + gh - 28, "Graceful HTTP 429 Rate-Limit Fallback")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    r_bullets1 = [
        "Live railway APIs frequently impose strict query quotas.",
        "YatriRail detects HTTP 429 status codes automatically.",
        "Instantly fails over to the bundled 8,490-train offline dataset.",
        "End-users experience zero application crashes or blank states.",
    ]
    ry = 240 + gh - 54
    for b in r_bullets1:
        draw_bullet(70, ry, accent_blue)
        c.drawString(80, ry, b)
        ry -= 24

    # Card 2: Coordinate Interpolation
    c.setFillColor(card_bg)
    c.roundRect(495, 240, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_emerald)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(515, 240 + gh - 28, "Mathematical Coordinate Interpolation")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    r_bullets2 = [
        "Many smaller rural stations lack explicit GPS coordinate records.",
        "Algorithm finds nearest upstream and downstream known junctions.",
        "Computes distance-weighted latitude/longitude coordinates.",
        "Guarantees contiguous polyline route mapping without missing stops.",
    ]
    ry = 240 + gh - 54
    for b in r_bullets2:
        draw_bullet(515, ry, accent_emerald)
        c.drawString(525, ry, b)
        ry -= 24

    # Card 3: Credential Isolation
    c.setFillColor(card_bg)
    c.roundRect(50, 58, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_indigo)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(70, 58 + gh - 28, "Zero-Leak Credential Isolation")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    r_bullets3 = [
        "API tokens and Bearer credentials remain strictly on the FastAPI server.",
        "The React client communicates exclusively with the local/cloud proxy.",
        "Restrictive CORS headers block unauthorized cross-site requests.",
        "Telemetry logs redact sensitive headers before JSONL persistence.",
    ]
    ry = 58 + gh - 54
    for b in r_bullets3:
        draw_bullet(70, ry, accent_indigo)
        c.drawString(80, ry, b)
        ry -= 24

    # Card 4: Automated Testing
    c.setFillColor(card_bg)
    c.roundRect(495, 58, gw, gh, 8, stroke=1, fill=1)
    c.setFillColor(accent_amber)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(515, 58 + gh - 28, "Automated Test Verification (59 Tests)")
    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    r_bullets4 = [
        "59 Comprehensive automated unit and integration tests.",
        "Covers normalization, 12-feature vectors, ML inference, & rate limits.",
        "Full test execution time: < 2.0 seconds.",
        "Validates frontend production build output via npm run build.",
    ]
    ry = 58 + gh - 54
    for b in r_bullets4:
        draw_bullet(515, ry, accent_amber)
        c.drawString(525, ry, b)
        ry -= 24

    c.showPage()

    # =========================================================================
    # SLIDE 8: Key Impact & Hackathon Achievements
    # =========================================================================
    draw_slide_base(
        "Key Impact & Milestones",
        "Measurable Hackathon Achievements",
        "From concept to a production-grade, deployed intelligence platform in record time.",
        8
    )

    # 4 Metric Cards
    mw = 200
    mh = 130
    my = 278

    # Metric 1
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, my, mw, mh, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(accent_blue)
    c.drawString(68, my + mh - 42, "8,490+")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(text_primary)
    c.drawString(68, my + mh - 70, "Trains Indexed")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(68, my + 26, "National coverage with")
    c.drawString(68, my + 14, "instant autocomplete.")

    # Metric 2
    c.setFillColor(card_bg)
    c.roundRect(270, my, mw, mh, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(accent_emerald)
    c.drawString(288, my + mh - 42, "< 5ms")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(text_primary)
    c.drawString(288, my + mh - 70, "ML Inference Latency")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(288, my + 26, "Sub-second turnaround")
    c.drawString(288, my + 14, "for real-time updates.")

    # Metric 3
    c.setFillColor(card_bg)
    c.roundRect(490, my, mw, mh, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(accent_amber)
    c.drawString(508, my + mh - 42, "59 / 59")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(text_primary)
    c.drawString(508, my + mh - 70, "Tests Passing")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(508, my + 26, "100% automated test")
    c.drawString(508, my + 14, "pass rate on backend.")

    # Metric 4
    c.setFillColor(card_bg)
    c.roundRect(710, my, mw, mh, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(accent_indigo)
    c.drawString(728, my + mh - 42, "100%")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(text_primary)
    c.drawString(728, my + mh - 70, "Cloud Deployed")
    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    c.drawString(728, my + 26, "Render Backend +")
    c.drawString(728, my + 14, "Vercel Edge Frontend.")

    # Bottom Qualitative Box
    c.setFillColor(card_bg)
    c.roundRect(50, 58, 860, 202, 8, stroke=1, fill=1)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(accent_blue)
    c.drawString(70, 232, "What We Accomplished During the Hackathon:")

    achievements = [
        "1. Built and production-tuned the 12-feature HistGradientBoosting delay prediction pipeline.",
        "2. Designed an end-to-end 60/40 operational dashboard using React 19, Tailwind 4, and Leaflet.",
        "3. Engineered real-time network KPI cards, automatic delay alerts, and interactive route mapping.",
        "4. Solved upstream API rate-limiting via seamless in-memory indexing of 8,490 train schedules.",
        "5. Automated deployment workflows for Render Blueprint and Vercel Edge hosting.",
        "6. Authored extensive production documentation, API schemas, and an open-source MIT repository.",
    ]
    c.setFont("Helvetica", 9)
    c.setFillColor(text_primary)
    ay = 208
    for a in achievements:
        c.drawString(70, ay, a)
        ay -= 22

    c.showPage()

    # =========================================================================
    # SLIDE 9: What is Next? — Future Roadmap
    # =========================================================================
    draw_slide_base(
        "What is Next?",
        "Future Roadmap: Scaling YatriRail Nationally",
        "Expanding from predictive passenger tracking to a comprehensive transit intelligence network.",
        9
    )

    rw = 266
    rh = 350
    ry = 58

    # Phase 1: Near-Term
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, ry, rw, rh, 8, stroke=1, fill=1)
    c.setFillColor(accent_blue)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(68, ry + rh - 26, "Phase 1: Real-Time Feeds")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(68, ry + rh - 42, "MONTHS 1 - 3")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    road_b1 = [
        "WebSocket Streaming:",
        "  Sub-second live locomotive push",
        "  updates replacing 30s polling.",
        "Doppler Weather Radar:",
        "  Incorporate monsoon rain and dense",
        "  winter fog intensity into ETA model.",
        "Mobile PWA Companion:",
        "  Offline-first mobile web app with",
        "  push notifications for station halts.",
        "Multi-Lingual Support:",
        "  Dashboard localization in 10+ languages.",
    ]
    r_y = ry + rh - 66
    for b in road_b1:
        if b.startswith("  "):
            c.drawString(78, r_y, b)
        else:
            draw_bullet(68, r_y, accent_blue)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(text_primary)
            c.drawString(78, r_y, b)
            c.setFont("Helvetica", 8)
            c.setFillColor(text_secondary)
        r_y -= 19

    # Phase 2: Medium-Term
    c.setFillColor(card_bg)
    c.roundRect(346, ry, rw, rh, 8, stroke=1, fill=1)
    c.setFillColor(accent_emerald)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(364, ry + rh - 26, "Phase 2: Network Effects")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(364, ry + rh - 42, "MONTHS 3 - 6")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    road_b2 = [
        "Secondary Delay Cascades:",
        "  Graph neural networks modeling rake",
        "  turnarounds & track ripple effects.",
        "Passenger Crowd Telemetry:",
        "  Zero-permission Bluetooth beacon &",
        "  onboard GPS ground-truth verification.",
        "Station Platform Allocation:",
        "  Predictive platform arrival estimates",
        "  preventing platform bottlenecking.",
        "Automated Delay Explanations:",
        "  Natural language root cause summaries.",
    ]
    r_y = ry + rh - 66
    for b in road_b2:
        if b.startswith("  "):
            c.drawString(374, r_y, b)
        else:
            draw_bullet(364, r_y, accent_emerald)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(text_primary)
            c.drawString(374, r_y, b)
            c.setFont("Helvetica", 8)
            c.setFillColor(text_secondary)
        r_y -= 19

    # Phase 3: Long-Term
    c.setFillColor(card_bg)
    c.roundRect(642, ry, rw, rh, 8, stroke=1, fill=1)
    c.setFillColor(accent_indigo)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(660, ry + rh - 26, "Phase 3: Controller Suite")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(text_muted)
    c.drawString(660, ry + rh - 42, "MONTHS 6+")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    road_b3 = [
        "Dispatcher Decision Support:",
        "  Assisting section controllers with",
        "  track precedence simulations.",
        "Smart Junction Precedence:",
        "  Reinforcement learning algorithms for",
        "  prioritizing fast trains at chokepoints.",
        "Energy Optimization:",
        "  Speed curve recommendations to reduce",
        "  traction power waste during idle halts.",
        "Nationwide Fleet Analytics:",
        "  Zone-by-zone operational scorecards.",
    ]
    r_y = ry + rh - 66
    for b in road_b3:
        if b.startswith("  "):
            c.drawString(670, r_y, b)
        else:
            draw_bullet(660, r_y, accent_indigo)
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(text_primary)
            c.drawString(670, r_y, b)
            c.setFont("Helvetica", 8)
            c.setFillColor(text_secondary)
        r_y -= 19

    c.showPage()

    # =========================================================================
    # SLIDE 10: Conclusion, Team & Q&A
    # =========================================================================
    draw_slide_base(
        "Conclusion & Team",
        "Predictable Railway Travel for Every Commuter",
        "YatriRail brings transparency, predictive precision, and peace of mind to Indian Railways.",
        10
    )

    # Left: Team Card
    c.setFillColor(card_bg)
    c.setStrokeColor(card_border)
    c.roundRect(50, 58, 430, 350, 8, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(accent_blue)
    c.drawString(68, 382, "The Hackathon Team")

    team = [
        ("Anuj Maurya", "Frontend / Map & Dashboard", "anujmaurya0104@gmail.com", "github.com/anuj-maurya-01"),
        ("Archita Kesharwani", "Backend / Real-Time Engine", "architakesharwani@gmail.com", "FastAPI, API Gateway & Tests"),
        ("Aru Shubham Singh", "ML / ETA Prediction", "ashubham701080@gmail.com", "HistGradientBoosting, 12 Features"),
        ("Shlok Bhardwaj", "Data Analytics & Research", "shlokbhardwaj80@gmail.com", "Delay Analytics & KPI Modeling"),
    ]

    ty = 348
    for name, role, email, note in team:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(text_primary)
        c.drawString(68, ty, name)
        
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(accent_blue)
        c.drawString(68, ty - 14, role)
        
        c.setFont("Helvetica", 8)
        c.setFillColor(text_secondary)
        c.drawString(68, ty - 26, f"Email: {email}")
        c.setFillColor(text_muted)
        c.drawString(68, ty - 38, f"Role: {note}")
        
        ty -= 66

    # Right: Project Summary & Q&A Callout
    c.setFillColor(card_bg)
    c.roundRect(500, 58, 410, 350, 8, stroke=1, fill=1)

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(accent_emerald)
    c.drawString(520, 382, "Repository & Open Source")

    c.setFont("Helvetica", 9)
    c.setFillColor(text_secondary)
    c.drawString(520, 352, "Public GitHub Repository:")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(accent_blue)
    c.drawString(520, 336, "https://github.com/anuj-maurya-01/YatriRail")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_secondary)
    r_bullets = [
        "License: MIT Open Source License",
        "Live Backend: Render Cloud Service (FastAPI)",
        "Live Frontend: Vercel Cloud Edge (React 19)",
        "Test Coverage: 59 Automated Tests Passing",
    ]
    ry = 312
    for b in r_bullets:
        draw_bullet(520, ry, accent_emerald)
        c.drawString(530, ry, b)
        ry -= 18

    # Q&A Box
    c.setFillColor(card_inner)
    c.roundRect(520, 78, 370, 130, 6, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(text_primary)
    c.drawCentredString(705, 172, "Thank You!")

    c.setFont("Helvetica", 10)
    c.setFillColor(accent_emerald)
    c.drawCentredString(705, 148, "We are excited to answer your questions.")

    c.setFont("Helvetica", 8)
    c.setFillColor(text_muted)
    c.drawCentredString(705, 122, "YatriRail: Live Indian Railway Intelligence")
    c.drawCentredString(705, 106, "Making train travel predictable and stress-free.")

    c.showPage()

    # Save PDF
    c.save()
    print(f"Presentation deck successfully generated at: {output_path}")

if __name__ == "__main__":
    create_presentation_deck()
