// Quick SMTP connectivity check (local test only — not deployed)
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT || '465', 10),
  secure: true,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  connectionTimeout: 15000,
});

transporter.verify()
  .then(() => { console.log('SMTP OK: login and connection verified'); process.exit(0); })
  .catch(err => { console.error('SMTP FAILED:', err.message); process.exit(1); });
