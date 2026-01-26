// content script to interact with job application forms

function findFormFields() {
    const selectors = [
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"])',
        'textarea',
        'select',
        '[role="combobox"]',
        '[contenteditable="true"]'
    ];

    const elements = Array.from(document.querySelectorAll(selectors.join(',')));
    const seenRadios = new Set();

    return elements.map(el => {
        const input = el as HTMLInputElement;

        // Group radios so we don't send 5 fields for one question
        if (input.type === 'radio' && input.name) {
            if (seenRadios.has(input.name)) return null;
            seenRadios.add(input.name);
        }

        const parent = input.closest('div, section, .form-group, .field, fieldset') as HTMLElement;
        const context = parent?.innerText?.substring(0, 500).replace(/\s+/g, ' ').trim() || "";

        return {
            id: input.id || input.getAttribute('name') || 'gen_' + Math.random().toString(36).substr(2, 5),
            name: input.getAttribute('name') || "",
            label: findLabel(input),
            placeholder: input.placeholder || input.getAttribute('aria-placeholder') || "",
            type: input.type || input.getAttribute('role') || 'text',
            context: context,
            options: input.tagName === 'SELECT' ? Array.from((el as HTMLSelectElement).options).map(o => o.text) : []
        };
    }).filter(f => f !== null && (f.label || f.placeholder || f.context));
}

function findLabel(input: HTMLElement): string {
    // 1. Explicit Aria Label
    const ariaLabel = input.getAttribute('aria-label');
    if (ariaLabel) return ariaLabel;

    // 2. Aria Labelled By
    const labelledBy = input.getAttribute('aria-labelledby');
    if (labelledBy) {
        const labels = labelledBy.split(' ').map(id => document.getElementById(id)?.innerText).filter(Boolean);
        if (labels.length > 0) return labels.join(' ').trim();
    }

    // 3. For attribute
    if (input.id) {
        const labelEl = document.querySelector(`label[for="${input.id}"]`) as HTMLElement;
        if (labelEl) return labelEl.innerText.trim();
    }

    // 4. Nested in Label
    const nestedLabel = input.closest('label') as HTMLElement;
    if (nestedLabel) return nestedLabel.innerText.trim();

    // 5. Preceding Label
    const parent = input.parentElement;
    if (parent) {
        const prevLabel = Array.from(parent.querySelectorAll('label')).find(l => l.contains(input) || l.nextElementSibling === input);
        if (prevLabel) return prevLabel.innerText.trim();
    }

    // 6. Closest text context
    const container = input.closest('div, section, .form-group, .field, fieldset') as HTMLElement;
    if (container) {
        const text = container.innerText.split('\n')[0].trim();
        if (text && text.length < 100) return text;
    }

    return "";
}

chrome.runtime.onMessage.addListener((request: any, _sender: chrome.runtime.MessageSender, sendResponse: (response?: any) => void) => {
    if (request.action === 'SCAN_FORM') {
        const fields = findFormFields();
        sendResponse({ fields, url: window.location.href });
    } else if (request.action === 'FILL_FORM') {
        const { data } = request;
        let fieldsFilled = 0;

        for (const [id, value] of Object.entries(data)) {
            // Find by ID, then Name, then Data-Attributes
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
                        fieldsFilled++;
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
                            fieldsFilled++;
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
                    fieldsFilled++;
                }
            } catch (e) { console.error(`JobFill: Error filling ${id}`, e); }
        }

        // Auto-Consent for terms
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            const checkbox = cb as HTMLInputElement;
            if (checkbox.checked) return;
            const text = (checkbox.closest('label')?.innerText || checkbox.parentElement?.innerText || "").toLowerCase();
            const consentWords = ['consent', 'privacy', 'data', 'store', 'terms', 'policy', 'agree', 'acknowledge'];
            if (consentWords.some(word => text.includes(word))) {
                checkbox.click();
                fieldsFilled++;
            }
        });

        sendResponse({ success: true, count: fieldsFilled });
    }
    return true;
});
