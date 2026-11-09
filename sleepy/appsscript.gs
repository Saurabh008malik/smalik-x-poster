// The Sleepy Biographer - YouTube sign-in helper (Google Apps Script web app, no Google Cloud project needed)
// GitHub does the heavy lifting (big video upload); this script only proves it is YOU and lends GitHub a short-lived
// (1 hour) YouTube access token for the Sleepy Biographer channel. It refuses to work for any other channel.
// Setup: Project Settings -> tick "Show appsscript.json" and paste appsscript.json; Services (+) -> YouTube Data API v3 -> Add;
// Deploy -> New deployment -> Web app -> Execute as: Me, Who has access: Anyone.

const KEY = 'PASTE_YOUR_KEY_HERE';       // the long random key Claude gives you in chat
const CHANNEL_MATCH = 'sleepy biographer';

function doPost(e) {
  try {
    if (!e.parameter || e.parameter.k !== KEY || KEY === 'PASTE_YOUR_KEY_HERE') return out({ok: false, error: 'wrong key'});
    const req = JSON.parse(e.postData.contents || '{}');
    const ch = YouTube.Channels.list('snippet', {mine: true});
    const name = (ch.items && ch.items.length) ? ch.items[0].snippet.title : '';
    if (name.toLowerCase().indexOf(CHANNEL_MATCH) < 0) {
      return out({ok: false, error: 'This script is connected to "' + name + '", not The Sleepy Biographer. Nothing done.'});
    }
    if (req.action === 'whoami') return out({ok: true, channel: name});
    if (req.action === 'token') return out({ok: true, channel: name, token: ScriptApp.getOAuthToken()});
    return out({ok: false, error: 'unknown action'});
  } catch (err) {
    return out({ok: false, error: String(err)});
  }
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

// Run once from the editor: approves access and shows which channel is connected.
function testConnection() {
  const ch = YouTube.Channels.list('snippet', {mine: true});
  Logger.log('Connected to: ' + ch.items[0].snippet.title);
}
