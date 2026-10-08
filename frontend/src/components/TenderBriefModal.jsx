import React from 'react';
import { X, Printer } from 'lucide-react';

export default function TenderBriefModal({ isOpen, onClose, routeId, payloadMt, spotRate, projectedRate, recommendation, maxCeilingBid }) {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const tenderToken = `MOS/BULK/2026/09-${Math.floor(1000 + Math.random() * 9000)}`;
  const dateStr = new Intl.DateTimeFormat('en-US', { dateStyle: 'long' }).format(new Date());

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm print:bg-white print:backdrop-blur-none p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[90vh] print:shadow-none print:w-full print:max-w-none print:h-full print:max-h-none print:rounded-none">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-slate-200 print:hidden">
          <h2 className="text-lg font-bold text-slate-800">Export Tender Brief</h2>
          <div className="flex items-center gap-2">
            <button onClick={handlePrint} className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg">
              <Printer className="w-5 h-5" />
            </button>
            <button onClick={onClose} className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Content */}
        <div className="p-8 overflow-y-auto print:p-0 print:overflow-visible text-slate-900 font-serif print-content">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-black uppercase tracking-widest border-b-2 border-slate-900 inline-block pb-1">Government of India</h1>
            <h2 className="text-xl font-bold uppercase mt-2">Ministry of Steel</h2>
            <p className="text-sm font-semibold mt-1">Bulk Cargo Procurement & Vessel Chartering</p>
          </div>

          <div className="flex justify-between mb-8 text-sm font-medium">
            <div>
              <p><strong>Reference ID:</strong> {tenderToken}</p>
              <p><strong>Date:</strong> {dateStr}</p>
            </div>
            <div className="text-right">
              <p><strong>Department:</strong> Logistics & Supply Chain</p>
              <p><strong>Classification:</strong> CONFIDENTIAL</p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-bold border-b border-slate-300 mb-2 uppercase">1. Consignment Details</h3>
            <table className="w-full text-left text-sm mb-4">
              <tbody>
                <tr className="border-b border-slate-100"><th className="py-2 w-1/3">Route Corridor</th><td className="py-2">{routeId} to East Coast India</td></tr>
                <tr className="border-b border-slate-100"><th className="py-2">Total Tonnage</th><td className="py-2">{payloadMt.toLocaleString()} MT</td></tr>
              </tbody>
            </table>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-bold border-b border-slate-300 mb-2 uppercase">2. Algorithmic Guidance & Market Data</h3>
            <table className="w-full text-left text-sm">
              <tbody>
                <tr className="border-b border-slate-100"><th className="py-2 w-1/3">Current Spot Rate</th><td className="py-2 font-mono">${spotRate.toLocaleString()} / day</td></tr>
                <tr className="border-b border-slate-100"><th className="py-2">30-Day Projected Rate</th><td className="py-2 font-mono">${projectedRate.toLocaleString()} / day</td></tr>
                <tr className="border-b border-slate-100"><th className="py-2 text-indigo-700">Max Ceiling Bid (Landed)</th><td className="py-2 font-bold text-lg font-mono">${maxCeilingBid.toFixed(2)} / MT</td></tr>
              </tbody>
            </table>
          </div>

          <div className="mb-12">
            <h3 className="text-lg font-bold border-b border-slate-300 mb-2 uppercase">3. Strategic Directive</h3>
            <div className="p-4 bg-slate-50 border border-slate-200 print:bg-white print:border-slate-400">
              <p className="font-bold text-lg">{recommendation}</p>
              <p className="text-sm mt-2">The algorithmic optimization engine mandates the above strategy to mitigate market exposure and optimize landed freight costs.</p>
            </div>
          </div>

          <div className="flex justify-between items-end pt-12">
            <div className="w-48 border-t border-slate-800 text-center pt-2 text-sm font-bold">
              Authorized Signature
            </div>
            <div className="w-48 border-t border-slate-800 text-center pt-2 text-sm font-bold">
              Official Seal
            </div>
          </div>
        </div>
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          body * {
            visibility: hidden;
          }
          .print-content, .print-content * {
            visibility: visible;
          }
          .print-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
        }
      `}} />
    </div>
  );
}
