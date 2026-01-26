import { useState, useEffect } from 'react'
import './App.css'

interface FormField {
  name: string;
  label: string;
  type: string;
  placeholder: string;
  context: string;
  jobTitle?: string;
  companyName?: string;
}

function App() {
  const [fields, setFields] = useState<FormField[]>([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('System Ready')
  const [backendUrl] = useState('http://localhost:8000')
  const [onboarding, setOnboarding] = useState(false)
  const [userId, setUserId] = useState<string | null>(localStorage.getItem('job_fill_user_id'))
  const [profile, setProfile] = useState<any>(null)

  useEffect(() => {
    if (!userId) {
      const newId = 'user_' + Math.random().toString(36).substr(2, 9);
      setUserId(newId);
      localStorage.setItem('job_fill_user_id', newId);
    }
  }, []);

  useEffect(() => {
    if (userId) {
      fetch(`${backendUrl}/profile`, {
        headers: { 'x-user-id': userId }
      })
        .then(res => res.json())
        .then(data => {
          setProfile(data);
          setOnboarding(false);
        })
        .catch(() => setOnboarding(true));
    }
  }, [userId]);

  const handleCvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !userId) return;

    setLoading(true);
    setStatus('Analyzing Document...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${backendUrl}/onboard/parse-cv`, {
        method: 'POST',
        headers: { 'x-user-id': userId },
        body: formData
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Extraction Failed');
      }
      const data = await res.json();
      setProfile(data);
      setOnboarding(false);
      setStatus('Profile Compiled');
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const scanForm = async () => {
    setStatus('Scanning Interface...')
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    if (tab.id) {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const jobTitle = document.querySelector('h1, h2')?.textContent?.trim() || document.title;
          const companyName =
            (document.querySelector('meta[property="og:site_name"]') as HTMLMetaElement)?.content ||
            document.querySelector('.company-name, .employer-name')?.textContent?.trim() ||
            window.location.hostname.replace('www.', '').split('.')[0].toUpperCase();
          return { jobTitle, companyName };
        }
      }, (results) => {
        const context = results?.[0]?.result as any;
        chrome.tabs.sendMessage(tab.id!, { action: 'SCAN_FORM' }, (response: any) => {
          if (response?.fields) {
            setFields(response.fields.map((f: any) => ({ ...f, ...context })));
            setStatus(`Identified ${response.fields.length} Fields`);
          }
        });
      });
    }
  }

  const autoFill = async () => {
    if (!userId || fields.length === 0) return;
    setLoading(true);
    setStatus('Generating Responses...');

    try {
      const response = await fetch(`${backendUrl}/autofill`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': userId
        },
        body: JSON.stringify({
          fields: fields,
          company_name: fields[0]?.companyName || '',
          job_title: fields[0]?.jobTitle || ''
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'AI Failed');
      }

      const data = await response.json();
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab.id) {
        chrome.tabs.sendMessage(tab.id, { action: 'FILL_FORM', data }, (res: any) => {
          if (res?.success) setStatus('Autofill Applied');
        });
      }
    } catch (error: any) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  if (onboarding) {
    return (
      <div className="container center">
        <h1>Welcome</h1>
        <p className="status">Upload your CV to initialize your professional profile. Our system will extract and structure your credentials.</p>
        <div className="card">
          <label className="file-upload-fancy">
            {loading ? 'Processing Document...' : 'Select PDF Resume'}
            <input type="file" onChange={handleCvUpload} hidden accept=".pdf" disabled={loading} />
          </label>
        </div>
        {loading && <div className="loader-orbit"></div>}
      </div>
    );
  }

  return (
    <div className="container">
      <h1>JobFill Pro</h1>
      <div className="profile-badge">
        <span>User: {profile?.full_name?.split(' ')[0]}</span>
        <button className="text-btn" onClick={() => setOnboarding(true)}>Re-upload</button>
      </div>

      <div className="card">
        <button className="secondary" onClick={scanForm}>Scan Page</button>
        <button onClick={autoFill} disabled={loading || fields.length === 0}>
          {loading ? 'AI Dispatching...' : 'Auto Fill Application'}
        </button>
      </div>

      <p className="status">{status}</p>

      {fields.length > 0 && (
        <div className="field-list">
          <div className="target-info">Entity: <strong>{fields[0].companyName}</strong></div>
          <ul>
            {fields.slice(0, 3).map((f, i) => (
              <li key={i}>{f.label || f.name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
