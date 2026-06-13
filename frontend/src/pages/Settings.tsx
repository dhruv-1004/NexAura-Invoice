import { useState, useEffect } from 'react';
import { Save } from 'lucide-react';
import api from '../services/api';
import './Settings.css';

interface CompanySettings {
  company_name: string;
  address: string;
  email: string;
  phone: string;
  bank_name: string;
  account_holder: string;
  account_number: string;
  ifsc: string;
  upi_id: string;
  footer_note: string;
}

const Settings = () => {
  const [settings, setSettings] = useState<CompanySettings>({
    company_name: '', address: '', email: '', phone: '',
    bank_name: '', account_holder: '', account_number: '',
    ifsc: '', upi_id: '', footer_note: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await api.get('/settings');
        setSettings(response.data);
      } catch (err) {
        console.error('Failed to fetch settings', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setSettings({ ...settings, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      await api.put('/settings', settings);
      setMessage('Settings saved successfully!');
    } catch (err) {
      console.error('Failed to save settings', err);
      setMessage('Failed to save settings.');
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  if (loading) return <div className="loading">Loading settings...</div>;

  return (
    <div className="settings-page">
      <div className="settings-grid">
        <div className="card">
          <div className="card-header">
            <h3>Company Details</h3>
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label className="label">Company Name</label>
              <input name="company_name" value={settings.company_name || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group">
              <label className="label">Email</label>
              <input name="email" type="email" value={settings.email || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group">
              <label className="label">Phone</label>
              <input name="phone" value={settings.phone || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group full-width">
              <label className="label">Address</label>
              <textarea name="address" value={settings.address || ''} onChange={handleChange} className="input-field" rows={3} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Bank & Payment Details</h3>
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label className="label">Bank Name</label>
              <input name="bank_name" value={settings.bank_name || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group">
              <label className="label">Account Holder</label>
              <input name="account_holder" value={settings.account_holder || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group">
              <label className="label">Account Number</label>
              <input name="account_number" value={settings.account_number || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group">
              <label className="label">IFSC Code</label>
              <input name="ifsc" value={settings.ifsc || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group">
              <label className="label">UPI ID</label>
              <input name="upi_id" value={settings.upi_id || ''} onChange={handleChange} className="input-field" />
            </div>
            <div className="form-group full-width">
              <label className="label">Invoice Footer Note</label>
              <textarea name="footer_note" value={settings.footer_note || ''} onChange={handleChange} className="input-field" rows={2} />
            </div>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        {message && <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>{message}</div>}
        <button className="btn-primary flex-center" onClick={handleSave} disabled={saving}>
          <Save size={18} style={{marginRight: '8px'}} />
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default Settings;
