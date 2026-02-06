import React, { useState } from 'react';
import { LayoutDashboard, Shield, Menu, UserCircle, Bell, Siren, BrainCircuit, ChevronLeft, ChevronRight } from 'lucide-react';
import { AlertList } from './components/AlertList';
import { TriageStation } from './components/TriageStation';
import { ViewState } from './types';

export default function App() {
  const [currentView, setCurrentView] = useState<ViewState>('alert-list');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const NavItem = ({ view, icon: Icon, label }: { view: ViewState, icon: any, label: string }) => (
    <button
      onClick={() => setCurrentView(view)}
      className={`relative group flex items-center gap-3 px-4 py-3 border-l-4 transition-all duration-200 overflow-hidden ${
        currentView === view
          ? 'bg-gradient-to-r from-cyan-950/50 to-transparent border-cyan-500 text-cyan-400'
          : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
      } ${sidebarOpen ? '' : 'justify-center'}`}
      title={!sidebarOpen ? label : ''}
    >
      <Icon size={22} className={`flex-shrink-0 transition-transform duration-300 ${!sidebarOpen && currentView === view ? 'scale-110 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]' : ''}`} />
      
      {/* Label with fade transition */}
      <span className={`font-medium tracking-wide whitespace-nowrap transition-all duration-300 ${
        sidebarOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 absolute left-16'
      }`}>
        {label}
      </span>
    </button>
  );

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans flex overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#020617] to-[#020617]">
      
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-20'} flex-shrink-0 bg-[#0f172a]/90 backdrop-blur-xl border-r border-slate-800 flex flex-col transition-[width] duration-300 ease-in-out z-20 relative`}
      >
        {/* Sidebar Toggle Button (Centered) */}
        <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="absolute -right-3 top-1/2 -translate-y-1/2 bg-slate-900 border border-slate-700 text-slate-400 hover:text-cyan-400 rounded-full p-1 shadow-lg z-50 transition-colors"
        >
            {sidebarOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
        </button>

        <div className={`h-16 flex items-center border-b border-slate-800 transition-all duration-300 ${sidebarOpen ? 'px-6' : 'justify-center px-0'}`}>
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)] flex-shrink-0">
             <Shield className="text-white" size={20} fill="currentColor" />
          </div>
          <div className={`ml-3 overflow-hidden transition-all duration-300 ${sidebarOpen ? 'w-32 opacity-100' : 'w-0 opacity-0'}`}>
             <span className="font-bold text-lg tracking-wider text-slate-100 whitespace-nowrap">SAI LAB</span>
          </div>
        </div>

        <div className="flex-1 py-6 space-y-2 overflow-x-hidden">
          <div className={`px-6 mb-4 text-xs font-bold text-slate-500 uppercase tracking-widest transition-opacity duration-300 ${sidebarOpen ? 'opacity-100' : 'opacity-0 hidden'}`}>
            Modules
          </div>
          {/* Divider when closed */}
          {!sidebarOpen && <div className="h-px bg-slate-800 mx-4 mb-4"></div>}

          <NavItem view="alert-list" icon={Siren} label="Alerts" />
          <NavItem view="triage" icon={BrainCircuit} label="Triage" />
        </div>

        <div className="p-4 border-t border-slate-800">
            <div className={`bg-slate-900/50 rounded-lg border border-slate-800 flex items-center transition-all duration-300 ${sidebarOpen ? 'p-3 gap-3' : 'p-2 justify-center'}`}>
                <div className="relative flex-shrink-0">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500"></div>
                    <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping opacity-75"></div>
                </div>
                <div className={`overflow-hidden transition-all duration-300 ${sidebarOpen ? 'w-auto opacity-100' : 'w-0 opacity-0'}`}>
                    <div className="text-xs font-bold text-emerald-500 whitespace-nowrap">SYSTEM ONLINE</div>
                    <div className="text-[10px] text-slate-500 font-mono whitespace-nowrap">v1.0.0</div>
                </div>
            </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Background Grid Decoration */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,0.1)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none"></div>

        {/* Header */}
        <header className="h-16 border-b border-slate-800 bg-[#0f172a]/80 backdrop-blur-md flex items-center justify-between px-8 z-10 sticky top-0">
          {/* Left Side - Clean, specific text removed */}
          <div className="flex items-center gap-4">
             {/* Mobile Menu Toggle (only visible on small screens) */}
             <button onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors">
                 <Menu size={20} />
             </button>
             
             {/* Optional: Breadcrumb or Current Location Indicator */}
             <div className="flex items-center text-sm font-mono text-slate-500">
                <span className="text-slate-600">SAI LAB</span>
                <span className="mx-2">/</span>
                <span className="text-cyan-400 font-semibold tracking-wide uppercase">
                    {currentView === 'alert-list' ? 'Alerts' : 'Triage'}
                </span>
             </div>
          </div>

          <div className="flex items-center gap-6">
             <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-full">
                <span className="w-2 h-2 rounded-full bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></span>
                <span className="text-xs font-mono text-cyan-400">NET_SECURE</span>
             </div>
             
             {/* Bell Notification removed */}

             <div className="w-10 h-10 rounded-full bg-gradient-to-r from-slate-700 to-slate-800 border border-slate-600 flex items-center justify-center text-xs font-bold text-white shadow-lg cursor-pointer hover:border-cyan-500 transition-colors">
                OP
             </div>
          </div>
        </header>

        {/* Content Body */}
        <div className="flex-1 overflow-auto p-6 md:p-8 relative z-0">
           {currentView === 'alert-list' && <AlertList onNavigate={() => setCurrentView('triage')} />}
           {currentView === 'triage' && <TriageStation />}
        </div>
      </main>
    </div>
  );
}