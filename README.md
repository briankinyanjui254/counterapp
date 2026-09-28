# Kumenya Mucii — Wedding RSVP Site

A single-page RSVP web app for a wedding event. Guests can confirm their attendance
with a single tap, and each confirmation is stored in **Firebase** so the couple can
track how many guests are coming in real time.

**Live site:** https://kumenya-mucii-rsvp.netlify.app
(auto-deploys from the `main` branch of this repository)

---

## Overview

- Guests open the page and tap **"Click here to confirm attendance."**
- The app increments a shared attendance **counter** and records a **device
  fingerprint** so the same device cannot RSVP twice.
- After confirming, the button is replaced with a **"Thank you for confirming
  attendance ♥"** message.
- All RSVP data lives in Firebase — there is no other backend server to run.

---

## Tech stack

| Layer      | Technology |
|------------|------------|
| Frontend   | A single, self-contained `index.html` (HTML + inline CSS + vanilla JS) |
| Data store | **Firebase Realtime Database** (project `kumenya-mucii-rsvp`) via the Firebase JS SDK (compat build, loaded from the CDN) |
| Hosting    | Static hosting — currently **Netlify**; works equally on GitHub Pages or Vercel |

> **Note on the data store:** The app uses the Firebase **Realtime Database**
> (`databaseURL: https://kumenya-mucii-rsvp-default-rtdb.firebaseio.com`), storing a
> `counter` value and a `fingerprints/` node. It does **not** use Cloud Firestore.
> The Firebase config is embedded directly in `index.html`, so all reads/writes
> happen **client-side** and no server-side environment variables are required for
> the site to function.

> **Email notifications have been removed.** The event has concluded, so the
> previous Netlify serverless functions that sent per-RSVP and daily-summary emails
> (via nodemailer/SMTP) have been deleted. The RSVP flow still writes to Firebase —
> it simply no longer triggers any email alerts.

---

## Repository layout

```
counterapp/
├── index.html          # The entire app (markup, styles, and RSVP logic)
├── border.svg          # Decorative assets
├── pattern.svg
├── shield.svg
├── couple.jpg          # Couple photo
├── make_assets.py      # Helper script that generated the SVG/PNG assets
├── netlify.toml        # Netlify static-publish config
├── package.json        # Project metadata (no runtime deps needed for the static site)
├── .gitignore          # Excludes secrets, env files, and service-account keys
└── README.md
```

---

## Deployment

The site is 100% static — a single HTML file plus a few image/SVG assets — so it can
be hosted on any static host. Firebase is called directly from the browser, so **no
build step and no server-side environment variables are required** for the RSVP form
to work.

### a. Netlify (current / recommended)

1. In the Netlify dashboard choose **Add new site → Import an existing project**
   and connect this GitHub repository (`briankinyanjui254/counterapp`).
2. Build settings:
   - **Build command:** _(leave empty — no build needed)_
   - **Publish directory:** `.` (the repo root; already set in `netlify.toml`)
3. Deploy. Netlify will **auto-deploy on every push to `main`**.

**Environment variables:** Not required for the current setup, because the Firebase
config is embedded client-side in `index.html`. If you ever move Firebase access to a
server-side function again, you would supply the service-account credentials as env
vars (from the downloaded service-account JSON):

- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY` (paste the full key, keeping the `\n` line breaks)

### b. GitHub Pages

1. Push the repo to GitHub (already done).
2. Go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to *Deploy from a branch*, pick
   the **`main`** branch and the **`/ (root)`** folder, then **Save**.
4. Your site will be published at
   `https://<username>.github.io/counterapp/`.

Because Firebase is called client-side using the SDK config embedded in
`index.html`, **no server-side environment variables are needed** for basic
read/write — GitHub Pages serves the static file and Firebase handles the data.

### c. Vercel

1. In Vercel choose **Add New → Project** and import this GitHub repository.
2. Framework preset: **Other** (it is a plain static site).
   - **Build command:** _(none)_
   - **Output directory:** `.` (root)
3. Deploy. Vercel serves it as a static site and redeploys automatically on each
   push to `main`.

---

## Firebase setup

- The Firebase project is **`kumenya-mucii-rsvp`**.
- Data is stored in the **Realtime Database** under `counter` and `fingerprints/`.
- Make sure the **Realtime Database security rules** allow the read/increment
  operations the page performs (reading `counter`, and writing `counter` /
  `fingerprints/<hash>`). Tighten these rules as appropriate for your needs.
- **Never commit the service-account key.** The admin SDK key file
  (`kumenya-mucii-rsvp-firebase-adminsdk-fbsvc-*.json`) and any `.env` files are
  listed in `.gitignore` and must stay out of version control.

---

## Viewing RSVPs

To see how many guests confirmed:

1. Open the [Firebase Console](https://console.firebase.google.com/).
2. Select the **`kumenya-mucii-rsvp`** project.
3. Go to **Realtime Database** and inspect:
   - **`counter`** — the total number of confirmed attendees.
   - **`fingerprints/`** — one entry per device that confirmed (used to prevent
     duplicate RSVPs).

> If you configure a Firestore `rsvps` collection in the future, responses would
> instead be viewed under **Firestore Database → `rsvps` collection**.

---

## Notes

- **Email notifications removed:** Since the event has concluded, all email-alerting
  serverless functions and their SMTP/nodemailer dependencies have been removed. The
  RSVP form continues to work as a static page backed by Firebase.
