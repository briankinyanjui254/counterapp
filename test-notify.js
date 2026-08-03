// Local test harness for the notify function (not deployed)
const fs = require('fs');

process.env.FIREBASE_SERVICE_ACCOUNT = fs.readFileSync('./serviceAccountKey.json', 'utf8');
process.env.FIREBASE_DATABASE_URL = 'https://kumenya-mucii-rsvp-default-rtdb.firebaseio.com';

const { handler } = require('./netlify/functions/notify.js');

(async () => {
  const res = await handler({ httpMethod: 'POST', body: JSON.stringify({ counter: 5 }) });
  console.log('STATUS:', res.statusCode);
  console.log('BODY:', res.body);
  process.exit(0);
})();
