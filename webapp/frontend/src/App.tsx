import {
  ChevronLeft,
  ChevronRight,
  FolderOpen,
  LayoutDashboard,
  LifeBuoy,
  ScrollText,
  Search,
  Settings,
  Wrench,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Help from "./pages/Help";
import Library from "./pages/Library";
import Logs from "./pages/Logs";
import SettingsPage from "./pages/SettingsPage";
import Sounds from "./pages/Sounds";
import Tools from "./pages/Tools";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/sounds", label: "Sounds", icon: Search, end: false },
  { to: "/library", label: "Library", icon: FolderOpen, end: false },
  { to: "/tools", label: "Tools", icon: Wrench, end: false },
  { to: "/logs", label: "Logs", icon: ScrollText, end: false },
  { to: "/settings", label: "Settings", icon: Settings, end: false },
  { to: "/help", label: "Help", icon: LifeBuoy, end: false },
];

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  const check = useCallback(() => {
    fetch("/api/health")
      .then((r) => setBackendOk(r.ok))
      .catch(() => setBackendOk(false));
  }, []);

  useEffect(() => {
    check();
  }, [check]);

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-100">
      <aside
        className={`flex flex-col border-r border-zinc-800 bg-zinc-900 transition-all ${collapsed ? "w-16" : "w-56"}`}
      >
        <div className="flex items-center justify-between p-3">
          {!collapsed && (
            <span className="text-sm font-bold" data-testid="app-logo">
              sfx-mcp
            </span>
          )}
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            className="rounded p-1 hover:bg-zinc-800"
            aria-label="Toggle sidebar"
            data-testid="sidebar-toggle"
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>
        <div className="flex items-center gap-2 px-3 pb-3 text-xs text-zinc-400">
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              backendOk === null ? "bg-zinc-500" : backendOk ? "bg-green-500" : "bg-red-500"
            }`}
            data-testid="backend-health-dot"
            title={backendOk ? "Backend reachable" : "Backend unreachable"}
          />
          {!collapsed && <span>{backendOk ? "Backend up" : "Backend down"}</span>}
        </div>
        <nav className="flex flex-col gap-1 p-2">
          {NAV.map((item) => (
            <NavLink
              key={item.to + item.label}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded px-3 py-2 text-sm hover:bg-zinc-800 ${
                  isActive ? "bg-zinc-800 text-white" : "text-zinc-400"
                }`
              }
            >
              <item.icon size={18} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sounds" element={<Sounds />} />
          <Route path="/library" element={<Library />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/help" element={<Help />} />
        </Routes>
      </main>
    </div>
  );
}
