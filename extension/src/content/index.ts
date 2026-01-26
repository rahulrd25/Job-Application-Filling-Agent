// content script to interact with job application forms

function findFormFields() {
    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
    return inputs.map(input => {
        const htmlInput = input as HTMLInputElement;
        const label = findLabel(htmlInput);
        return {
            name: htmlInput.name || htmlInput.id || 'unnamed_field',
            label: label,
            type: htmlInput.type,
            placeholder: htmlInput.placeholder,
            context: getContext(htmlInput)
        };
    });
}

function findLabel(input: HTMLElement): string {
    if (input.id) {
        const labelElement = document.querySelector(`label[for="${input.id}"]`);
        if (labelElement && labelElement.textContent) return labelElement.textContent.trim();
    }
    const parentLabel = input.closest('label');
    if (parentLabel && parentLabel.textContent) return parentLabel.textContent.trim();
    const previousElement = input.previousElementSibling;
    if (previousElement && previousElement.textContent) return previousElement.textContent.trim();
    return input.getAttribute('aria-label') || '';
}

function getContext(input: HTMLElement): string {
    const container = input.closest('div, section, fieldset');
    return container?.textContent?.trim().substring(0, 300) || '';
}

chrome.runtime.onMessage.addListener((request: any, _sender: chrome.runtime.MessageSender, sendResponse: (response?: any) => void) => {
    if (request.action === 'SCAN_FORM') {
        const fields = findFormFields();
        sendResponse({ fields, url: window.location.href });
    } else if (request.action === 'FILL_FORM') {
        const { data } = request;

        // Fill text/select/textarea fields
        for (const [name, value] of Object.entries(data)) {
            const input = document.getElementsByName(name)[0] || document.getElementById(name) || document.querySelector(`[name="${name}"]`);
            if (input) {
                const htmlInput = input as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
                htmlInput.value = value as string;
                htmlInput.dispatchEvent(new Event('input', { bubbles: true }));
                htmlInput.dispatchEvent(new Event('change', { bubbles: true }));
                htmlInput.dispatchEvent(new Event('blur', { bubbles: true }));
            }
        }

        // Auto-Consent Checkboxes
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            const checkbox = cb as HTMLInputElement;
            const label = findLabel(checkbox).toLowerCase();
            const parentText = checkbox.parentElement?.textContent?.toLowerCase() || '';
            const consentWords = ['consent', 'privacy', 'data', 'store', 'terms', 'policy', 'agree'];

            if (consentWords.some(word => label.includes(word) || parentText.includes(word))) {
                if (!checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('click', { bubbles: true }));
                }
            }
        });

        sendResponse({ success: true });
    }
    return true;
});
