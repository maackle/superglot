(function() {
  var API, NLP, tabPort, userLemmata;

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

  userLemmata = {};

  console.log('ready to load data');

  async.parallel([
    function(cb) {
      var lemmata;
      if (localStorage['superglot-lemmata'] != null) {
        lemmata = $.parseJSON(localStorage['superglot-lemmata']);
        console.debug('loaded lemmata from localStorage');
        return cb(null, lemmata);
      } else {
        return $.getJSON(API + '/words/lemmata', function(lemmata) {
          localStorage['superglot-lemmata'] = JSON.stringify(lemmata);
          return cb(null, lemmata);
        });
      }
    }, function(cb) {
      return $.getJSON(API + '/user', function(user) {
        return cb(null, user);
      });
    }
  ], function(err, results) {
    var lemmata, user;
    lemmata = results[0], user = results[1];
    userLemmata = new LemmaPartition({
      known: user.lemmata.known,
      learning: user.lemmata.learning,
      ignored: user.lemmata.ignored
    });
    return chrome.runtime.onConnect.addListener(function(port) {
      console.log('listening...', port);
      if (port.sender.tab != null) {
        tabPort[port.sender.tab.id] = port;
      }
      port.onMessage.addListener(function(msg) {
        var diff;
        switch (msg.action) {
          case 'word-diff':
            diff = msg.data.diff;
            return $.ajax({
              url: API + "/user/words/apply-diffs",
              type: 'post',
              dataType: 'json',
              data: {
                diffs: JSON.stringify([diff])
              },
              success: function(data) {
                console.log('applying diff', diff);
                console.log(userLemmata);
                userLemmata.applyDiff(diff);
                console.log(userLemmata);
                return port.postMessage({
                  id: 'word-diff',
                  data: {
                    diff: diff
                  }
                });
              }
            });
          default:
            return console.warn('got weird message', msg);
        }
      });
      return port.postMessage({
        id: 'load-words',
        data: {
          lemmata: {
            all: lemmata.all,
            common: lemmata.common,
            user: userLemmata
          }
        }
      });
    });
  });

}).call(this);
