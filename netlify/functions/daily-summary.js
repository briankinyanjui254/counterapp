/**
 * daily-summary.js — Netlify Scheduled Function
 * ---------------------------------------------------------------
 * Runs daily at 17:00 UTC (8:00 PM EAT) — cron: "0 17 * * *"
 * Fetches the current RSVP counter from Firebase and sends a daily
 * summary via email (nodemailer) and WhatsApp (CallMeBot).
 *
 * Required environment variables (set in Netlify dashboard):
 *   FIREBASE_SERVICE_ACCOUNT  - stringified service account JSON
 *   FIREBASE_DATABASE_URL     - e.g. https://myproject-default-rtdb.firebaseio.com
 *   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
 *   NOTIFICATION_EMAIL        - recipient address
 *   CALLMEBOT_PHONE           - e.g. 254710298666
 *   CALLMEBOT_API_KEY
 */

const { schedule } = require('@netlify/functions');
const admin = require('firebase-admin');
const nodemailer = require('nodemailer');

/* ---------- Firebase Admin (initialised once per warm container) ---------- */
function getDatabase() {
  if (!admin.apps.length) {
    const raw = process.env.FIREBASE_SERVICE_ACCOUNT;
    if (!raw) throw new Error('FIREBASE_SERVICE_ACCOUNT env var is not set');
    const serviceAccount = JSON.parse(raw);
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
      databaseURL: process.env.FIREBASE_DATABASE_URL,
    });
  }
  return admin.database();
}

/* ---------- Email ---------- */
async function sendEmail(count) {
  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFICATION_EMAIL } = process.env;
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS || !NOTIFICATION_EMAIL) {
    throw new Error('SMTP env vars (SMTP_HOST, SMTP_USER, SMTP_PASS, NOTIFICATION_EMAIL) are not fully set');
  }

  const port = parseInt(SMTP_PORT || '465', 10);
  const transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port,
    secure: port === 465, // true for 465 (SSL), false for 587 (STARTTLS)
    auth: { user: SMTP_USER, pass: SMTP_PASS },
  });

  const body =
    `Good evening Brenda! Here's your daily RSVP update: ${count} guests have confirmed attendance ` +
    `for Kumenya Mucii (Njeri & Mburu) as of today. Date: 26th September 2026.`;

  await transporter.sendMail({
    from: `"Kumenya Mucii RSVP" <${SMTP_USER}>`,
    to: NOTIFICATION_EMAIL,
    subject: '📊 Daily RSVP Summary — Kumenya Mucii',
    text: body,
    html: `<p>Good evening Brenda!</p><p>Here's your daily RSVP update: <strong>${count} guests</strong> have confirmed attendance for <strong>Kumenya Mucii</strong> (Njeri &amp; Mburu) as of today.</p><p>Date: 26th September 2026.</p>`,
  });
}

/* ---------- WhatsApp via CallMeBot ---------- */
async function sendWhatsApp(count) {
  const { CALLMEBOT_PHONE, CALLMEBOT_API_KEY } = process.env;
  if (!CALLMEBOT_PHONE || !CALLMEBOT_API_KEY) {
    throw new Error('CallMeBot env vars (CALLMEBOT_PHONE, CALLMEBOT_API_KEY) are not set');
  }

  const message =
    `📊 Daily RSVP Summary: ${count} guests have confirmed attendance for Kumenya Mucii ` +
    `(Njeri & Mburu) as of today. Event date: 26th September 2026.`;

  const url =
    `https://api.callmebot.com/whatsapp.php?phone=${encodeURIComponent(CALLMEBOT_PHONE)}` +
    `&text=${encodeURIComponent(message)}` +
    `&apikey=${encodeURIComponent(CALLMEBOT_API_KEY)}`;

  const res = await fetch(url); // Node 18+ has global fetch
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`CallMeBot request failed: ${res.status} ${body.slice(0, 200)}`);
  }
}

/* ---------- Scheduled handler ---------- */
const handler = async function () {
  try {
    const db = getDatabase();
    const snap = await db.ref('counter').once('value');
    const count = snap.val() || 0;

    console.log(`daily-summary: current counter = ${count}`);

    const results = await Promise.allSettled([sendEmail(count), sendWhatsApp(count)]);

    results.forEach((r, i) => {
      const channel = i === 0 ? 'email' : 'whatsapp';
      if (r.status === 'rejected') {
        console.error(`daily-summary: ${channel} failed —`, r.reason && r.reason.message);
      } else {
        console.log(`daily-summary: ${channel} sent`);
      }
    });

    return {
      statusCode: 200,
      body: JSON.stringify({
        success: true,
        counter: count,
        email: results[0].status,
        whatsapp: results[1].status,
      }),
    };
  } catch (err) {
    console.error('daily-summary: unhandled error —', err);
    return {
      statusCode: 500,
      body: JSON.stringify({ success: false, error: err.message }),
    };
  }
};

// 17:00 UTC = 20:00 EAT (East Africa Time, UTC+3)
exports.handler = schedule('0 17 * * *', handler);
