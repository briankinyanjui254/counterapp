/**
 * notify.js — Netlify Function
 * ---------------------------------------------------------------
 * Called by the frontend after each successful RSVP.
 * Every 5th confirmation (5, 10, 15, ...) it sends:
 *   1. An email via SMTP (nodemailer)
 *   2. A WhatsApp message via CallMeBot
 *
 * Required environment variables (set in Netlify dashboard):
 *   FIREBASE_SERVICE_ACCOUNT  - stringified service account JSON
 *   FIREBASE_DATABASE_URL     - e.g. https://myproject-default-rtdb.firebaseio.com
 *   SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
 *   NOTIFICATION_EMAIL        - recipient address
 *   CALLMEBOT_PHONE           - e.g. 254710298666
 *   CALLMEBOT_API_KEY
 */

const admin = require('firebase-admin');
const nodemailer = require('nodemailer');

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

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

  await transporter.sendMail({
    from: `"Kumenya Mucii RSVP" <${SMTP_USER}>`,
    to: NOTIFICATION_EMAIL,
    subject: `🎉 RSVP Update — ${count} people confirmed!`,
    text: `Hi Brenda, ${count} guests have confirmed attendance for Kumenya Mucii so far. Keep sharing the link!`,
    html: `<p>Hi Brenda,</p><p><strong>${count} guests</strong> have confirmed attendance for <strong>Kumenya Mucii</strong> so far. Keep sharing the link!</p>`,
  });
}

/* ---------- WhatsApp via CallMeBot ---------- */
async function sendWhatsApp(count) {
  const { CALLMEBOT_PHONE, CALLMEBOT_API_KEY } = process.env;
  if (!CALLMEBOT_PHONE || !CALLMEBOT_API_KEY) {
    throw new Error('CallMeBot env vars (CALLMEBOT_PHONE, CALLMEBOT_API_KEY) are not set');
  }

  const message = `🎉 RSVP Update: ${count} guests have confirmed attendance for Kumenya Mucii! Keep sharing the link.`;
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

/* ---------- Handler ---------- */
exports.handler = async function (event) {
  // CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: CORS_HEADERS, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: CORS_HEADERS,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    // Parse (and sanity-check) the client-supplied counter — used only as a hint;
    // the authoritative value is read from Firebase below.
    let clientCounter = null;
    try {
      const parsed = JSON.parse(event.body || '{}');
      clientCounter = parseInt(parsed.counter, 10);
    } catch (e) {
      /* ignore malformed body — we rely on Firebase anyway */
    }

    const db = getDatabase();

    const [counterSnap, lastNotifiedSnap] = await Promise.all([
      db.ref('counter').once('value'),
      db.ref('lastNotifiedAt').once('value'),
    ]);

    const counter = counterSnap.val() || 0;
    const lastNotifiedAt = lastNotifiedSnap.val() || 0;

    console.log(`notify: counter=${counter}, lastNotifiedAt=${lastNotifiedAt}, clientCounter=${clientCounter}`);

    // Only notify on every 5th confirmation, and never twice for the same milestone
    if (counter > 0 && counter % 5 === 0 && counter > lastNotifiedAt) {
      const results = await Promise.allSettled([sendEmail(counter), sendWhatsApp(counter)]);

      results.forEach((r, i) => {
        const channel = i === 0 ? 'email' : 'whatsapp';
        if (r.status === 'rejected') {
          console.error(`notify: ${channel} failed —`, r.reason && r.reason.message);
        } else {
          console.log(`notify: ${channel} sent for count ${counter}`);
        }
      });

      // Mark milestone as notified (even if one channel failed, to avoid spam loops)
      await db.ref('lastNotifiedAt').set(counter);

      return {
        statusCode: 200,
        headers: CORS_HEADERS,
        body: JSON.stringify({
          success: true,
          notified: true,
          counter,
          email: results[0].status,
          whatsapp: results[1].status,
        }),
      };
    }

    return {
      statusCode: 200,
      headers: CORS_HEADERS,
      body: JSON.stringify({ success: true, notified: false, counter }),
    };
  } catch (err) {
    console.error('notify: unhandled error —', err);
    return {
      statusCode: 500,
      headers: CORS_HEADERS,
      body: JSON.stringify({ success: false, error: err.message }),
    };
  }
};
