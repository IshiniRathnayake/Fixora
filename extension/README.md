# Fixora Browser Extension

AI-powered office IT support extension for the supervisor demo.

## Load in Chrome / Edge

1. Start Fixora API: `.\run-local.ps1` or run backend on port 8000
2. Open `chrome://extensions` (or `edge://extensions`)
3. Enable **Developer mode**
4. Click **Load unpacked**
5. Select this folder: `extension/`

## Demo flow

1. Open http://localhost:5173 and sign in
2. Go to **Enterprise** or any page with an error
3. Click the **Fixora** extension icon
4. Sign in with `admin@fixora.local` / `admin123`
5. Describe the issue (e.g. "Access denied when submitting order")
6. Click **Analyze with AI Agents**
7. Show the multi-agent workflow and resolution steps

## What it captures

- Current page URL and title
- Visible error messages on the page
- Selected text (if any)
- Browser/OS info

Passwords and form fields are **not** captured.

## API

Extension calls `POST /api/v1/support/analyze` with Bearer token.
