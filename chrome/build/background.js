(function() {
  var API;

  API = 'http://localhost:3000/api';

  async.parallel([
    function(cb) {
      return $.getJSON(API + '/words', function(words) {
        return cb(null, words);
      });
    }, function(cb) {
      return $.getJSON(API + '/user', function(user) {
        return cb(null, user);
      });
    }
  ], function(err, results) {
    var allWords, user, words;
    allWords = results[0], user = results[1];
    words = {};
    words.common = "i you am a the he she it we they him her".split(' ');
    words.tracked = user.words;
    words.untracked = _.difference(allWords, words.tracked, words.common);
    words.common.sort();
    words.tracked.sort();
    words.untracked.sort();
    return chrome.runtime.onConnect.addListener(function(port) {
      console.log('listening...', port);
      port.onMessage.addListener(function(msg) {
        var lemma;
        switch (msg.action) {
          case 'update-word':
            console.log('marking ' + msg);
            lemma = msg.data.lemma;
            return $.post(API + '/api/user/words', {
              action: 'update',
              lemma: lemma
            }, function(data) {
              return port.postMessage({
                id: 'update-word',
                data: {
                  lemma: lemma,
                  classification: 0
                }
              });
            });
          default:
            return console.log('got weird message' + msg);
        }
      });
      return port.postMessage({
        id: 'load-words',
        data: words
      });
    });
  });

}).call(this);
