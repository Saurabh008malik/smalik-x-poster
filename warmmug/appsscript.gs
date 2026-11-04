// Warm Mug Radio - YouTube uploader (Google Apps Script web app, no Google Cloud setup needed)
// GitHub builds the video and sends it here; this script posts it to the Warm Mug Radio channel.
// Setup: Services (+) -> YouTube Data API v3 -> Add. Deploy -> New deployment -> Web app,
// Execute as: Me, Who has access: Anyone. When Google asks which account/channel, pick Warm Mug Radio.

const KEY = 'wmc62d3ae7b7a284c8d75dceef';

function doPost(e) {
  try {
    if (!e.parameter || e.parameter.k !== KEY) return out({ok: false, error: 'wrong key'});
    const req = JSON.parse(e.postData.contents);
    const ch = YouTube.Channels.list('snippet', {mine: true});
    const name = (ch.items && ch.items.length) ? ch.items[0].snippet.title : '';
    if (req.action === 'whoami') return out({ok: true, channel: name});
    // safety: never post to any other channel (e.g. the cricket one)
    if (name.toLowerCase().indexOf('warm mug') < 0) {
      return out({ok: false, error: 'This script is connected to "' + name + '", not Warm Mug Radio. Nothing posted.'});
    }
    const video = Utilities.newBlob(Utilities.base64Decode(req.video), 'video/mp4', 'video.mp4');
    const res = YouTube.Videos.insert({
      snippet: {title: req.title, description: req.description, tags: req.tags, categoryId: '10', defaultLanguage: 'en'},
      status: {privacyStatus: req.privacy || 'public', selfDeclaredMadeForKids: false, containsSyntheticMedia: true, embeddable: true}
    }, 'snippet,status', video);
    let thumb = 'none';
    if (req.thumbnail) {
      try {
        YouTube.Thumbnails.set(res.id, Utilities.newBlob(Utilities.base64Decode(req.thumbnail), 'image/jpeg', 'thumb.jpg'));
        thumb = 'set';
      } catch (err) { thumb = 'failed: ' + err.message; }
    }
    // first comment from the channel itself (YouTube's API cannot pin it - pin by hand if you want)
    let comment = 'none';
    if (req.comment) {
      try {
        YouTube.CommentThreads.insert({
          snippet: {videoId: res.id, topLevelComment: {snippet: {textOriginal: req.comment}}}
        }, 'snippet');
        comment = 'posted';
      } catch (err) { comment = 'failed: ' + err.message; }
    }
    return out({ok: true, id: res.id, url: 'https://youtu.be/' + res.id, thumbnail: thumb,
                comment: comment, channel: name});
  } catch (err) {
    return out({ok: false, error: String(err)});
  }
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

// Run this once from the editor to approve access and see which channel it is connected to.
function testConnection() {
  const ch = YouTube.Channels.list('snippet', {mine: true});
  Logger.log('Connected to: ' + ch.items[0].snippet.title);
}
