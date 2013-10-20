(function() {
  var API, NLP, tabPort;

  API = 'http://localhost:3000/api';

  NLP = new nlp.NLP;

  chrome.contextMenus.create({
    title: 'Get Stats',
    contexts: ['selection'],
    onclick: function(info, tab) {
      var text;
      text = info.selectionText;
      return tabPort[tab.id].postMessage({
        id: 'show-stats',
        text: text
      });
    }
  });

  tabPort = {};

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
    var allLemmata, allWords, user, words;
    allWords = results[0], user = results[1];
    allLemmata = allWords.map(function(w) {
      return w.lemma;
    });
    words = {};
    words.common = "i you am a the he she it we they him her".split(' ');
    words.known = user.lemmata;
    words.untracked = _.difference(allLemmata, words.known, words.common);
    words.common.sort();
    words.known.sort();
    words.untracked.sort();
    console.log(words);
    return chrome.runtime.onConnect.addListener(function(port) {
      console.log('listening...', port);
      if (port.sender.tab != null) {
        tabPort[port.sender.tab.id] = port;
      }
      port.onMessage.addListener(function(msg) {
        var action, lemma, verb, _ref;
        switch (msg.action) {
          case 'add-word':
          case 'remove-word':
            _ref = msg.action.match(/(\w+)-word/), action = _ref[0], verb = _ref[1];
            lemma = msg.data.lemma;
            return $.ajax({
              url: API + ("/user/words/" + verb),
              type: 'post',
              dataType: 'json',
              data: {
                lemma: lemma
              },
              success: function(data) {
                return port.postMessage({
                  id: 'update-word',
                  data: data
                });
              }
            });
          default:
            return console.warn('got weird message', msg);
        }
      });
      return port.postMessage({
        id: 'load-words',
        data: words
      });
    });
  });

}).call(this);
