/** Capture safe page context for issue analysis. */

function detectVisibleError() {
  const selectors = [
    ".error", ".alert-danger", ".alert-error", "[role='alert']",
    ".text-danger", ".notification-error", "#error", ".error-message",
  ];
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el?.textContent?.trim()) {
      return el.textContent.trim().slice(0, 500);
    }
  }
  const bodyText = document.body?.innerText || "";
  const patterns = [
    /access denied/i, /403 forbidden/i, /500 internal server error/i,
    /something went wrong/i, /unable to process/i, /session expired/i,
  ];
  for (const pat of patterns) {
    const match = bodyText.match(pat);
    if (match) return match[0];
  }
  return null;
}

function getContext() {
  const selection = window.getSelection()?.toString().trim().slice(0, 500) || null;
  return {
    page_url: location.href,
    page_title: document.title,
    page_error: detectVisibleError(),
    selected_text: selection || undefined,
  };
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === "GET_CONTEXT") {
    sendResponse(getContext());
  }
  return true;
});
