import { useState, useEffect } from 'react';
import { Download, Archive } from 'lucide-react';
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
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div className="loading">Loading invoices...</div>;

  return (
    <div className="invoices-page">
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
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center empty-cell">No invoices found. Create one!</td>
                </tr>
              ) : (
                invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td className="font-medium">{inv.invoice_number}</td>
                    <td>{inv.client_name}</td>
                    <td>{new Date(inv.issue_date).toLocaleDateString()}</td>
                    <td className="font-medium">${inv.grand_total.toFixed(2)}</td>
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
