import { useState, useEffect } from 'react'
import './App.css'
import Questionnaire from './components/Questionnaire'

interface FormField {
  id: string;
  name: string;
  label: string;
  type: string;
  placeholder: string;
  context: string;
  options?: string[];
  jobTitle?: string;
  companyName?: string;
}

function App() {
  const [fields, setFields] = useState<FormField[]>([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('Ready to fill applications')
  const [backendUrl] = useState(import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000')
  const [showQuestionnaire, setShowQuestionnaire] = useState(false)
  const [hasProfile, setHasProfile] = useState(false)
  const [userId] = useState<string>(() => {
    let id = localStorage.getItem('jobfill_user_id')
    if (!id) {
      id = 'user_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('jobfill_user_id', id)
    }
    return id
  })

  useEffect(() => {
    checkProfile();
  }, []);

  const checkProfile = async () => {
    try {
      const res = await fetch(`${backendUrl}/profile`, { headers: { 'x-user-id': userId } });
      if (res.ok) {
        const data = await res.json();
        setHasProfile(data.completed_onboarding);
      }
    } catch (e) {
      setHasProfile(false);
    }
  }

  const handleQuestionnaireComplete = () => {
    setShowQuestionnaire(false);
    setHasProfile(true);
    setStatus('Profile complete! Ready to fill applications.');
  }

  const scanForm = async () => {
    setFields([]);
    setStatus('Scanning page...');
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
      if (!tab?.id) return;

      // Use scripting.executeScript to run the scan in ALL frames at once.
      // This is more robust for cross-origin frames than manual messaging.
      const scanResults = await chrome.scripting.executeScript({
        target: { tabId: tab.id, allFrames: true },
        func: () => {
          // Inner function to find labels (simplified version of content script logic)
          const findLabel = (input: HTMLElement) => {
            const ariaLabel = input.getAttribute('aria-label');
            if (ariaLabel) return ariaLabel;

            const labelledBy = input.getAttribute('aria-labelledby');
            if (labelledBy) {
              const labels = labelledBy.split(' ').map(id => document.getElementById(id)?.innerText).filter(Boolean);
              if (labels.length > 0) return labels.join(' ').trim();
            }

            if (input.id) {
              const labelEl = document.querySelector(`label[for="${input.id}"]`) as HTMLElement;
              if (labelEl) return labelEl.innerText.trim();
            }
            const nestedLabel = input.closest('label');
            if (nestedLabel) return nestedLabel.innerText.trim();

            const parent = input.parentElement;
            if (parent && parent.innerText.length > 5 && parent.innerText.length < 200) {
              return parent.innerText.split('\n')[0].trim();
            }
            return "";
          };

          const selectors = ['input:not([type="hidden"]):not([type="submit"]):not([type="button"])', 'textarea', 'select'];
          const elements = Array.from(document.querySelectorAll(selectors.join(',')));

          return elements.map(el => {
            const input = el as HTMLInputElement;
            const parent = input.closest('div, section, .form-group, .field, fieldset') as HTMLElement;
            return {
              id: input.id || input.getAttribute('name') || 'gen_' + Math.random().toString(36).substr(2, 5),
              name: input.getAttribute('name') || "",
              label: findLabel(input),
              placeholder: input.placeholder || "",
              type: input.type || 'text',
              context: parent?.innerText?.substring(0, 500).replace(/\s+/g, ' ').trim() || "",
              options: input.tagName === 'SELECT' ? Array.from((el as HTMLSelectElement).options).map(o => o.text) : []
            };
          }).filter(f => f.label || f.placeholder || f.context.length > 10);
        }
      });

      // Get metadata from main frame
      const meta = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => ({
          company: document.querySelector('.company-name, [class*="company"]')?.textContent?.trim() || window.location.hostname,
          job: document.querySelector('h1, h2')?.textContent?.trim() || document.title
        })
      });

      const companyName = (meta[0].result as any)?.company || "Unknown";
      const jobTitle = (meta[0].result as any)?.job || "Role";

      const allFields = scanResults
        .flatMap(r => r.result as any[])
        .map(f => ({ ...f, companyName, jobTitle }));

      // De-duplicate fields by label/context to handle overlap
      const uniqueFields = allFields.filter((f, index, self) =>
        index === self.findIndex((t) => t.label === f.label && t.type === f.type)
      );

      setFields(uniqueFields);
      setStatus(`Detected ${uniqueFields.length} fields`);
    } catch (error: any) {
      console.error(error);
      setStatus('Scan failed: ' + error.message);
    }
  }

  const autoFill = async () => {
    if (fields.length === 0) return;
    setLoading(true);
    setStatus('Matching your data...');

    try {
      const res = await fetch(`${backendUrl}/autofill`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': userId },
        body: JSON.stringify({
          fields,
          company_name: fields[0]?.companyName || "Unknown",
          job_title: fields[0]?.jobTitle || "Role"
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        const detail = errData.detail;
        const msg = Array.isArray(detail)
          ? detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ')
          : (typeof detail === 'object' ? JSON.stringify(detail) : detail);
        throw new Error(msg || 'Failed to match fields');
      }

      const { mappings, missing_fields } = await res.json();

      if (missing_fields && missing_fields.length > 0 && Object.keys(mappings).length === 0) {
        setStatus(`Could not match any fields. Try updating your profile.`);
        return;
      }

      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) return;

      // Use scripting.executeScript to fill ALL frames.
      const fillResults = await chrome.scripting.executeScript({
        target: { tabId: tab.id, allFrames: true },
        args: [mappings],
        func: (data: Record<string, any>) => {
          let count = 0;

          // Re-use findLabel helper for identification
          const findLabel = (input: HTMLElement) => {
            return input.getAttribute('aria-label') ||
              (document.querySelector(`label[for="${input.id}"]`) as HTMLElement)?.innerText ||
              input.closest('label')?.innerText || "";
          };

          for (const [id, value] of Object.entries(data)) {
            const input = document.getElementById(id) ||
              document.getElementsByName(id)[0] ||
              document.querySelector(`[name="${id}"], [id="${id}"]`);

            if (!input) continue;
            const valStr = String(value).toLowerCase();

            try {
              if (input instanceof HTMLSelectElement) {
                const option = Array.from(input.options).find(o =>
                  o.text.toLowerCase().includes(valStr) || o.value.toLowerCase().includes(valStr)
                );
                if (option) {
                  input.value = option.value;
                  input.dispatchEvent(new Event('change', { bubbles: true }));
                  count++;
                }
              }
              else if (input instanceof HTMLInputElement && input.type === 'radio') {
                const group = document.querySelectorAll(`input[name="${input.name}"]`);
                group.forEach(r => {
                  const radio = r as HTMLInputElement;
                  const labelText = findLabel(radio).toLowerCase();
                  if (labelText.includes(valStr) || radio.value.toLowerCase() === valStr) {
                    radio.click();
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                    count++;
                  }
                });
              }
              else {
                const el = input as HTMLInputElement;
                el.focus();
                el.value = value as string;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
                count++;
              }
            } catch (e) { console.error(`JobFill: Error`, e); }
          }
          return count;
        }
      });

      const totalFilled = fillResults.reduce((acc, curr) => acc + (curr.result as number || 0), 0);

      if (totalFilled > 0) {
        setStatus(`✓ Successfully filled ${totalFilled} fields!`);
      } else {
        setStatus('No matching fields found');
      }
    } catch (error: any) {
      console.error(error);
      setStatus(`Error: ${error.message}`);
    }
    finally { setLoading(false); }
  }

  if (showQuestionnaire) {
    return <Questionnaire userId={userId} onComplete={handleQuestionnaireComplete} backendUrl={backendUrl} />;
  }

  return (
    <div className="container">
      <h1>JobFill Pro</h1>

      {!hasProfile && (
        <div className="warning-banner">
          ⚠️ Profile not complete. Click "Setup Profile" to get started.
        </div>
      )}

      <div className="card">
        <button className="secondary" onClick={scanForm}>
          Scan Application
        </button>
        <button onClick={autoFill} disabled={loading || fields.length === 0 || !hasProfile}>
          {loading ? 'Filling...' : 'Fill Application'}
        </button>
      </div>

      <p className="status">{status}</p>

      <div className="actions">
        <button className="text-btn" onClick={() => setShowQuestionnaire(true)}>
          {hasProfile ? '✏️ Edit Profile' : '📝 Setup Profile'}
        </button>
      </div>
    </div>
  )
}

export default App
