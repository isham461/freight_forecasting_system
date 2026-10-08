import React from 'react';
import { Briefcase, TrendingUp, TrendingDown, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function ProcurementStrategy({ strategyData }) {
  if (!strategyData) return null;

  const { spot_economics, tc_economics, delta_total_cost, recommendation, exposure_desc } = strategyData;
  const isSurging = recommendation === "LOCK 3-MONTH TIME CHARTER";
  const isDropping = recommendation === "DELAY SPOT CHARTER";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col h-full">
      <div className="flex items-center space-x-2 mb-6 border-b border-slate-100 pb-3">
        <Briefcase className="w-5 h-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-slate-800">Charter Strategy Analysis</h3>
      </div>

      <div className="flex-grow flex flex-col justify-between">
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className={`p-4 rounded-lg border ${!isSurging && !isDropping ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-slate-50'}`}>
            <h4 className="text-sm font-semibold text-slate-700 mb-1">Single Spot Voyage</h4>
            <p className="text-2xl font-bold text-slate-900">${spot_economics.landed_freight_cost_per_mt.toFixed(2)}<span className="text-sm font-medium text-slate-500">/MT</span></p>
            <p className="text-xs text-slate-500 mt-1">Total: ${spot_economics.total_voyage_cost.toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
          </div>
          
          <div className={`p-4 rounded-lg border ${isSurging ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200 bg-slate-50'}`}>
            <h4 className="text-sm font-semibold text-slate-700 mb-1">3-Month Term Contract</h4>
            <p className="text-2xl font-bold text-slate-900">${tc_economics.landed_freight_cost_per_mt.toFixed(2)}<span className="text-sm font-medium text-slate-500">/MT</span></p>
            <p className="text-xs text-slate-500 mt-1">Total: ${tc_economics.total_voyage_cost.toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Total Financial Exposure</h4>
          <div className={`flex items-start space-x-3 p-4 rounded-lg border ${isSurging ? 'bg-rose-50 border-rose-200 text-rose-800' : isDropping ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-slate-50 border-slate-200 text-slate-700'}`}>
            {isSurging ? <TrendingUp className="w-5 h-5 mt-0.5 flex-shrink-0" /> : isDropping ? <TrendingDown className="w-5 h-5 mt-0.5 flex-shrink-0" /> : <ShieldCheck className="w-5 h-5 mt-0.5 flex-shrink-0" />}
            <p className="text-sm leading-relaxed">{exposure_desc}</p>
          </div>
        </div>


      </div>
    </div>
  );
}
