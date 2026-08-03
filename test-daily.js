// Local test harness for daily-summary (not deployed)
const fs = require('fs');
process.env.FIREBASE_SERVICE_ACCOUNT = fs.readFileSync('./serviceAccountKey.json', 'utf8');
process.env.FIREBASE_DATABASE_URL = 'https://kumenya-mucii-rsvp-default-rtdb.firebaseio.com';
const { handler } = require('./netlify/functions/daily-summary.js');
(async () => {
  const res = await handler({}, {});
  console.log('RESULT:', JSON.stringify(res));
  process.exit(0);
})();
