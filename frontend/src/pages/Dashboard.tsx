import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DollarSign, FileText, CheckCircle, Clock } from 'lucide-react';
import api from '../services/api';
import './Dashboard.css';

interface DashboardData {
  monthly_revenue: number;
  weekly_revenue: number;
  total_invoices: number;
  paid_invoices: number;
  pending_invoices: number;
  cancelled_invoices: number;
  top_clients: Array<{ client_name: string; revenue: number }>;
}

const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get('/dashboard/summary');
        setData(response.data);
      } catch (err) {
        console.error('Failed to fetch dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading || !data) return <div className="loading">Loading dashboard...</div>;

  const chartData = data.top_clients.map(c => ({
    name: c.client_name,
    Revenue: c.revenue
  }));

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-icon orange"><DollarSign size={24} /></div>
          <div className="stat-content">
            <p>Monthly Revenue</p>
            <h3>${data.monthly_revenue.toFixed(2)}</h3>
          </div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon dark"><FileText size={24} /></div>
          <div className="stat-content">
            <p>Total Invoices</p>
            <h3>{data.total_invoices}</h3>
          </div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon green"><CheckCircle size={24} /></div>
          <div className="stat-content">
            <p>Paid</p>
            <h3>{data.paid_invoices}</h3>
          </div>
        </div>
        <div className="card stat-card">
          <div className="stat-icon blue"><Clock size={24} /></div>
          <div className="stat-content">
            <p>Pending</p>
            <h3>{data.pending_invoices}</h3>
          </div>
        </div>
      </div>

      <div className="dashboard-row">
        <div className="card chart-card">
          <div className="card-header">
            <h3>Top Clients by Revenue</h3>
          </div>
          <div className="chart-container">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip 
                    cursor={{fill: 'rgba(255, 90, 0, 0.05)'}} 
                    contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}}
                  />
                  <Bar dataKey="Revenue" fill="#FF5A00" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">No revenue data yet</div>
            )}
          </div>
        </div>

        <div className="card recent-card">
          <div className="card-header">
            <h3>Quick Actions</h3>
          </div>
          <div className="action-list">
            <button className="action-item" onClick={() => window.location.href = '/invoices/new'}>
              <div className="action-icon"><FileText size={20} /></div>
              <div className="action-text">Create New Invoice</div>
            </button>
            <button className="action-item" onClick={async () => {
              const res = await api.get('/reports/monthly?format=csv', { responseType: 'blob' });
              const url = window.URL.createObjectURL(new Blob([res.data]));
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', 'monthly_report.csv');
              document.body.appendChild(link);
              link.click();
            }}>
              <div className="action-icon"><DollarSign size={20} /></div>
              <div className="action-text">Download Monthly Report</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
