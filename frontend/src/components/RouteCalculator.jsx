import React, { useState } from 'react';
import { Ship, Anchor, Droplets } from 'lucide-react';

export default function RouteCalculator({ routes, selectedRoute, onRouteSelect, brentShock, onBrentShockChange, congestion, onCongestionChange, splitCargoData }) {
  const [fleetType, setFleetType] = useState('capesize');

  const activeEcon = splitCargoData ? splitCargoData[fleetType] : null;
  const isSplitCheaper = splitCargoData?.is_split_cheaper;
  const savings = splitCargoData?.savings_per_mt;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col h-full">
      <div className="flex items-center space-x-2 mb-6 border-b border-slate-100 pb-3">
        <Ship className="w-5 h-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-800">Route Economics Simulator</h3>
      </div>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Import Route (Origin to ECI)</label>
          <select 
            className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5"
            value={selectedRoute}
            onChange={(e) => onRouteSelect(e.target.value)}
          >
            {Object.values(routes).map(r => (
              <option key={r.id} value={r.id}>{r.name} ({r.cargo_type})</option>
            ))}
          </select>
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <label className="text-sm font-medium text-slate-700 flex items-center gap-1">
              <Droplets className="w-4 h-4 text-slate-500" /> Crude Oil Shock (Bunker Impact)
            </label>
            <span className="text-sm text-indigo-600 font-bold">{brentShock > 0 ? '+' : ''}{brentShock}%</span>
          </div>
          <input type="range" min="-30" max="30" value={brentShock} onChange={(e) => onBrentShockChange(parseFloat(e.target.value))} className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600" />
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <label className="text-sm font-medium text-slate-700 flex items-center gap-1">
              <Anchor className="w-4 h-4 text-slate-500" /> Port Congestion Delay
            </label>
            <span className="text-sm text-rose-600 font-bold">+{congestion} Days</span>
          </div>
          <input type="range" min="0" max="15" value={congestion} onChange={(e) => onCongestionChange(parseFloat(e.target.value))} className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-rose-500" />
        </div>

        {/* Fleet Optimizer Toggle */}
        <div className="pt-2">
          <label className="block text-sm font-medium text-slate-700 mb-2">Fleet Optimizer Configuration</label>
          <div className="flex rounded-lg shadow-sm">
            <button
              onClick={() => setFleetType('capesize')}
              className={`flex-1 py-2 text-sm font-medium rounded-l-lg border ${fleetType === 'capesize' ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}`}
            >
              Standard Capesize (160k MT)
            </button>
            <button
              onClick={() => setFleetType('twin_panamax')}
              className={`flex-1 py-2 text-sm font-medium rounded-r-lg border-y border-r relative ${fleetType === 'twin_panamax' ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'}`}
            >
              Split-Cargo (2x Panamax)
              {isSplitCheaper && fleetType !== 'twin_panamax' && (
                <span className="absolute -top-2 -right-2 flex h-4 w-4">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border border-white"></span>
                </span>
              )}
            </button>
          </div>
        </div>
      </div>

      {activeEcon && (
        <div className="mt-8 bg-slate-50 rounded-lg border border-slate-200 p-4 relative">
          {fleetType === 'twin_panamax' && isSplitCheaper && (
            <div className="absolute -top-3 right-4 bg-emerald-100 border border-emerald-200 text-emerald-700 px-3 py-0.5 rounded-full text-xs font-bold shadow-sm">
              Saves ${savings.toFixed(2)} / MT
            </div>
          )}
          <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Voyage Cost Breakdown</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-500">Duration</p>
              <p className="text-lg font-bold text-slate-800">{activeEcon.total_voyage_days} Days</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Bunker Fuel</p>
              <p className="text-lg font-bold text-slate-800">${activeEcon.total_bunker_expense.toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Charter Hire</p>
              <p className="text-lg font-bold text-slate-800">${activeEcon.charter_hire_expense.toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 text-indigo-600 font-bold">Landed Freight</p>
              <p className="text-2xl font-black text-indigo-700">${activeEcon.landed_cost_per_mt.toFixed(2)}<span className="text-sm font-medium">/MT</span></p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
