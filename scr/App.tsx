import React, { useState, useEffect, useCallback } from 'react';
import { Search, Database, Download, AlertCircle, Clock, ChevronLeft, ChevronRight, Filter, Table as TableIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import axios from 'axios';

interface DatasetState {
  rows: any[];
  total: number;
  columns: string[];
  loading: boolean;
  error: string | null;
  duration: number;
  page: number;
  limit: number;
}

export default function App() {
  const [state, setState] = useState<DatasetState>({
    rows: [],
    total: 0,
    columns: [],
    loading: false,
    error: null,
    duration: 0,
    page: 0,
    limit: 25,
  });

  const [searchInputs, setSearchInputs] = useState({
    mobile: '',
  });

  const buildQuery = () => {
    if (!searchInputs.mobile) return '';
    // Casting mobile to VARCHAR to ensure LIKE works even if inferred as BIGINT
    return `CAST(mobile AS VARCHAR) LIKE '%${searchInputs.mobile}%'`;
  };

  const fetchData = useCallback(async (isSearch = false) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const activeQuery = buildQuery();
      const response = await axios.post('/api/search', {
        query: activeQuery,
        limit: state.limit,
        offset: isSearch ? 0 : state.page * state.limit
      });

      setState(prev => ({
        ...prev,
        rows: response.data.rows,
        total: response.data.total,
        columns: response.data.columns,
        duration: response.data.duration,
        loading: false,
        page: isSearch ? 0 : prev.page
      }));
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Database is initializing, please try again in a moment...';
      setState(prev => ({
        ...prev,
        error: errorMsg,
        loading: false
      }));
      
      // Auto retry once if it's a connection error
      if (!isSearch && errorMsg.includes('initializing')) {
        setTimeout(() => fetchData(), 3000);
      }
    }
  }, [state.page, state.limit, searchInputs]);

  useEffect(() => {
    fetchData();
  }, [state.page]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Database className="text-white size-5" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">Paytm Mobile Search</h1>
          </div>
          
          <div className="flex items-center gap-4">
            {state.duration > 0 && (
              <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
                <Clock className="size-3" />
                Query: {state.duration}ms
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid gap-6">
          {/* Main Controls */}
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
            <div className="max-w-xl mx-auto w-full space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-bold text-slate-500 uppercase tracking-wider block text-center">Enter Mobile Number to Search</label>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 size-5" />
                  <input
                    type="text"
                    placeholder="e.g. 976604..."
                    className="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none text-lg transition-all"
                    value={searchInputs.mobile}
                    onChange={(e) => setSearchInputs({ mobile: e.target.value })}
                    onKeyDown={(e) => e.key === 'Enter' && fetchData(true)}
                  />
                </div>
              </div>

              <button
                onClick={() => fetchData(true)}
                className="w-full py-4 bg-blue-600 text-white rounded-2xl text-lg font-bold hover:bg-blue-700 transition-all shadow-xl shadow-blue-200 active:scale-[0.98]"
              >
                Search Now
              </button>
            </div>
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {state.error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-start gap-3"
              >
                <AlertCircle className="size-5 shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-bold">Error encountered</p>
                  <p className="opacity-90">{state.error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Table Container */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden min-h-[400px] flex flex-col relative">
            {state.loading && (
              <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] z-10 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3">
                  <div className="size-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <p className="text-sm font-medium text-slate-600">Searching...</p>
                </div>
              </div>
            )}

            <div className="overflow-x-auto flex-1">
              <table className="w-full text-left border-collapse min-w-[800px]">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    {state.columns.map(col => (
                      <th key={col} className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {state.rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                      {state.columns.map(col => (
                        <td key={`${idx}-${col}`} className="px-6 py-3.5 text-sm text-slate-600">
                          <div className="max-w-[300px] truncate group relative">
                            {String(row[col])}
                            <div className="hidden group-hover:block absolute left-0 top-full mt-1 p-2 bg-slate-900 text-white text-xs rounded shadow-xl z-20 max-w-md break-words">
                              {String(row[col])}
                            </div>
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {state.rows.length > 0 && (
                <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-center items-center gap-4">
                  <button
                    onClick={() => setState(prev => ({ ...prev, page: Math.max(0, prev.page - 1) }))}
                    disabled={state.page === 0 || state.loading}
                    className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium hover:bg-slate-50 disabled:opacity-30"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-slate-500 font-medium">Page {state.page + 1}</span>
                  <button
                    onClick={() => setState(prev => ({ ...prev, page: prev.page + 1 }))}
                    disabled={state.rows.length < state.limit || state.loading}
                    className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium hover:bg-slate-50 disabled:opacity-30"
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-slate-400 text-xs border-t border-slate-200 mt-12">
        Powered by DuckDB & Paytm Explorer • Supports 7M+ Rows
      </footer>
    </div>
  );
}
