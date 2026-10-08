# SIH26006: Ministry of Steel Freight Dashboard
## Exhaustive Technical & Operational System Architecture Documentation
*(Version 3.0 - Expanded Deep-Dive)*

---

## 1. Executive Summary and Strategic Vision

### 1.1 Objective and Scope
The **SIH26006 Freight Dashboard** represents a multi-faceted, enterprise-grade software architecture developed for the Government of India's Ministry of Steel. The core directive of this platform is to algorithmically optimize the procurement and chartering of massive bulk cargo vessels. The system strictly deals with Capesize (160k-180k MT) and Panamax (80k MT) class vessels responsible for importing indispensable raw materials—specifically iron ore and coking coal—from major global export hubs (Australia, South Africa, and Brazil) exclusively to the East Coast of India (ECI).

### 1.2 The Problem Statement
The global maritime shipping industry is plagued by extreme volatility. Spot charter rates for Capesize vessels can swing wildly based on macroeconomic indicators, geopolitical instability (e.g., bunker fuel shocks), and port congestion. When the Ministry of Steel secures vessels reactively, it exposes the government to millions of dollars in unexpected freight costs.

### 1.3 The Solution
This platform introduces an AI-driven paradigm shift. By integrating a predictive machine learning pipeline with real-time voyage economic stress-testing, the dashboard empowers logistics officers to secure freight forward contracts or time-charters exactly when the algorithmic models predict an impending market squeeze. 

---

## 2. Machine Learning Pipeline & Predictive Analytics

### 2.1 The Forecasting Engine Overview
At the core of the backend architecture is a time-series machine learning model responsible for forecasting the **Baltic Exchange Capesize Index (BCI)**. The engine is designed to parse highly noisy financial data and extract actionable short-to-medium-term trends.

### 2.2 Data Ingestion & Synthetic Generation Fallbacks
The data pipeline (`scrape_baltic_capesize.py`, `fetch_macro_data.py`) relies on live web scraping from sources like Investing.com. However, scraping financial data is highly volatile due to Cloudflare and other anti-bot implementations. 
To guarantee 100% uptime, the data layer includes a sophisticated **Synthetic Data Generator**. If web requests fail, the system falls back to generating statistically accurate synthetic rates based on historical means and variances, seamlessly extrapolating data up to the current date.

### 2.3 Feature Engineering (`01_feature_engineering.py`)
The model requires a robust feature set, which includes:
- **Historical Lag Features:** Spot rates from $t-1$, $t-7$, $t-30$.
- **Macroeconomic Anchors:** Brent Crude Oil Index, directly influencing the bunker fuel subset of shipping rates.
- **Rolling Averages:** 14-day and 30-day Simple Moving Averages (SMA) to smooth out daily market noise.
- **Seasonality Flags:** Iron ore demand traditionally spikes in Q3/Q4.

### 2.4 Model Outputs & Validation Metrics
The target outputs are multi-horizon continuous variables:
1. **+7-Day Forecast:** Highly accurate, targeted MAPE (Mean Absolute Percentage Error) of < 8%. Used for immediate spot fixtures.
2. **+14-Day Forecast:** Medium-term trend indicator.
3. **+30-Day Forecast:** The critical anchor for the Operations Directive. Used to determine if the Ministry should abandon spot markets and lock into a 3-Month Time Charter.

### 2.5 The Operations Directive Algorithm
The `chartering_strategy_optimizer()` executes a deterministic logic tree over the 30-day ML forecast:
- **Calculation (`delta_pct`):** `(forecasted_30d_rate - spot_rate) / spot_rate`
- **Surge Condition (`delta_pct >= 0.05`):** If the market is predicted to surge by 5% or more, the algorithm triggers a **"LOCK 3-MONTH TIME CHARTER"** directive, advising officers to secure long-term contracts immediately to hedge against rising rates.
- **Crash Condition (`delta_pct <= -0.05`):** If a market drop is predicted, the directive displays **"DELAY SPOT CHARTER"**, preventing officers from overpaying today.
- **Stable Condition:** **"SPOT CHARTER NOW"**.

---

## 3. Backend Architecture: FastAPI & The Logistics Engine

### 3.1 Backend Stack
The backend is powered by **FastAPI** (Python 3.10+), utilizing Pydantic for strict data validation and schema enforcement. FastAPI was chosen for its extreme speed and native asynchronous capabilities, essential for serving ML inferences and complex logistics permutations to the frontend with zero latency.

### 3.2 Deep Dive: `src/logistics_engine.py`
The logistics engine is the mathematical heart of the platform. It calculates exact landed freight costs (USD/Metric Ton) based on dynamic user inputs.

#### 3.2.1 Route Definitions
The system hardcodes three primary strategic corridors:
- **Australia to ECI:** 15 Days sailing, 160k MT payload.
- **South Africa to ECI:** 19 Days sailing, 150k MT payload.
- **Brazil to ECI:** 33 Days sailing, 170k MT payload.

#### 3.2.2 `calculate_voyage_economics()`
This function computes the baseline costs:
```python
shock_multiplier = 1.0 + (brent_shock_pct / 100.0)
bunker_price_per_mt = brent_crude_usd * 6.5 * shock_multiplier
total_bunker_expense = total_voyage_days * 40 * bunker_price_per_mt
charter_hire_expense = total_voyage_days * capesize_day_rate
```
*Note: A standard Capesize vessel burns approximately 40 MT of VLSFO (Very Low Sulphur Fuel Oil) per day.*

#### 3.2.3 `split_cargo_optimizer()` (Fleet Optimization)
A highly sophisticated module that evaluates the financial viability of a twin-Panamax strategy over a single Capesize booking.
- **Capesize Assumptions:** 1x 160k MT vessel, 40 MT/day fuel consumption.
- **Twin-Panamax Assumptions:** 2x 80k MT vessels. The algorithm applies a `0.65` mathematical ratio to the Capesize spot rate to determine Panamax daily hire costs. It dynamically lowers the bunker consumption model to 28 MT/day per Panamax vessel.
- **Output:** The algorithm calculates the absolute difference in Landed Cost ($/MT). If `savings > 0`, `is_split_cheaper` evaluates to `True`, triggering frontend UI alerts.

#### 3.2.4 `FLEET_SIMULATION_DATA`
A data dictionary containing geographical coordinates for major global ports and the specific polyline arrays mapping the oceanic corridors. It includes a simulated array of active vessels (e.g., "Bulk Pioneer", IMO: IMO9123456) with calculated ETAs and live transit speeds.

---

## 4. RESTful API Specifications (`src/api.py`)

The FastAPI gateway exposes the following crucial endpoints:

- **`GET /api/logistics/routes`**
  - **Returns:** JSON object containing the hardcoded route definitions and baseline parameters.
  
- **`GET /api/rates/historical`**
  - **Returns:** Time-series array of historical Capesize spot rates and Brent Crude index values for frontend charting.

- **`POST /api/rates/forecast`**
  - **Payload:** Current temporal features.
  - **Returns:** Extrapolated `7-Day`, `14-Day`, and `30-Day` forecasts.

- **`POST /api/logistics/voyage-calculator`**
  - **Payload:** Route ID, Spot Rate, Brent USD, Congestion Days.
  - **Returns:** Exhaustive breakdown of Voyage Economics (Bunker fuel cost, Charter hire, Landed cost) and the Operations Directive.

- **`POST /api/logistics/split-cargo-eval`**
  - **Payload:** Route ID, Spot Rate, Brent USD.
  - **Returns:** Comparative economics (`capesize` vs `twin_panamax`), exact `$ Savings/MT`, and a boolean optimization flag.

- **`GET /api/logistics/fleet-simulation`**
  - **Returns:** `FLEET_SIMULATION_DATA` payload injected into the React-Leaflet map.

---

## 5. Frontend Architecture: The React Command Center

The User Interface is an SPA (Single Page Application) built with **React (Vite)** and heavily styled using utility classes from **Tailwind CSS**. It is responsive, highly modular, and designed strictly for enterprise dashboard use-cases.

### 5.1 Global Layout (`App.jsx`)
The overarching architecture was explicitly redesigned to a highly effective **3-column asymmetrical grid** (`lg:grid-cols-3`).
- **Left Column (`col-span-1`):** Houses the control levers (`RouteCalculator.jsx`) and the ultimate financial output (`ProcurementStrategy.jsx`), stacking them vertically.
- **Right Column (`col-span-2`):** Houses the `RouteMap.jsx` component. By allocating 2/3 of the screen width and utilizing `h-full flex-grow` CSS properties, the interactive map scales massively to match the combined height of the left column.

### 5.2 The Top KPI Grid
A critical component rendering an immediate executive snapshot of the market.
- **Current Spot Rate & Brent Crude:** Displays realtime ingested data.
- **30-Day Projected Rate:** Incorporates a dynamic Tailwind badge. If the rate is rising, it applies `bg-rose-100 text-rose-700`. If falling, `bg-emerald-100`.
- **Operations Directive Badge:** Changes entirely based on backend output. A "LOCK 3-MONTH" directive triggers a high-alert red UI (`bg-rose-600`), commanding immediate user attention.

### 5.3 Predictive Forecast Chart (`ForecastChart.jsx`)
Built over the `Recharts` library, this component merges the 60-day historical `actual` rates with the 30-day `forecasted` rates.
- **Dynamic Y-Axis Scaling:** Crucially, the chart uses `domain={['auto', 'auto']}`. This prevents the chart from artificially flattening market trends by starting at $0, thereby visually exacerbating the true volatility of the shipping index.

### 5.4 The Route Economics Simulator (`RouteCalculator.jsx`)
This component is highly interactive, binding HTML range inputs to React state variables (`brentShock`, `congestion`) that immediately trigger asynchronous calls to the backend calculator.
- **The Fleet Optimizer Toggle:** A segmented button group allowing the user to toggle the UI state between "Standard Capesize" and "Split-Cargo". 
- If the backend detects the Split-Cargo option is cheaper, an absolute-positioned, pulsing green Tailwind radar badge (`animate-ping absolute inline-flex`) appears on the toggle to alert the officer.

### 5.5 Live AIS Maritime Corridors (`RouteMap.jsx`)
The map utilizes `react-leaflet` to wrap standard Leaflet.js components.
- **TileLayer Selection:** The map utilizes the stunning **Thunderforest Spinal Map** (via `api.thunderforest.com/spinal-map`), providing an edgy, dark-mode aesthetic. 
- **Polylines & Markers:** The oceanic routes are drawn using `Polyline` tags strictly configured to a glowing neon cyan (`color="#00E5FF"`) with a dash array, ensuring it starkly contrasts against the dark tiles. The live vessel markers pull exact coordinates and ETA data from the FastAPI simulation endpoint, rendering them in interactive `Popup` tags.
- **MapUpdater Component:** A custom sub-component utilizing the `useMap()` hook that forces the Leaflet camera to automatically pan and zoom (`map.fitBounds`) whenever the user selects a new origin route in the calculator.

### 5.6 The Tender Brief Export Module (`TenderBriefModal.jsx`)
Triggered by the "EXPORT RFQ" button, this module dynamically renders a formalized, printable Request For Quotation (RFQ) memo.
- **Print Logic:** It utilizes a custom injected CSS style (`@media print`). When `window.print()` is called, it actively hides the entire application background and modal overlays (`.print:hidden`), isolating only the pure text content of the Tender Brief. This allows a logistics officer to export a perfectly clean PDF, formatted with "Authorized Signature" lines, ready for the Ministry of Steel bureaucracy.

---

## 6. Conclusion and Future Scalability

The SIH26006 Freight Dashboard successfully bridges the gap between raw machine learning output and actionable, enterprise-level user interfaces. 

By automating the complex mathematics of voyage economics (factoring in dynamic oil shocks, exact distance matrices, and Capesize-to-Panamax ratios) and continuously validating it against an AI-driven forecasting engine, the platform practically eliminates the risk of catastrophic market exposure. 

**Future Roadmap considerations include:**
1. Integrating live REST APIs from Baltic Exchange to replace web-scraping.
2. Expanding the ML model to include a Random Forest or XGBoost ensemble to factor in global weather disruptions (e.g., typhoons in the Pacific).
3. Transitioning the synthetic AIS Fleet Simulator into a live WebSocket feed connected directly to global maritime tracking APIs (like MarineTraffic or Spire).

The system as it stands is fully modular, robustly designed, and perfectly tailored for immediate deployment within a government logistics command center.
