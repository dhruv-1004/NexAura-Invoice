import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LayoutDashboard, FileText, Settings, LogOut, PlusCircle } from 'lucide-react';
import './Layout.css';

const Layout = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/invoices', label: 'Invoices', icon: <FileText size={20} /> },
    { path: '/settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="layout-container">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/LOGO.jpeg" alt="Logo" className="brand-logo-img" />
          <h2>NexAura</h2>
        </div>
        
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link 
              key={item.path} 
              to={item.path} 
              className={`nav-item ${location.pathname.startsWith(item.path) ? 'active' : ''}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item logout-btn" onClick={handleLogout}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="main-header">
          <div className="header-content">
            <div className="header-title">
              {navItems.find(item => location.pathname.startsWith(item.path))?.label || 'Invoice System'}
            </div>
            {location.pathname === '/invoices' && (
              <Link to="/invoices/new" className="btn-primary create-btn">
                <PlusCircle size={18} />
                New Invoice
              </Link>
            )}
          </div>
        </header>
        
        <div className="content-wrapper animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
