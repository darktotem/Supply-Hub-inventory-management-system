
import { useState } from "react";

const icons = {
  Dashboard: "▦",
  Inventory: "▤",
  Suppliers: "♧",
  "Purchase Orders": "▣",
  Deliveries: "⇄",
  Sales: "↗",
  Customers: "♙",
  Invoices: "▧",
  Payments: "◇",
  Employees: "♧",
  "Audit Logs": "◷",
  Settings: "⚙",
};

export function Navbar({ links = [], activePath, onNavigate }) {
  const [currentPath, setCurrentPath] = useState(activePath || "#dashboard");

  function handleNavigation(path) {
    setCurrentPath(path);
    onNavigate?.(path);
  }

  return (
    <aside className="flex min-h-screen w-[260px] shrink-0 flex-col bg-[#111c2e] px-4 py-6 text-slate-300">
      {/* Brand */}
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500 text-sm font-bold text-white">
          SH
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-wide text-white">
            Supply Hub
          </h2>
          <p className="text-xs text-slate-400">Management System</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        <p className="mb-4 px-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Main Menu
        </p>

        {links.map((link) => {
          const isActive = (activePath || currentPath) === link.path;

          return (
            <a
              key={link.path}
              href={link.path}
              onClick={() => handleNavigation(link.path)}
              className={`group flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-emerald-500 text-white shadow-lg shadow-emerald-950/20"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <span className="flex w-6 justify-center text-lg">
                {icons[link.label] || "○"}
              </span>
              <span>{link.label}</span>
            </a>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-8 border-t border-slate-700 pt-5">
        <p className="px-3 text-xs text-slate-500">
          Supply Hub © 2026
        </p>
      </div>
    </aside>
  );
}
