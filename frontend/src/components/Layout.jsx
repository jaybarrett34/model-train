import { Link, useLocation } from 'react-router-dom';
import {
  FolderKanban,
  Code2,
  Database,
  Sparkles,
  Calculator,
  GraduationCap,
  Download
} from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Projects', icon: FolderKanban },
    { path: '/xml-editor', label: 'XML Editor', icon: Code2 },
    { path: '/generator', label: 'Generator', icon: Sparkles },
    { path: '/datasets', label: 'Datasets', icon: Database },
    { path: '/size-analyzer', label: 'Size Analyzer', icon: Calculator },
    { path: '/training', label: 'Training', icon: GraduationCap },
    { path: '/export', label: 'Export', icon: Download },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-primary-600">Model Trainer</h1>
          <p className="text-sm text-gray-500 mt-1">AI Training Pipeline</p>
        </div>

        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
