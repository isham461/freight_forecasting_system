import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Ship, AlertTriangle, FileText } from 'lucide-react';
import ForecastChart from './components/ForecastChart';
import RouteCalculator from './components/RouteCalculator';
import ProcurementStrategy from './components/ProcurementStrategy';
import RouteMap from './components/RouteMap';
import TenderBriefModal from './components/TenderBriefModal';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

function App() {
  const [routes, setRoutes] = useState({});
  const [historical, setHistorical] = useState([]);
  const [latestFeatures, setLatestFeatures] = useState(null);
  const [forecasts, setForecasts] = useState(null);
  const [chartData, setChartData] = useState([]);

  // Calculator State
  const [selectedRoute, setSelectedRoute] = useState('');
  const [brentShock, setBrentShock] = useState(0);
  const [congestion, setCongestion] = useState(0);
  
  const [strategy, setStrategy] = useState(null);
  const [splitCargoData, setSplitCargoData] = useState(null);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    // Initial Data Fetch
    const fetchData = async () => {
      try {
        const routeRes = await axios.get(`${API_BASE}/logistics/routes`);
        setRoutes(routeRes.data.routes);
        setSelectedRoute(Object.keys(routeRes.data.routes)[0]);

        const histRes = await axios.get(`${API_BASE}/rates/historical`);
        const histData = histRes.data;
        setHistorical(histData);
        
        if (histData.length > 0) {
          const latest = histData[histData.length - 1];
          setLatestFeatures(latest);
          
          const forecastRes = await axios.post(`${API_BASE}/rates/forecast`, latest);
          setForecasts(forecastRes.data.forecasts);
          
          // Build Chart Data
          const recentHist = histData.slice(-60);
          const cData = recentHist.map(d => ({
            name: new Date(d.Date).toLocaleDateString(undefined, {month: 'short', day: 'numeric'}),
            actual: d.Capesize_Price,
            forecast: null
          }));
          
          const lastPoint = { ...cData[cData.length - 1] };
          lastPoint.forecast = lastPoint.actual;
          cData[cData.length - 1] = lastPoint;
          
          cData.push({ name: '+7 Days', actual: null, forecast: forecastRes.data.forecasts['7-Day'] });
          cData.push({ name: '+14 Days', actual: null, forecast: forecastRes.data.forecasts['14-Day'] });
          cData.push({ name: '+30 Days', actual: null, forecast: forecastRes.data.forecasts['30-Day'] });
          
          setChartData(cData);
        }
      } catch (err) {
        console.error("Failed to load initial data", err);
      }
    };
    fetchData();
  }, []);

  // Update calculator when inputs change
  useEffect(() => {
    if (!latestFeatures || !forecasts || !selectedRoute) return;

    const calcVoyage = async () => {
      try {
        const payload = {
          route_id: selectedRoute,
          custom_spot_rate: latestFeatures.Capesize_Price,
          forecasted_30d_rate: forecasts['30-Day'],
          brent_crude_usd: latestFeatures.Brent_Close,
          brent_shock_pct: brentShock,
          congestion_days: congestion
        };
        const [voyageRes, splitRes] = await Promise.all([
          axios.post(`${API_BASE}/logistics/voyage-calculator`, payload),
          axios.post(`${API_BASE}/logistics/split-cargo-eval`, payload)
        ]);
        
        setStrategy(voyageRes.data);
        setSplitCargoData(splitRes.data);
      } catch (err) {
        console.error("Failed to calculate voyage", err);
      }
    };
    calcVoyage();
  }, [selectedRoute, brentShock, congestion, latestFeatures, forecasts]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <header className="bg-indigo-900 text-white shadow-md border-b border-indigo-800 print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <div className="flex items-center space-x-3 mb-2 sm:mb-0">
            <Ship className="w-8 h-8 text-indigo-400" />
            <div>
              <h1 className="text-xl font-bold tracking-tight">Bulk Cargo Procurement <span className="font-light text-indigo-300">& Vessel Chartering</span></h1>
              <p className="text-xs text-indigo-200 font-medium tracking-wide">ROUTE OPTIMIZATION: OVERSEAS TO EAST COAST INDIA (ECI)</p>
            </div>
          </div>
          <div className="flex flex-col items-end">
            <div className="text-sm font-medium text-indigo-200 bg-indigo-800 px-3 py-1 rounded-full border border-indigo-700 mb-1">
              Live Market Data Active
            </div>
            <div className="text-xs text-indigo-300 pr-2">
              {new Intl.DateTimeFormat('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).format(new Date())}
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {latestFeatures && forecasts && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <p className="text-sm font-medium text-slate-500 mb-1">Current Spot Rate</p>
              <h2 className="text-3xl font-bold text-slate-900">${latestFeatures.Capesize_Price.toLocaleString()}<span className="text-sm text-slate-500 font-medium">/day</span></h2>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <p className="text-sm font-medium text-slate-500 mb-1">30-Day Projected Rate</p>
              {(() => {
                const projDelta = ((forecasts['30-Day'] - latestFeatures.Capesize_Price) / latestFeatures.Capesize_Price) * 100;
                const isSurgingRate = projDelta > 0;
                return (
                  <div className="flex items-end gap-3">
                    <h2 className="text-3xl font-bold text-indigo-600">${forecasts['30-Day'].toLocaleString('en-US', {maximumFractionDigits:0})}<span className="text-sm text-slate-500 font-medium">/day</span></h2>
                    <div className={`px-2 py-1 mb-1 rounded-md text-xs font-bold ${isSurgingRate ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                      {isSurgingRate ? '+' : ''}{projDelta.toFixed(1)}%
                    </div>
                  </div>
                );
              })()}
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <p className="text-sm font-medium text-slate-500 mb-1">Brent Crude Index</p>
              <h2 className="text-3xl font-bold text-slate-900">${latestFeatures.Brent_Close.toLocaleString()}<span className="text-sm text-slate-500 font-medium">/bbl</span></h2>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-center relative">
              <div className="flex justify-between items-center mb-2">
                <p className="text-sm font-medium text-slate-500">Operations Directive</p>
                <button 
                  onClick={() => setIsModalOpen(true)}
                  className="text-indigo-600 hover:text-indigo-800 flex items-center text-xs font-semibold bg-indigo-50 px-2 py-1 rounded border border-indigo-100"
                  title="Generate Tender Brief"
                >
                  <FileText className="w-3 h-3 mr-1" />
                  EXPORT RFQ
                </button>
              </div>
              {strategy ? (() => {
                const isSurging = strategy.recommendation === "LOCK 3-MONTH TIME CHARTER";
                const isDropping = strategy.recommendation === "DELAY SPOT CHARTER";
                return (
                  <div className={`w-full flex items-center justify-center p-2 rounded-lg font-bold text-[13px] shadow-sm border text-center ${
                    isSurging ? 'bg-rose-600 text-white border-rose-700' : 
                    isDropping ? 'bg-emerald-600 text-white border-emerald-700' : 
                    'bg-indigo-600 text-white border-indigo-700'
                  }`}>
                    {isSurging ? <AlertTriangle className="w-4 h-4 mr-1 flex-shrink-0" /> : null}
                    {strategy.recommendation}
                  </div>
                )
              })() : (
                <div className="w-full flex items-center justify-center p-2 rounded-lg font-bold text-sm bg-slate-100 text-slate-400">
                  CALCULATING...
                </div>
              )}
            </div>
          </div>
        )}

        <ForecastChart data={chartData} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Left Column: Controls & Analysis */}
          <div className="lg:col-span-1 flex flex-col gap-8">
            <RouteCalculator 
              routes={routes} 
              selectedRoute={selectedRoute} 
              onRouteSelect={setSelectedRoute}
              brentShock={brentShock}
              onBrentShockChange={setBrentShock}
              congestion={congestion}
              onCongestionChange={setCongestion}
              splitCargoData={splitCargoData}
            />
            <ProcurementStrategy strategyData={strategy} />
          </div>
          
          {/* Right Column: Massive Map */}
          <div className="lg:col-span-2 h-[600px] lg:h-auto lg:min-h-[700px]">
            <RouteMap selectedRoute={selectedRoute} />
          </div>
        </div>
      </main>

      <TenderBriefModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        routeId={routes[selectedRoute]?.name || selectedRoute}
        payloadMt={routes[selectedRoute]?.payload_mt || 160000}
        spotRate={latestFeatures?.Capesize_Price || 0}
        projectedRate={forecasts?.['30-Day'] || 0}
        recommendation={strategy?.recommendation || ''}
        maxCeilingBid={splitCargoData?.capesize?.landed_cost_per_mt || 0}
      />
    </div>
  );
}

export default App;
