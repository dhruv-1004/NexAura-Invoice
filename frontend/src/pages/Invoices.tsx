import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Download, Archive, Filter } from 'lucide-react';
import api from '../services/api';
import './Invoices.css';

interface Invoice {
  id: string;
  invoice_number: string;
  client_name: string;
  issue_date: string;
  grand_total: number;
  status: string;
}

const Invoices = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  const filterStatus = searchParams.get('status') || 'All';

  const fetchInvoices = async () => {
    try {
      const response = await api.get('/invoices/');
      setInvoices(response.data);
    } catch (err) {
      console.error('Failed to fetch invoices', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleDownload = async (id: string, number: string) => {
    try {
      const response = await api.get(`/invoices/${id}/pdf`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${number}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error('Failed to download PDF', err);
    }
  };

  const handleArchive = async (id: string) => {
    if (window.confirm('Are you sure you want to archive this invoice?')) {
      try {
        await api.patch(`/invoices/${id}/archive`);
        fetchInvoices();
      } catch (err) {
        console.error('Failed to archive invoice', err);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Paid': return 'status-paid';
      case 'Pending':
      case 'Sent': return 'status-pending';
      case 'Draft': return 'status-draft';
      case 'Cancelled':
      case 'Archived': return 'status-cancelled';
      default: return 'status-draft';
    }
  };

  const filteredInvoices = filterStatus === 'All' 
    ? invoices 
    : invoices.filter(inv => inv.status === filterStatus);

  if (loading) return <div className="loading">Loading invoices...</div>;

  return (
    <div className="invoices-page">
      <div className="card" style={{ marginBottom: '20px', padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>Invoice List</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Filter size={18} style={{ color: 'var(--text-secondary)' }} />
          <select 
            value={filterStatus} 
            onChange={(e) => setSearchParams(e.target.value === 'All' ? {} : { status: e.target.value })}
            style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--border-color)', outline: 'none' }}
          >
            <option value="All">All Statuses</option>
            <option value="Paid">Paid</option>
            <option value="Pending">Pending</option>
            <option value="Draft">Draft</option>
            <option value="Sent">Sent</option>
            <option value="Cancelled">Cancelled</option>
            <option value="Archived">Archived</option>
          </select>
        </div>
      </div>

      <div className="card">
        <div className="table-responsive">
          <table className="invoice-table">
            <thead>
              <tr>
                <th>Invoice No</th>
                <th>Client</th>
                <th>Issue Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredInvoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center empty-cell">
                    {filterStatus === 'All' ? 'No invoices found. Create one!' : `No ${filterStatus} invoices found.`}
                  </td>
                </tr>
              ) : (
                filteredInvoices.map((inv) => (
                  <tr key={inv.id}>
                    <td className="font-medium">{inv.invoice_number}</td>
                    <td>{inv.client_name}</td>
                    <td>{new Date(inv.issue_date).toLocaleDateString()}</td>
                    <td className="font-medium">₹{Number(inv.grand_total).toFixed(2)}</td>
                    <td>
                      <span className={`status-chip ${getStatusColor(inv.status)}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button 
                        className="icon-btn" 
                        onClick={() => handleDownload(inv.id, inv.invoice_number)}
                        title="Download PDF"
                      >
                        <Download size={18} />
                      </button>
                      <button 
                        className="icon-btn danger" 
                        onClick={() => handleArchive(inv.id)}
                        title="Archive"
                      >
                        <Archive size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Invoices;
