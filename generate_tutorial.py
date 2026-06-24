"""
generate_tutorial.py
Run with: python generate_tutorial.py
Outputs:  TUTORIAL.pdf in the project root
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    PageBreak, Table, TableStyle, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import date

PAGE_W, PAGE_H = letter
MARGIN = inch
TODAY = date.today().strftime("%B %d, %Y")

# ---------------------------------------------------------------------------
# Page numbering via canvas callback
# ---------------------------------------------------------------------------

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(num_pages)
            super().showPage()
        super().save()

    def _draw_page_number(self, page_count):
        page_num = self._saved_page_states.index(dict(self.__dict__)) + 1 if hasattr(self, '_pageNumber') else 1
        # Find position of current page
        for i, s in enumerate(self._saved_page_states):
            if s.get('_pageNumber') == self._pageNumber:
                page_num = i + 1
                break
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.grey)
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_W - MARGIN, 0.5 * inch, text)
        self.drawString(MARGIN, 0.5 * inch, "TrainTime Web API — Developer Tutorial")


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["title"] = ParagraphStyle(
        "TitleStyle",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    styles["subtitle"] = ParagraphStyle(
        "SubtitleStyle",
        fontName="Helvetica",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#444444"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles["date"] = ParagraphStyle(
        "DateStyle",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    styles["h1"] = ParagraphStyle(
        "H1Style",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=24,
        spaceAfter=10,
    )
    styles["h2"] = ParagraphStyle(
        "H2Style",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#2c2c54"),
        spaceBefore=16,
        spaceAfter=6,
    )
    styles["h3"] = ParagraphStyle(
        "H3Style",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#393939"),
        spaceBefore=10,
        spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "BodyStyle",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#222222"),
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    styles["bullet"] = ParagraphStyle(
        "BulletStyle",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222"),
        leftIndent=18,
        spaceAfter=4,
        bulletIndent=6,
    )
    styles["toc_entry"] = ParagraphStyle(
        "TocEntry",
        fontName="Helvetica",
        fontSize=11,
        leading=18,
        textColor=colors.HexColor("#222222"),
        leftIndent=0,
        spaceAfter=2,
    )
    styles["toc_sub"] = ParagraphStyle(
        "TocSub",
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#555555"),
        leftIndent=20,
        spaceAfter=1,
    )
    styles["warning"] = ParagraphStyle(
        "WarningStyle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#8b0000"),
        spaceAfter=6,
    )
    styles["checklist"] = ParagraphStyle(
        "ChecklistStyle",
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        leftIndent=10,
        spaceAfter=3,
    )
    return styles


# ---------------------------------------------------------------------------
# Helper to render a code block as a Table with grey background
# ---------------------------------------------------------------------------

def code_block(code_text, styles_map, max_lines=42):
    """Return a list of flowables for a code block, split at page boundaries."""
    code_style = ParagraphStyle(
        "CodeInner",
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1a1a1a"),
        leftIndent=0,
    )
    tbl_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f2f2")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])

    lines = code_text.split("\n")
    chunks = [lines[i:i + max_lines] for i in range(0, len(lines), max_lines)]
    result = []
    for i, chunk in enumerate(chunks):
        pre = Preformatted("\n".join(chunk), code_style)
        tbl = Table([[pre]], colWidths=[PAGE_W - 2 * MARGIN])
        tbl.setStyle(tbl_style)
        result.append(tbl)
        if i < len(chunks) - 1:
            result.append(Spacer(1, 2))
    return result


def sp(n=1):
    return Spacer(1, n * 6)


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd"), spaceAfter=4, spaceBefore=4)


# ---------------------------------------------------------------------------
# Content builders — one function per section
# ---------------------------------------------------------------------------

def title_page(S):
    return [
        Spacer(1, 2 * inch),
        Paragraph("TrainTime", S["title"]),
        Paragraph("Web API — Developer Tutorial", S["subtitle"]),
        Spacer(1, 0.2 * inch),
        hr(),
        Spacer(1, 0.2 * inch),
        Paragraph(
            "A complete guide to rebuilding the FastAPI backend from scratch, "
            "understanding every design decision, and deploying to Vercel.",
            S["subtitle"],
        ),
        Spacer(1, 0.5 * inch),
        Paragraph(TODAY, S["date"]),
        PageBreak(),
    ]


def toc_page(S):
    items = [
        Paragraph("Table of Contents", S["h1"]),
        sp(2),
        Paragraph("Section 1   What We're Building and Why", S["toc_entry"]),
        Paragraph("Section 2   System Design", S["toc_entry"]),
        Paragraph("Section 3   Full Technology Stack", S["toc_entry"]),
        Paragraph("Section 4   Prerequisites and Setup From Zero", S["toc_entry"]),
        Paragraph("    4a  Python environment", S["toc_sub"]),
        Paragraph("    4b  Vercel CLI", S["toc_sub"]),
        Paragraph("    4c  Project structure", S["toc_sub"]),
        Paragraph("Section 5   API Key Setup", S["toc_entry"]),
        Paragraph("Section 6   Static Data Files", S["toc_entry"]),
        Paragraph("    6a  utils/stations.json", S["toc_sub"]),
        Paragraph("    6b  utils/bus_stops.json", S["toc_sub"]),
        Paragraph("Section 7   Backend — File by File", S["toc_entry"]),
        Paragraph("    utils/haversine.py", S["toc_sub"]),
        Paragraph("    utils/gtfs.py", S["toc_sub"]),
        Paragraph("    utils/bus.py", S["toc_sub"]),
        Paragraph("    api/trains.py", S["toc_sub"]),
        Paragraph("    api/buses.py", S["toc_sub"]),
        Paragraph("    api/location.py", S["toc_sub"]),
        Paragraph("    dev_server.py", S["toc_sub"]),
        Paragraph("Section 8   Deploy to Vercel", S["toc_entry"]),
        Paragraph("Section 9   Happy Path — End to End", S["toc_entry"]),
        Paragraph("Section 10  Known Bugs and Fixes", S["toc_entry"]),
        Paragraph("Section 11  Testing Checklist", S["toc_entry"]),
        PageBreak(),
    ]
    return items


def section1(S):
    return [
        Paragraph("Section 1: What We're Building and Why", S["h1"]),
        hr(),
        Paragraph(
            "TrainTime is a lightweight JSON API that surfaces real-time NYC transit departure "
            "data — subways and buses — over plain HTTP. Its job is simple: given a location, "
            "return the next few trains and buses leaving from the nearest station or stop. "
            "Everything is read-only and stateless. There is no database, no user accounts, "
            "no authentication on the client side. You make a GET request and get departure "
            "times back as JSON.",
            S["body"],
        ),
        Paragraph(
            "The problem it solves is that MTA's own real-time feeds are not consumer-friendly. "
            "The subway feed is a binary protobuf format defined by the GTFS-RT spec. The bus "
            "feed uses SIRI, a verbose XML-derived JSON format from an EU transit standard. "
            "Neither is something you want to parse on a microcontroller or in a browser widget. "
            "This API absorbs that complexity and emits clean, minimal JSON: station name, line, "
            "and minutes until departure. That's it.",
            S["body"],
        ),
        Paragraph(
            "The choice of FastAPI on Vercel is deliberate. FastAPI handles async I/O natively, "
            "which matters because every request fans out to one or more upstream MTA endpoints. "
            "Vercel turns each api/*.py file into an isolated serverless function — no server to "
            "provision, no Docker image, no port management. The free tier is sufficient for "
            "personal use. Cold starts add a few hundred milliseconds on first request, but "
            "subsequent requests are fast because the MTA feeds are the bottleneck anyway.",
            S["body"],
        ),
        Paragraph(
            "The intended consumer in this project is an ESP32 microcontroller displaying "
            "departure times on a small screen, but the API is generic. Any HTTP client — "
            "a browser, a phone app, a curl command, a Home Assistant integration — can call it. "
            "The ESP32 also uses the /api/location endpoint to determine its own coordinates "
            "from nearby WiFi networks before polling the transit endpoints.",
            S["body"],
        ),
        PageBreak(),
    ]


def section2(S):
    trains_flow = """\
[HTTP GET /api/trains?lat=40.7484&lon=-73.9857]
              |
              v
     [api/trains.py receives request]
              |
              | reads lat/lon from query params
              v
     [utils/haversine.py: find_nearest_station()]
       iterates all 496 stations in stations.json
       computes haversine distance to each
       returns closest station dict
              |
              | {id: "R20", name: "34 St-Herald Sq", lines: ["B","D","F","M","N","Q","R","W"], ...}
              v
     [utils/gtfs.py: fetch_departures(station_id, lines)]
       deduplicates feed URLs (B/D/F/M share one feed, N/Q/R/W share another)
       for each unique feed URL:
              |
              | HTTP GET + x-api-key header
              v
     [MTA GTFS-RT endpoint (binary protobuf)]
       e.g. https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm
              |
              | parse FeedMessage protobuf
              | iterate TripUpdate entities
              | for each StopTimeUpdate: check stop_id.startswith("R20")
              | "R20N" -> northbound, "R20S" -> southbound
              | convert Unix timestamp to minutes from now
              v
     [sort northbound asc, sort southbound asc, take top 3 each]
              |
              v
     [return JSON to caller]

Response shape:
{
  "station": "34 St-Herald Sq",
  "uptown":   [{"line": "B", "minutes": 2}, {"line": "F", "minutes": 4}, {"line": "Q", "minutes": 7}],
  "downtown": [{"line": "N", "minutes": 1}, {"line": "R", "minutes": 3}, {"line": "D", "minutes": 6}],
  "north_label": "Uptown & The Bronx",
  "south_label": "Downtown & Brooklyn"
}"""

    buses_flow = """\
[HTTP GET /api/buses?lat=40.7484&lon=-73.9857]
              |
              v
     [api/buses.py receives request]
              |
              | reads lat/lon from query params
              v
     [utils/haversine.py: find_nearest_station()]
       iterates all 12,581 stops in bus_stops.json
       returns closest stop dict
              |
              | {id: "MTA_305423", name: "34 ST/7 AV", lat: 40.749, lon: -73.990, routes: [...]}
              v
     [utils/bus.py: fetch_bus_departures(stop_id)]
              |
              | HTTP GET + ?key=MTA_BUS_API_KEY&MonitoringRef=MTA_305423
              v
     [MTA Bustime SIRI endpoint (JSON)]
       https://bustime.mta.info/api/siri/stop-monitoring.json
              |
              | parse Siri.ServiceDelivery.StopMonitoringDelivery[0].MonitoredStopVisit
              | for each visit: extract route, DirectionRef, ExpectedArrivalTime
              | DirectionRef "0" -> inbound, "1" -> outbound
              | parse ISO 8601 timestamp, convert to minutes from now
              v
     [sort inbound asc, sort outbound asc, take top 3 each]
              |
              v
     [return JSON to caller]

Response shape:
{
  "stop":    "34 ST/7 AV",
  "inbound":  [{"route": "M34A+", "minutes": 3}, {"route": "M34A+", "minutes": 8}],
  "outbound": [{"route": "M34A+", "minutes": 1}, {"route": "M34A+", "minutes": 6}]
}"""

    location_flow = """\
[HTTP POST /api/location]
  Body: {"wifiAccessPoints": [{"macAddress": "aa:bb:cc:dd:ee:ff", "signalStrength": -65}, ...]}
              |
              v
     [api/location.py validates request body via Pydantic]
              |
              | HTTP POST + ?key=GOOGLE_GEOLOCATION_API_KEY
              v
     [Google Geolocation API]
       https://www.googleapis.com/geolocation/v1/geolocate
       matches MAC addresses against Google's WiFi database
              |
              | {"location": {"lat": 40.7484, "lng": -73.9857}, "accuracy": 15.0}
              v
     [extract lat/lng, rename lng -> lon]
              |
              v
     {"lat": 40.7484, "lon": -73.9857}"""

    ip_fallback = """\
If no lat/lon is provided to /api/trains or /api/buses:

1. Read the X-Forwarded-For header (Vercel sets this)
2. Take the first IP address from the comma-separated list
3. GET http://ip-api.com/json/{ip}
4. If status == "success": use returned lat/lon
5. If localhost or any failure: fall back to NYC_COORDS (40.7128, -74.0060)"""

    return [
        Paragraph("Section 2: System Design", S["h1"]),
        hr(),
        Paragraph("2.1  Trains Request Flow", S["h2"]),
        *code_block(trains_flow, S),
        sp(2),
        Paragraph("2.2  Buses Request Flow", S["h2"]),
        *code_block(buses_flow, S),
        sp(2),
        Paragraph("2.3  Location Request Flow", S["h2"]),
        *code_block(location_flow, S),
        sp(2),
        Paragraph("2.4  IP Geolocation Fallback", S["h2"]),
        Paragraph(
            "When no lat/lon is supplied, both /api/trains and /api/buses fall back to "
            "geolocating the caller's IP address using the free ip-api.com service.",
            S["body"],
        ),
        *code_block(ip_fallback, S),
        PageBreak(),
    ]


def section3(S):
    return [
        Paragraph("Section 3: Full Technology Stack", S["h1"]),
        hr(),

        Paragraph("FastAPI (fastapi==0.137.1)", S["h2"]),
        Paragraph(
            "The web framework. FastAPI is chosen because it is async-native (critical for "
            "making multiple upstream HTTP calls without blocking), auto-generates OpenAPI docs "
            "at /docs, and uses Pydantic for request validation — which lets us define the "
            "/api/location request body as a typed Python class and get free validation. "
            "Every api/*.py file instantiates its own FastAPI() app instance. Vercel treats "
            "each file as an isolated function, so there is no shared process between them.",
            S["body"],
        ),

        Paragraph("Starlette (starlette==1.3.1)", S["h2"]),
        Paragraph(
            "FastAPI is built on top of Starlette, which provides the ASGI foundation, routing, "
            "and the Request object. You do not interact with Starlette directly, but it is why "
            "app.include_router() works in dev_server.py — FastAPI exposes the underlying "
            "Starlette router.",
            S["body"],
        ),

        Paragraph("httpx (httpx==0.28.1)", S["h2"]),
        Paragraph(
            "The async HTTP client used for all outbound requests: MTA GTFS feeds, MTA Bustime, "
            "ip-api.com, and Google Geolocation. httpx is preferred over aiohttp because it has "
            "a nearly identical API to the synchronous requests library, supports both sync and "
            "async, and integrates cleanly with FastAPI's async handlers. All calls use "
            "async with httpx.AsyncClient() as client: to open one connection per request "
            "handler and close it cleanly on exit.",
            S["body"],
        ),

        Paragraph("gtfs-realtime-bindings (gtfs-realtime-bindings==2.0.0)", S["h2"]),
        Paragraph(
            "MTA's subway real-time feed is binary protobuf data, not JSON. This package "
            "provides the Python protobuf bindings for the GTFS-RT specification — specifically "
            "gtfs_realtime_pb2.FeedMessage, which is what you call .ParseFromString() on. "
            "Without this package you would have to decode raw protobuf bytes manually.",
            S["body"],
        ),

        Paragraph("protobuf (protobuf==7.35.1)", S["h2"]),
        Paragraph(
            "The underlying Google protobuf runtime that gtfs-realtime-bindings depends on. "
            "You do not import it directly, but it must be present for protobuf parsing to work.",
            S["body"],
        ),

        Paragraph("Pydantic (pydantic==2.13.4)", S["h2"]),
        Paragraph(
            "Request/response validation. Used explicitly in api/location.py to define "
            "WiFiAccessPoint and LocationRequest models. FastAPI also uses Pydantic internally "
            "for query parameter validation on all endpoints. The .model_dump() call on the "
            "request body serializes the Pydantic model back to a plain dict for forwarding "
            "to Google's API.",
            S["body"],
        ),

        Paragraph("python-dotenv (python-dotenv==1.2.2)", S["h2"]),
        Paragraph(
            "Loads the .env file into environment variables during local development. "
            "dev_server.py calls load_dotenv() before importing the api modules, so the "
            "MTA and Google API keys are available to os.environ.get() calls in the "
            "handler code. On Vercel, environment variables are set in the dashboard and "
            "injected at runtime — python-dotenv is not used in production.",
            S["body"],
        ),

        Paragraph("uvicorn (uvicorn==0.49.0)", S["h2"]),
        Paragraph(
            "The ASGI server for local development. Run as: "
            "uvicorn dev_server:app --reload --port 8000. "
            "Vercel does not use uvicorn in production — it invokes the FastAPI ASGI app "
            "directly through its own runtime. uvicorn is a dev-only dependency but is "
            "included in requirements.txt because Vercel installs all deps listed there.",
            S["body"],
        ),

        Paragraph("Vercel (@vercel/python runtime)", S["h2"]),
        Paragraph(
            "The deployment platform. vercel.json configures the build: each api/*.py file "
            "is compiled independently by the @vercel/python builder and served as a separate "
            "serverless function. The routes block maps /api/(.*) to api/$1.py, so "
            "/api/trains routes to api/trains.py, /api/buses to api/buses.py, and so on. "
            "There is no shared state between functions — STATIONS and BUS_STOPS are loaded "
            "from JSON at cold-start time inside each function.",
            S["body"],
        ),

        Paragraph("ip-api.com (external, no package)", S["h2"]),
        Paragraph(
            "A free IP geolocation service. Called via httpx when no lat/lon is provided. "
            "Returns JSON with status, lat, lon fields. The free tier has rate limits but "
            "is sufficient for personal use. No API key required. Used as a convenience "
            "fallback — the primary location path for the ESP32 is the /api/location "
            "WiFi-based endpoint.",
            S["body"],
        ),

        PageBreak(),
    ]


def section4(S):
    project_structure = """\
train-time/
|-- api/                      # Serverless function handlers (one per endpoint)
|   |-- trains.py             # GET /api/trains
|   |-- buses.py              # GET /api/buses
|   +-- location.py           # POST /api/location
|
|-- utils/                    # Shared utilities (imported by api/ files)
|   |-- haversine.py          # Great-circle distance + nearest-station lookup
|   |-- gtfs.py               # MTA GTFS-RT protobuf feed fetcher/parser
|   |-- bus.py                # MTA Bustime SIRI API client
|   |-- stations.json         # Pre-built: 496 NYC subway stations (lat/lon, lines, IDs)
|   +-- bus_stops.json        # Pre-built: 12,581 NYC bus stops (lat/lon, routes, IDs)
|
|-- gtfs_static/              # GTFS static schedule data (reference only, not used at runtime)
|   |-- stops.txt             # Station definitions with N/S stop IDs
|   |-- routes.txt            # 29 NYC subway routes
|   +-- ...                   # trips, stop_times, shapes, calendar, etc.
|
|-- dev_server.py             # Local dev: mounts all three apps onto one uvicorn instance
|-- vercel.json               # Vercel build + routing config
|-- requirements.txt          # Python dependencies
|-- .env                      # Local API keys (never commit this)
|-- convert_stations.py       # One-time: converts stations.csv -> utils/stations.json
|-- generate_bus_stops.py     # One-time: crawls MTA API to build utils/bus_stops.json
+-- stations.csv              # Raw MTA station data (input to convert_stations.py)"""

    python_setup = """\
# macOS: install Python 3.11+
brew install python

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\\Scripts\\activate       # Windows

# Install all dependencies
pip install -r requirements.txt"""

    vercel_setup = """\
# Install the Vercel CLI globally
npm install -g vercel

# Log in (opens browser)
vercel login"""

    run_local = """\
# Start the local dev server (all three endpoints on port 8000)
uvicorn dev_server:app --reload --port 8000

# Verify each endpoint responds
curl http://localhost:8000/api/trains
curl http://localhost:8000/api/buses
curl -X POST http://localhost:8000/api/location \\
  -H "Content-Type: application/json" \\
  -d '{"wifiAccessPoints": []}'"""

    return [
        Paragraph("Section 4: Prerequisites and Setup From Zero", S["h1"]),
        hr(),

        Paragraph("4a. Python Environment", S["h2"]),
        Paragraph(
            "You need Python 3.11 or later. The union type syntax (str | None) used throughout "
            "the codebase requires Python 3.10+, and several dependencies pin to 3.11+.",
            S["body"],
        ),
        *code_block(python_setup, S),

        Paragraph("4b. Vercel CLI", S["h2"]),
        Paragraph(
            "Vercel's CLI handles deployment. You need Node.js installed for npm. "
            "After login, the CLI stores a token locally — subsequent deploys do not require "
            "re-authentication.",
            S["body"],
        ),
        *code_block(vercel_setup, S),

        Paragraph("4c. Project Structure", S["h2"]),
        Paragraph(
            "Before writing any code, this is what the complete project looks like. "
            "Understanding the layout matters because Vercel's routing config in vercel.json "
            "depends on files being in the api/ directory specifically.",
            S["body"],
        ),
        *code_block(project_structure, S),
        sp(2),
        Paragraph("Running Locally", S["h2"]),
        Paragraph(
            "dev_server.py exists because Vercel's model (one file = one function) does not "
            "translate directly to a local uvicorn process. The dev server imports all three "
            "FastAPI app instances and mounts their routers onto a single app, giving you all "
            "three endpoints on one port. Vercel is not involved locally at all.",
            S["body"],
        ),
        *code_block(run_local, S),
        PageBreak(),
    ]


def section5(S):
    env_file = """\
# .env  (local development only — never commit this file)
MTA_BUS_API_KEY=your_mta_key_here
GOOGLE_GEOLOCATION_API_KEY=your_google_key_here"""

    vercel_env = """\
# Add each variable to your Vercel project (run once per variable)
vercel env add MTA_BUS_API_KEY
vercel env add GOOGLE_GEOLOCATION_API_KEY

# Vercel will prompt you to paste the value and choose environments
# (Production, Preview, Development)"""

    return [
        Paragraph("Section 5: API Key Setup", S["h1"]),
        hr(),
        Paragraph(
            "The project requires two API keys. Both are read via os.environ.get() at "
            "request time, never hardcoded. Locally they come from the .env file loaded "
            "by python-dotenv. On Vercel they are set in the project dashboard or via CLI.",
            S["body"],
        ),

        Paragraph("MTA_BUS_API_KEY", S["h2"]),
        Paragraph(
            "Used in two places. In utils/gtfs.py it is sent as the x-api-key request "
            "header when fetching GTFS-RT protobuf feeds from api-endpoint.mta.info. "
            "In utils/bus.py it is sent as the key query parameter to the MTA Bustime "
            "SIRI endpoint at bustime.mta.info.",
            S["body"],
        ),
        Paragraph(
            "How to get it: Register for a free MTA developer account at "
            "api.mta.info. After registration the dashboard provides an API key "
            "immediately. The same key works for both the GTFS-RT subway feeds and "
            "the Bustime bus API.",
            S["body"],
        ),

        Paragraph("GOOGLE_GEOLOCATION_API_KEY", S["h2"]),
        Paragraph(
            "Used only in api/location.py. Sent as the key query parameter to "
            "https://www.googleapis.com/geolocation/v1/geolocate. This endpoint accepts "
            "a list of WiFi access point MAC addresses and returns a lat/lon.",
            S["body"],
        ),
        Paragraph(
            "How to get it: Create a project in Google Cloud Console, enable the "
            "Geolocation API, and generate an API key under APIs and Services > Credentials. "
            "The Geolocation API has a free tier (a number of requests per month at no cost) "
            "before billing starts. Restrict the key to the Geolocation API only in the "
            "Cloud Console to limit blast radius if the key leaks.",
            S["body"],
        ),

        Paragraph("Local .env File", S["h2"]),
        Paragraph(
            "Create this file in the project root. The python-dotenv load_dotenv() call in "
            "dev_server.py reads it before any imports run. Do not use export or quotes — "
            "python-dotenv parses the file itself.",
            S["body"],
        ),
        *code_block(env_file, S),
        Paragraph(
            "Add .env to your .gitignore immediately. There is no .gitignore in this "
            "project currently — create one with at least .env listed.",
            S["warning"],
        ),

        Paragraph("Setting Keys on Vercel", S["h2"]),
        *code_block(vercel_env, S),

        PageBreak(),
    ]


def section6(S):
    station_entry = """\
{
  "id": "R01",
  "name": "Astoria-Ditmars Blvd",
  "lat": 40.775036,
  "lon": -73.912034,
  "lines": ["N", "W"],
  "north_label": "",
  "south_label": "Manhattan"
}"""

    bus_stop_entry = """\
{
  "id": "MTA_200966",
  "name": "MAIN ST/AMBOY RD",
  "lat": 40.508896,
  "lon": -74.246881,
  "routes": ["MTA NYCT_S78"]
}"""

    stations_csv_header = """\
Station ID,Complex ID,GTFS Stop ID,Division,Line,Stop Name,Borough,
           Daytime Routes,Structure,GTFS Latitude,GTFS Longitude,
           North Direction Label,South Direction Label,...

Example row:
1,1,R01,BMT,Astoria,Astoria-Ditmars Blvd,Q,N W,Elevated,40.775036,-73.912034,,Manhattan,..."""

    convert_script = """\
import csv
import json

stations = []

with open("stations.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stations.append({
            "id":           row["GTFS Stop ID"],       # "R01", "G12", "101" -- NOT "Station ID"
            "name":         row["Stop Name"],
            "lat":          float(row["GTFS Latitude"]),
            "lon":          float(row["GTFS Longitude"]),
            "lines":        row["Daytime Routes"].split(),   # "N W" -> ["N", "W"]
            "north_label":  row["North Direction Label"],
            "south_label":  row["South Direction Label"],
        })

with open("utils/stations.json", "w") as f:
    json.dump(stations, f, indent=2)

print(f"Done -- {len(stations)} stations written to utils/stations.json")"""

    generate_bus = """\
import httpx, json, os, time

API_KEY = os.environ.get("MTA_BUS_API_KEY")
if not API_KEY:
    raise Exception("Set MTA_BUS_API_KEY environment variable first")

# Grid covers Manhattan, Brooklyn, Queens, Bronx, Staten Island
LAT_RANGE = [40.50, 40.91]
LON_RANGE = [-74.25, -73.70]
STEP = 0.02          # ~2km grid spacing

all_stops = {}       # keyed by stop ID to deduplicate overlapping grid cells

lat = LAT_RANGE[0]
while lat <= LAT_RANGE[1]:
    lon = LON_RANGE[0]
    while lon <= LON_RANGE[1]:
        url = (
            f"https://bustime.mta.info/api/where/stops-for-location.json"
            f"?lat={lat}&lon={lon}&latSpan=0.02&lonSpan=0.02&key={API_KEY}"
        )
        try:
            response = httpx.get(url, timeout=10.0)
            data = response.json()
            stops = data.get("data", {}).get("stops", [])
            for stop in stops:
                stop_id = stop["id"]
                if stop_id not in all_stops:   # only add each stop once
                    all_stops[stop_id] = {
                        "id":     stop_id,
                        "name":   stop["name"],
                        "lat":    stop["lat"],
                        "lon":    stop["lon"],
                        "routes": [r["id"] for r in stop.get("routes", [])]
                    }
        except Exception as e:
            print(f"Error at lat={lat} lon={lon}: {e}")

        lon = round(lon + STEP, 3)
        time.sleep(0.1)        # rate limit: 10 requests/second max

    lat = round(lat + STEP, 3)

stops_list = list(all_stops.values())
with open("utils/bus_stops.json", "w") as f:
    json.dump(stops_list, f, indent=2)

print(f"Done -- {len(stops_list)} unique bus stops written to utils/bus_stops.json")"""

    wrong_id_example = """\
WRONG approach (using "Station ID" column):
  row["Station ID"] -> "1", "2", "3", "265"
  These are MTA internal IDs. The GTFS-RT feed uses stop IDs like "G12N", "G12S".
  Lookup will never match. Every departure query silently returns empty lists.

CORRECT approach (using "GTFS Stop ID" column):
  row["GTFS Stop ID"] -> "R01", "G12", "101"
  The GTFS-RT feed uses "R01N"/"R01S", "G12N"/"G12S", "101N"/"101S".
  gtfs.py checks stop_id.startswith(station_id) -- this matches correctly."""

    return [
        Paragraph("Section 6: Static Data Files", S["h1"]),
        hr(),

        Paragraph("Why Pre-Baked JSON?", S["h2"]),
        Paragraph(
            "Station and bus stop data does not change in real time. MTA updates GTFS static "
            "feeds (which include stop coordinates and names) infrequently — typically when "
            "new stations open or existing ones are renamed. Fetching this data live on every "
            "API request would add 100-500ms of latency and an unnecessary external dependency. "
            "Instead, the data is pre-processed into JSON files that are committed to the repo "
            "and loaded once at function cold-start time. This also means zero cost — no "
            "database, no caching layer, no external lookup.",
            S["body"],
        ),

        Paragraph("6a. utils/stations.json", S["h2"]),
        Paragraph(
            "Contains 496 NYC subway stations. Each entry includes the GTFS stop ID used to "
            "match against the real-time feed, the station's coordinates for nearest-neighbor "
            "lookup, the list of train lines serving it (used to pick the right GTFS-RT feed "
            "URLs), and human-readable directional labels.",
            S["body"],
        ),
        Paragraph("Entry shape:", S["h3"]),
        *code_block(station_entry, S),
        sp(2),

        Paragraph("How stations.json is generated", S["h3"]),
        Paragraph(
            "Run convert_stations.py once locally with stations.csv in the project root. "
            "The CSV comes from the MTA's public GTFS station list. The script is 22 lines. "
            "Here it is with inline explanation:",
            S["body"],
        ),
        *code_block(convert_script, S),
        sp(2),

        Paragraph("Critical: Use the Right Column", S["h2"]),
        Paragraph(
            "The stations CSV has two ID columns that look similar but are completely different. "
            "Using the wrong one causes a silent failure where every departure lookup returns "
            "an empty list.",
            S["body"],
        ),
        *code_block(wrong_id_example, S),
        Paragraph(
            "The 'GTFS Stop ID' column (R01, G12, 101) matches the base stop IDs in the "
            "GTFS-RT feed. The GTFS-RT feed appends N or S for direction (R01N, R01S). "
            "gtfs.py handles this by checking stop_id.startswith(station_id), which turns "
            "'R01N'.startswith('R01') into True without any extra processing.",
            S["body"],
        ),
        Paragraph(
            "Alternative: The gtfs_static/stops.txt file in this repo contains the "
            "authoritative GTFS stop IDs directly (stop_id column). It also includes the "
            "N/S variants as child stops. If the CSV is unavailable, parse stops.txt "
            "filtering for rows where location_type == 1 (station, not platform).",
            S["body"],
        ),

        Paragraph("6b. utils/bus_stops.json", S["h2"]),
        Paragraph(
            "Contains 12,581 NYC bus stops. Unlike subway stations, MTA does not publish a "
            "convenient pre-processed list of all bus stops with their routes and coordinates "
            "in a single file. The generate_bus_stops.py script solves this by systematically "
            "querying the MTA's OBA (OneBusAway) endpoint, which returns stops near a given "
            "coordinate.",
            S["body"],
        ),
        Paragraph("Entry shape:", S["h3"]),
        *code_block(bus_stop_entry, S),
        sp(2),

        Paragraph("How bus_stops.json is generated", S["h3"]),
        Paragraph(
            "Run generate_bus_stops.py once locally with MTA_BUS_API_KEY set. "
            "The script grids the NYC bounding box at 0.02-degree intervals (~2km), "
            "queries the stops-for-location endpoint at each point, and deduplicates "
            "results across overlapping grid cells. Takes a few minutes to run.",
            S["body"],
        ),
        *code_block(generate_bus, S),
        Paragraph(
            "The output is committed to the repo. You only need to re-run this if MTA "
            "significantly changes their bus stop network.",
            S["body"],
        ),
        PageBreak(),
    ]


def section7(S):
    haversine_code = """\
import math

EARTH_RADIUS_KM = 6371

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Convert degree differences to radians
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    # Haversine formula: accounts for Earth's curvature
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    # atan2 gives the angular distance; multiply by diameter to get km
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_station(
    user_lat: float, user_lon: float, stations: list[dict]
) -> dict | None:
    if not stations:
        return None
    # min() with a key is O(n) -- fine for 496 stations or 12,581 bus stops
    return min(
        stations,
        key=lambda s: haversine(user_lat, user_lon, s["lat"], s["lon"]),
    )"""

    gtfs_code = """\
import os
import httpx
from google.transit import gtfs_realtime_pb2
from datetime import datetime

# Map each line letter to the MTA feed URL that carries it.
# Multiple lines share feeds: A/C/E share gtfs-ace, B/D/F/M share gtfs-bdfm, etc.
FEED_URLS = {
    "A": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "C": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "E": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "B": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "D": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "F": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "M": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    "J": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "Z": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "N": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "Q": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "R": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "W": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    "1": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "2": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "3": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "4": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "5": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "6": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "7": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "S": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
}

def get_feed_url_for_line(line: str) -> str | None:
    return FEED_URLS.get(line.upper())


async def fetch_departures(station_id: str, lines: list[str]) -> dict:
    now = datetime.now().timestamp()   # Unix timestamp for comparing against feed times

    # Deduplicate URLs. If a station serves B, D, F, M we'd hit gtfs-bdfm four times
    # without this. set() collapses them to one request.
    feed_urls = list(set(
        url for line in lines
        if (url := get_feed_url_for_line(line))
    ))

    northbound = []
    southbound = []

    # The same MTA key used for bus also authenticates GTFS-RT subway feeds
    mta_key = os.environ.get("MTA_BUS_API_KEY", "")
    headers = {"x-api-key": mta_key} if mta_key else {}

    async with httpx.AsyncClient() as client:
        for url in feed_urls:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()

                # Parse the binary protobuf response into a FeedMessage object
                feed = gtfs_realtime_pb2.FeedMessage()
                feed.ParseFromString(response.content)

                for entity in feed.entity:
                    if not entity.HasField("trip_update"):
                        continue          # skip VehiclePosition and Alert entities

                    trip = entity.trip_update
                    route_id = trip.trip.route_id   # e.g. "F", "N", "7"

                    for stop_time in trip.stop_time_update:
                        stop_id = stop_time.stop_id   # e.g. "R20N" or "R20S"

                        # startswith() handles N/S suffix: "R20N".startswith("R20") == True
                        if not stop_id.startswith(station_id):
                            continue

                        # Arrival is preferred; departure is fallback for terminal stops
                        arrival = stop_time.arrival.time or stop_time.departure.time

                        if not arrival or arrival < now:
                            continue    # skip trains that have already departed

                        minutes = round((arrival - now) / 60)
                        entry = {"line": route_id, "minutes": minutes}

                        if stop_id.endswith("N"):
                            northbound.append(entry)
                        elif stop_id.endswith("S"):
                            southbound.append(entry)

            except Exception as e:
                print(f"Error fetching feed {url}: {e}")
                continue    # one bad feed should not kill the whole response

    northbound.sort(key=lambda x: x["minutes"])
    southbound.sort(key=lambda x: x["minutes"])

    return {
        "uptown":   northbound[:3] if northbound else [],
        "downtown": southbound[:3] if southbound else [],
    }"""

    bus_code = """\
import os
import httpx
from datetime import datetime, timezone

BUS_API_URL = "https://bustime.mta.info/api/siri/stop-monitoring.json"


async def fetch_bus_departures(stop_id: str) -> dict:
    api_key = os.environ.get("MTA_BUS_API_KEY", "")
    if not api_key:
        return {"inbound": None, "outbound": None}   # degrade gracefully if key missing

    now = datetime.now(timezone.utc).timestamp()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                BUS_API_URL,
                params={
                    "key": api_key,
                    "MonitoringRef": stop_id,    # the MTA_xxxxxx stop ID
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching bus departures: {e}")
            return {"inbound": None, "outbound": None}

    # The SIRI response has deeply nested structure. Every .get() is necessary --
    # any level can be missing if the stop has no service or the API is degraded.
    visits = (
        data.get("Siri", {})
        .get("ServiceDelivery", {})
        .get("StopMonitoringDelivery", [{}])[0]
        .get("MonitoredStopVisit", [])
    )

    inbound  = []
    outbound = []

    for visit in visits:
        journey      = visit.get("MonitoredVehicleJourney", {})
        route        = journey.get("PublishedLineName", "")
        direction_ref = journey.get("DirectionRef", "")

        # ExpectedArrivalTime is real-time; AimedArrivalTime is scheduled.
        # Current code uses only Expected -- if that's absent, the entry is skipped.
        arrival = (
            journey.get("MonitoredCall", {})
            .get("ExpectedArrivalTime", "")
        )
        if not arrival:
            continue

        try:
            # MTA returns ISO 8601 with timezone offset; replace Z for Python compat
            arrival_dt = datetime.fromisoformat(arrival.replace("Z", "+00:00"))
            minutes = round((arrival_dt.timestamp() - now) / 60)
        except (ValueError, TypeError):
            continue

        if minutes < 0:
            continue    # bus already passed

        entry = {"route": route, "minutes": minutes}

        if direction_ref == "0":
            inbound.append(entry)
        elif direction_ref == "1":
            outbound.append(entry)

    inbound.sort(key=lambda x: x["minutes"])
    outbound.sort(key=lambda x: x["minutes"])

    return {
        "inbound":  inbound[:3]  if inbound  else [],
        "outbound": outbound[:3] if outbound else [],
    }"""

    trains_code = """\
from fastapi import FastAPI, HTTPException, Query, Request
from utils.haversine import find_nearest_station
from utils.gtfs import fetch_departures
import json, os, httpx

app = FastAPI()

# Load station data once at cold-start, not per request.
# os.path.dirname(__file__) is needed because Vercel runs each function
# in its own directory context -- relative paths are unreliable.
_stations_path = os.path.join(os.path.dirname(__file__), "../utils/stations.json")
with open(_stations_path) as f:
    STATIONS = json.load(f)   # 496 station dicts loaded into memory

NYC_COORDS = (40.7128, -74.0060)   # fallback: midtown Manhattan


async def geolocate_ip(ip: str) -> tuple[float, float]:
    # Don't hit ip-api.com with loopback addresses from local dev
    if ip in ("127.0.0.1", "::1", "localhost"):
        return NYC_COORDS
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}", timeout=5.0)
            data = resp.json()
            if data.get("status") == "success":
                return data["lat"], data["lon"]
    except Exception:
        pass
    return NYC_COORDS   # any failure -> default to NYC


@app.get("/api/trains")
async def get_trains(
    request: Request,
    station: str | None = None,              # explicit station ID override
    lat: float | None = Query(None),         # explicit coordinates
    lon: float | None = Query(None),
):
    # Priority 1: explicit station ID
    if station is not None:
        matches = [s for s in STATIONS if s["id"] == station]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Station {station} not found")
        found = matches[0]

    # Priority 2: explicit lat/lon
    elif lat is not None and lon is not None:
        found = find_nearest_station(lat, lon, STATIONS)
        if found is None:
            return {"station": None, "uptown": None, "downtown": None}

    # Priority 3: geolocate by caller IP
    else:
        # X-Forwarded-For can be a comma-separated list when through multiple proxies.
        # Take the first (leftmost) IP -- that is the original client.
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() or (
            request.client.host if request.client else "127.0.0.1"
        )
        lat2, lon2 = await geolocate_ip(ip)
        found = find_nearest_station(lat2, lon2, STATIONS)
        if found is None:
            return {"station": None, "uptown": None, "downtown": None}

    departures = await fetch_departures(found["id"], found["lines"])

    return {
        "station":    found["name"],
        "uptown":     departures["uptown"],
        "downtown":   departures["downtown"],
        "north_label": found["north_label"],
        "south_label": found["south_label"],
    }"""

    buses_code = """\
from fastapi import FastAPI, HTTPException, Query, Request
from utils.haversine import find_nearest_station
from utils.bus import fetch_bus_departures
import json, os, httpx

app = FastAPI()

_bus_stops_path = os.path.join(os.path.dirname(__file__), "../utils/bus_stops.json")
BUS_STOPS = []
# Conditional load: if bus_stops.json doesn't exist yet the app still starts.
# This lets you run the server before generating the data file.
if os.path.exists(_bus_stops_path):
    with open(_bus_stops_path) as f:
        BUS_STOPS = json.load(f)    # 12,581 bus stop dicts

NYC_COORDS = (40.7128, -74.0060)


async def geolocate_ip(ip: str) -> tuple[float, float]:
    if ip in ("127.0.0.1", "::1", "localhost"):
        return NYC_COORDS
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}", timeout=5.0)
            data = resp.json()
            if data.get("status") == "success":
                return data["lat"], data["lon"]
    except Exception:
        pass
    return NYC_COORDS


@app.get("/api/buses")
async def get_buses(
    request: Request,
    stop: str | None = None,
    lat: float | None = Query(None),
    lon: float | None = Query(None),
):
    # Early return if bus_stops.json was not generated yet
    if not BUS_STOPS and stop is None and lat is None:
        return {"stop": None, "inbound": None, "outbound": None}

    if stop is not None:
        matches = [s for s in BUS_STOPS if s["id"] == stop]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Stop {stop} not found")
        found = matches[0]

    elif lat is not None and lon is not None:
        found = find_nearest_station(lat, lon, BUS_STOPS)
        if found is None:
            return {"stop": None, "inbound": None, "outbound": None}

    else:
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() or (
            request.client.host if request.client else "127.0.0.1"
        )
        lat2, lon2 = await geolocate_ip(ip)
        found = find_nearest_station(lat2, lon2, BUS_STOPS)
        if found is None:
            return {"stop": None, "inbound": None, "outbound": None}

    departures = await fetch_bus_departures(found["id"])

    return {
        "stop":     found["name"],
        "inbound":  departures["inbound"],
        "outbound": departures["outbound"],
    }"""

    location_code = """\
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx, os

app = FastAPI()

GOOGLE_GEOLOCATION_URL = "https://www.googleapis.com/geolocation/v1/geolocate"


# Pydantic models give us free request validation and a clean .model_dump()
# for forwarding the body to Google's API unchanged.
class WiFiAccessPoint(BaseModel):
    macAddress: str
    signalStrength: int


class LocationRequest(BaseModel):
    wifiAccessPoints: list[WiFiAccessPoint]


@app.post("/api/location")
async def get_location(body: LocationRequest):
    api_key = os.environ.get("GOOGLE_GEOLOCATION_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_GEOLOCATION_API_KEY not configured")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_GEOLOCATION_URL,
                params={"key": api_key},
                json=body.model_dump(),   # Pydantic model -> plain dict -> JSON
                timeout=10.0,
            )
            resp.raise_for_status()       # raise on 4xx/5xx from Google
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google Geolocation API error: {e.response.status_code}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to geolocate: {e}")

    location = data.get("location", {})
    lat = location.get("lat")
    lon = location.get("lng")    # Google returns "lng", not "lon" -- we rename it here

    if lat is None or lon is None:
        raise HTTPException(status_code=500, detail="Google Geolocation API returned no location")

    return {"lat": lat, "lon": lon}"""

    devserver_code = """\
\"\"\"
Local dev entrypoint that combines the separate api/*.py apps onto one port.

Vercel deploys each api/*.py file as its own serverless function (see vercel.json),
so each defines its own FastAPI() app. This mounts their routers together for
uvicorn dev_server:app --reload --port 8000 so all /api/* routes work locally.
\"\"\"
from dotenv import load_dotenv

load_dotenv()   # reads .env into os.environ BEFORE importing api modules

from fastapi import FastAPI

from api.buses    import app as buses_app
from api.location import app as location_app
from api.trains   import app as trains_app

app = FastAPI()
app.include_router(trains_app.router)
app.include_router(buses_app.router)
app.include_router(location_app.router)"""

    return [
        Paragraph("Section 7: Backend — File by File", S["h1"]),
        hr(),

        Paragraph("utils/haversine.py", S["h2"]),
        Paragraph(
            "The distance engine. Two functions: haversine() computes the great-circle "
            "distance in kilometers between two lat/lon points using the Haversine formula, "
            "which correctly accounts for Earth's curvature. find_nearest_station() uses "
            "Python's built-in min() with a key function to scan the entire station list and "
            "return whichever station minimizes the haversine distance to the user's position.",
            S["body"],
        ),
        Paragraph(
            "Why haversine and not Euclidean distance? At NYC latitudes, treating lat/lon as "
            "a flat grid introduces about 25-30% error on east-west distances due to longitude "
            "lines converging toward the poles. Over a 500m radius this is acceptable, but "
            "haversine costs nothing extra so there is no reason not to use it.",
            S["body"],
        ),
        *code_block(haversine_code, S),
        sp(2),

        Paragraph("utils/gtfs.py", S["h2"]),
        Paragraph(
            "The subway real-time data layer. MTA publishes seven GTFS-RT protobuf feeds, "
            "grouped by line family. This file maps every line letter to its feed URL, fetches "
            "only the feeds needed for the given station's lines, parses the protobuf binary "
            "response, and extracts upcoming departures in both directions.",
            S["body"],
        ),
        Paragraph(
            "The deduplication step (set() on the URL list) is load-bearing: a station like "
            "34 St-Herald Sq serves B, D, F, M, N, Q, R, W — that's two feed URLs, not eight. "
            "Without deduplication you'd make four duplicate requests to each feed.",
            S["body"],
        ),
        Paragraph(
            "Note that MTA_BUS_API_KEY is reused here as the x-api-key header for GTFS-RT "
            "feeds. Despite the variable name, the same MTA developer key authenticates both "
            "the bus API and the subway feeds.",
            S["body"],
        ),
        *code_block(gtfs_code, S),
        sp(2),

        Paragraph("utils/bus.py", S["h2"]),
        Paragraph(
            "The bus real-time data layer. Calls MTA Bustime's SIRI stop-monitoring endpoint. "
            "SIRI is an EU transit standard; the MTA's implementation wraps it in JSON but "
            "keeps the verbose nested structure. The chain of .get() calls down to "
            "MonitoredStopVisit is necessary because any level can be absent in degraded "
            "responses.",
            S["body"],
        ),
        Paragraph(
            "DirectionRef '0' is inbound (toward Manhattan / main terminal) and '1' is outbound. "
            "These are MTA conventions and are not explained in the SIRI spec itself.",
            S["body"],
        ),
        *code_block(bus_code, S),
        sp(2),

        Paragraph("api/trains.py", S["h2"]),
        Paragraph(
            "The /api/trains route handler. Implements a three-level location fallback: "
            "explicit station ID, explicit coordinates, IP geolocation. Station data is loaded "
            "from JSON at module load time (cold start), not per request.",
            S["body"],
        ),
        *code_block(trains_code, S),
        sp(2),

        Paragraph("api/buses.py", S["h2"]),
        Paragraph(
            "Identical structure to trains.py but for buses. One difference: the conditional "
            "load of bus_stops.json (if os.path.exists(...)) means the app starts cleanly "
            "even if you haven't run generate_bus_stops.py yet. The endpoint returns nulls in "
            "that case rather than crashing.",
            S["body"],
        ),
        *code_block(buses_code, S),
        sp(2),

        Paragraph("api/location.py", S["h2"]),
        Paragraph(
            "The /api/location route handler. Accepts a POST body containing WiFi access points "
            "(MAC addresses + signal strengths), forwards the body directly to Google's "
            "Geolocation API, and returns clean lat/lon. The Pydantic models serve double duty: "
            "request validation (FastAPI rejects malformed bodies automatically) and "
            "serialization (body.model_dump() converts back to a dict for the outbound request). "
            "Note the lng-to-lon rename: Google returns 'lng', the rest of the codebase expects "
            "'lon'.",
            S["body"],
        ),
        *code_block(location_code, S),
        sp(2),

        Paragraph("dev_server.py", S["h2"]),
        Paragraph(
            "Not deployed to Vercel. Used only for local development. Mounts all three "
            "FastAPI routers onto a single app so that one uvicorn process serves all three "
            "endpoints. load_dotenv() must be called before the api imports because those "
            "modules reference os.environ at import time (stations.json is read at module "
            "load, not inside the route handler).",
            S["body"],
        ),
        *code_block(devserver_code, S),
        PageBreak(),
    ]


def section8(S):
    vercel_json = """\
{
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/$1.py"
    }
  ]
}"""

    deploy_cmds = """\
# Initial deploy (run from project root)
vercel

# Add every required environment variable
vercel env add MTA_BUS_API_KEY
vercel env add GOOGLE_GEOLOCATION_API_KEY

# Promote to production
vercel --prod"""

    test_prod = """\
# Replace YOUR_VERCEL_DOMAIN with your actual deployment URL

# Test trains by coordinates
curl "https://YOUR_VERCEL_DOMAIN/api/trains?lat=40.7484&lon=-73.9857"

# Test trains by explicit station ID
curl "https://YOUR_VERCEL_DOMAIN/api/trains?station=R20"

# Test buses by coordinates
curl "https://YOUR_VERCEL_DOMAIN/api/buses?lat=40.7484&lon=-73.9857"

# Test location endpoint
curl -X POST "https://YOUR_VERCEL_DOMAIN/api/location" \\
  -H "Content-Type: application/json" \\
  -d '{"wifiAccessPoints": [{"macAddress": "aa:bb:cc:dd:ee:ff", "signalStrength": -65}]}'

# Test IP geolocation fallback (no params -- uses caller's IP)
curl "https://YOUR_VERCEL_DOMAIN/api/trains" """

    return [
        Paragraph("Section 8: Deploy to Vercel", S["h1"]),
        hr(),

        Paragraph("vercel.json Explained", S["h2"]),
        Paragraph(
            "This file tells Vercel's build system two things: how to build the code, "
            "and how to route requests.",
            S["body"],
        ),
        *code_block(vercel_json, S),
        Paragraph(
            "The builds block tells Vercel to compile every .py file in api/ using the "
            "@vercel/python runtime. Each file becomes an independent serverless function "
            "with its own process, its own memory, and its own cold start. They do not share "
            "any in-memory state.",
            S["body"],
        ),
        Paragraph(
            "The routes block maps incoming URLs to files. /api/(.*) captures everything after "
            "/api/ and routes it to api/$1.py. So /api/trains goes to api/trains.py, "
            "/api/buses to api/buses.py, /api/location to api/location.py.",
            S["body"],
        ),

        Paragraph("Deploy Commands", S["h2"]),
        *code_block(deploy_cmds, S),
        Paragraph(
            "The first vercel command creates the project, links it to your Vercel account, "
            "and deploys to a preview URL. Set environment variables before running --prod. "
            "Vercel stores env vars per environment (Production, Preview, Development) -- "
            "add them to all three.",
            S["body"],
        ),

        Paragraph("Testing Production Endpoints", S["h2"]),
        *code_block(test_prod, S),
        PageBreak(),
    ]


def section9(S):
    trains_trace = """\
T=0ms   GET /api/trains?lat=40.7484&lon=-73.9857 arrives at Vercel edge

T=0ms   Cold start (if first request): Vercel spins up the api/trains.py function.
        Python imports run. stations.json (496 entries) is read from disk into STATIONS.

T=5ms   get_trains() handler begins.
        lat=40.7484, lon=-73.9857 parsed from query string.

T=5ms   find_nearest_station(40.7484, -73.9857, STATIONS) called.
        496 haversine computations run synchronously.
        Returns: {id: "R20", name: "34 St-Herald Sq", lines: ["B","D","F","M","N","Q","R","W"],
                  north_label: "Uptown & The Bronx", south_label: "Downtown & Brooklyn"}

T=6ms   fetch_departures("R20", ["B","D","F","M","N","Q","R","W"]) called.
        Deduplicated feed URLs: ["gtfs-bdfm URL", "gtfs-nqrw URL"]
        Two concurrent HTTP requests dispatched.

T=6ms   httpx opens connections to MTA's api-endpoint.mta.info for both feeds.

T+~300ms  Both protobuf responses received (~50-200KB each).

T+300ms   gtfs_realtime_pb2.FeedMessage().ParseFromString() runs for feed 1.
          Iterates all TripUpdate entities.
          For each StopTimeUpdate: checks stop_id.startswith("R20").
          "R20N" matches -> northbound. "R20S" matches -> southbound.
          Minutes = round((arrival_unix - now_unix) / 60).

T+310ms   Same parse runs for feed 2.

T+315ms   northbound and southbound lists sorted by minutes.
          Each truncated to top 3.

T+316ms   JSON response serialized and returned.

Example response:
{
  "station": "34 St-Herald Sq",
  "uptown":  [{"line": "B", "minutes": 2}, {"line": "D", "minutes": 5}, {"line": "F", "minutes": 7}],
  "downtown":[{"line": "N", "minutes": 1}, {"line": "R", "minutes": 4}, {"line": "Q", "minutes": 6}],
  "north_label": "Uptown & The Bronx",
  "south_label": "Downtown & Brooklyn"
}

Total wall time: ~320ms on warm function, ~800ms-1200ms on cold start."""

    buses_trace = """\
T=0ms   GET /api/buses?lat=40.7484&lon=-73.9857 arrives.

T=5ms   find_nearest_station() scans 12,581 bus stops.
        Returns nearest stop dict with id, name, lat, lon, routes.

T=6ms   fetch_bus_departures("MTA_305423") called.
        GET https://bustime.mta.info/api/siri/stop-monitoring.json
            ?key=MTA_BUS_API_KEY&MonitoringRef=MTA_305423

T+~400ms  JSON response received. Parses SIRI envelope:
          Siri -> ServiceDelivery -> StopMonitoringDelivery[0] -> MonitoredStopVisit[]

          For each visit:
            journey = MonitoredVehicleJourney
            route   = journey.PublishedLineName       ("M34A+")
            dir     = journey.DirectionRef             ("0" or "1")
            arrival = journey.MonitoredCall.ExpectedArrivalTime  (ISO 8601)
            minutes = round((arrival_timestamp - now) / 60)

T+410ms   inbound and outbound sorted, top 3 each.

T+411ms   Response returned.

Example response:
{
  "stop": "7 AV/W 34 ST",
  "inbound":  [{"route": "M34A+", "minutes": 2}, {"route": "M34A+", "minutes": 9}],
  "outbound": [{"route": "M34A+", "minutes": 4}, {"route": "M34A+", "minutes": 12}]
}"""

    return [
        Paragraph("Section 9: Happy Path — End to End", S["h1"]),
        hr(),

        Paragraph("Trains Request", S["h2"]),
        *code_block(trains_trace, S),
        sp(2),

        Paragraph("Buses Request", S["h2"]),
        *code_block(buses_trace, S),
        PageBreak(),
    ]


def section10(S):
    return [
        Paragraph("Section 10: Known Bugs and Fixes", S["h1"]),
        hr(),

        Paragraph("Bug 1: IP Geolocation Returns Vercel Proxy IP", S["h2"]),
        Paragraph("Symptom:", S["h3"]),
        Paragraph(
            "When no lat/lon is provided, the API geolocates the caller's IP and always "
            "returns the same location regardless of where the caller actually is. All "
            "IP-based lookups return an address in the Vercel infrastructure region.",
            S["body"],
        ),
        Paragraph("Root cause:", S["h3"]),
        Paragraph(
            "Vercel's serverless runtime sits behind a proxy. request.client.host gives "
            "you the proxy's IP, not the caller's. The caller's real IP is in the "
            "X-Forwarded-For header, which Vercel sets automatically.",
            S["body"],
        ),
        Paragraph("Fix (already applied in the codebase):", S["h3"]),
        *code_block(
            'forwarded = request.headers.get("x-forwarded-for", "")\n'
            'ip = forwarded.split(",")[0].strip() or (\n'
            '    request.client.host if request.client else "127.0.0.1"\n'
            ')',
            S,
        ),
        Paragraph(
            "X-Forwarded-For can contain multiple IPs (client, then each proxy). "
            "The leftmost is always the original client. .split(',')[0].strip() extracts it.",
            S["body"],
        ),

        Paragraph("Bug 2: stations.json Built From Wrong Column", S["h2"]),
        Paragraph("Symptom:", S["h3"]),
        Paragraph(
            "Every call to /api/trains returns empty uptown and downtown lists. No error "
            "is raised. The departure lookup runs but finds no matching stop IDs in the feed.",
            S["body"],
        ),
        Paragraph("Root cause:", S["h3"]),
        Paragraph(
            "The MTA stations CSV has a 'Station ID' column (values: 1, 2, 3, 265...) and "
            "a separate 'GTFS Stop ID' column (values: R01, G12, 101...). If you use "
            "row['Station ID'] instead of row['GTFS Stop ID'] in convert_stations.py, the "
            "JSON gets numeric IDs that never match GTFS-RT stop IDs like 'R01N' or 'G12S'.",
            S["body"],
        ),
        Paragraph("Fix:", S["h3"]),
        *code_block(
            '# In convert_stations.py -- use the GTFS Stop ID column, not Station ID\n'
            '"id": row["GTFS Stop ID"],   # correct: "R01", "G12", "101"\n'
            '# NOT: row["Station ID"]     # wrong:   "1",   "265", "3"',
            S,
        ),

        Paragraph("Bug 3: Bus Departures Return Empty When Buses Are Running", S["h2"]),
        Paragraph("Symptom:", S["h3"]),
        Paragraph(
            "The /api/buses endpoint returns empty inbound/outbound arrays even when "
            "buses are actively running at that stop.",
            S["body"],
        ),
        Paragraph("Root cause:", S["h3"]),
        Paragraph(
            "The current code only uses ExpectedArrivalTime. Some vehicles report only "
            "AimedArrivalTime (the scheduled time) in their MonitoredCall, particularly "
            "when the bus is not yet tracked in real time. If ExpectedArrivalTime is "
            "absent and no fallback is attempted, those vehicles are silently skipped.",
            S["body"],
        ),
        Paragraph("Fix:", S["h3"]),
        *code_block(
            '# In utils/bus.py, fall back to AimedArrivalTime when Expected is absent\n'
            'monitored_call = journey.get("MonitoredCall", {})\n'
            'arrival = (\n'
            '    monitored_call.get("ExpectedArrivalTime")\n'
            '    or monitored_call.get("AimedArrivalTime")\n'
            '    or ""\n'
            ')',
            S,
        ),

        Paragraph("Bug 4: Port 8000 Already in Use Locally", S["h2"]),
        Paragraph("Symptom:", S["h3"]),
        Paragraph(
            "uvicorn exits immediately with 'address already in use' when starting dev_server.",
            S["body"],
        ),
        Paragraph("Fix:", S["h3"]),
        *code_block(
            "# Find and kill whatever is using port 8000\n"
            "lsof -ti:8000 | xargs kill -9\n\n"
            "# Or use a different port\n"
            "uvicorn dev_server:app --reload --port 8001",
            S,
        ),

        Paragraph("Bug 5: Cold Start Reads stations.json Before .env Loads", S["h2"]),
        Paragraph("Symptom:", S["h3"]),
        Paragraph(
            "Locally, api/trains.py or api/buses.py raises FileNotFoundError when imported "
            "directly (not via dev_server.py).",
            S["body"],
        ),
        Paragraph("Root cause:", S["h3"]),
        Paragraph(
            "stations.json is loaded at module import time using os.path.dirname(__file__). "
            "If you import api.trains directly from a different working directory, the path "
            "resolves incorrectly. Always run via dev_server.py locally.",
            S["body"],
        ),
        Paragraph("Fix:", S["h3"]),
        *code_block(
            "# Always use dev_server.py for local development\n"
            "uvicorn dev_server:app --reload --port 8000\n\n"
            "# Never run individual api files directly\n"
            "# uvicorn api.trains:app  <-- this will fail locally",
            S,
        ),

        Paragraph("Bug 6: Google Geolocation Returns lng Not lon", S["h2"]),
        Paragraph("Symptom:", S["h3"]),
        Paragraph(
            "If you naively forward Google's response to callers, the longitude field is "
            "named 'lng' not 'lon', which breaks downstream code expecting 'lon'.",
            S["body"],
        ),
        Paragraph("Fix (already applied in api/location.py):", S["h3"]),
        *code_block(
            'location = data.get("location", {})\n'
            'lat = location.get("lat")\n'
            'lon = location.get("lng")   # Google says "lng"; we expose it as "lon"\n'
            'return {"lat": lat, "lon": lon}',
            S,
        ),

        PageBreak(),
    ]


def section11(S):
    def check(text):
        return Paragraph(f"[ ]  {text}", S["checklist"])

    return [
        Paragraph("Section 11: Testing Checklist", S["h1"]),
        hr(),

        Paragraph("Local", S["h2"]),
        check("Dev server starts without errors: uvicorn dev_server:app --reload --port 8000"),
        check("GET /api/trains returns JSON with station, uptown, downtown, north_label, south_label"),
        check("GET /api/buses returns JSON with stop, inbound, outbound"),
        check("POST /api/location returns JSON with lat and lon"),
        check("GET /api/trains?station=R01 returns Astoria-Ditmars Blvd"),
        check("GET /api/trains?lat=40.7484&lon=-73.9857 returns 34 St area station"),
        check("GET /api/buses?lat=40.7484&lon=-73.9857 returns a midtown bus stop"),
        check("GET /api/buses?stop=MTA_200966 returns MAIN ST/AMBOY RD"),
        check("uptown and downtown arrays each contain up to 3 entries"),
        check("inbound and outbound arrays each contain up to 3 entries"),
        check("Each train entry has line and minutes fields"),
        check("Each bus entry has route and minutes fields"),
        check("minutes values are non-negative integers"),
        check("GET /api/trains with no params falls back to IP geolocation (returns some NYC station)"),
        check("north_label and south_label are non-empty for stations that serve them"),
        sp(2),

        Paragraph("Vercel (Production)", S["h2"]),
        check("vercel --prod completes without build errors"),
        check("MTA_BUS_API_KEY is set in Vercel dashboard for Production environment"),
        check("GOOGLE_GEOLOCATION_API_KEY is set in Vercel dashboard for Production environment"),
        check("GET https://YOUR_DOMAIN/api/trains?lat=40.7484&lon=-73.9857 returns valid JSON"),
        check("GET https://YOUR_DOMAIN/api/buses?lat=40.7484&lon=-73.9857 returns valid JSON"),
        check("POST https://YOUR_DOMAIN/api/location with real WiFi data returns lat/lon"),
        check("No 500 errors in Vercel function logs (check vercel logs in CLI or dashboard)"),
        check("Response times under 1000ms on warm functions"),
        check("GET /api/trains (no params) returns a valid station based on caller IP"),
        sp(2),

        Paragraph("Edge Cases", S["h2"]),
        check("GET /api/trains?station=INVALID returns 404 with detail message"),
        check("GET /api/buses?stop=INVALID returns 404 with detail message"),
        check("POST /api/location with empty wifiAccessPoints array returns 500 from Google (expected)"),
        check("POST /api/location with malformed body returns 422 Unprocessable Entity from FastAPI"),
        check("Endpoints return non-null uptown/downtown even if one direction has no trains"),
        PageBreak(),
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_pdf():
    S = build_styles()

    doc = SimpleDocTemplate(
        "TUTORIAL.pdf",
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN + 0.3 * inch,  # extra bottom room for footer
    )

    story = []
    story += title_page(S)
    story += toc_page(S)
    story += section1(S)
    story += section2(S)
    story += section3(S)
    story += section4(S)
    story += section5(S)
    story += section6(S)
    story += section7(S)
    story += section8(S)
    story += section9(S)
    story += section10(S)
    story += section11(S)

    doc.build(story, canvasmaker=NumberedCanvas)
    print("TUTORIAL.pdf written.")


if __name__ == "__main__":
    build_pdf()
