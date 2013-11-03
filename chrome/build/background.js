(function() {
  var API, NLP, tabPorts, userLemmata;

  API = 'http://localhost:3000/api';

  NLP = new nlp.NLP;

  chrome.contextMenus.create({
    title: "Get Stats for '%s'",
    contexts: ['selection'],
    onclick: function(info, tab) {
      var text;
      text = info.selectionText;
      return tabPorts[tab.id].postMessage({
        id: 'show-stats',
        data: {
          text: text
        }
      });
    }
  });

  chrome.contextMenus.create({
    title: 'Get Stats',
    contexts: ['page'],
    onclick: function(info, tab) {
      return tabPorts[tab.id].postMessage({
        id: 'show-stats'
      });
    }
  });

  tabPorts = {};

  userLemmata = {};

  console.debug('ready to load data');

  async.parallel([
    function(cb) {
      return chrome.storage.local.get('superglot-lemmata', function(storage) {
        if (storage['superglot-lemmata'] != null) {
          console.debug('loaded lemmata from chrome.storage.local');
          return cb(null, storage['superglot-lemmata']);
        } else {
          console.debug('downloading from server...');
          return $.getJSON(API + '/words/lemmata', function(lemmata) {
            console.debug('downloaded lemmata from server');
            return chrome.storage.local.set({
              'superglot-lemmata': lemmata
            }, function() {
              console.debug('saved to storage: ', arguments, chrome.runtime.lastError);
              return cb(null, lemmata);
            });
          });
        }
      });
    }, function(cb) {
      return $.getJSON(API + "/user", function(user) {
        return cb(null, user);
      });
    }
  ], function(err, results) {
    var lemmata, user;
    if (err) {
      console.error(err);
      return;
    }
    console.debug('words and user loaded');
    lemmata = results[0], user = results[1];
    userLemmata = new LemmaPartition({
      known: user.lemmata.known,
      learning: user.lemmata.learning,
      ignored: user.lemmata.ignored
    });
    return chrome.runtime.onConnect.addListener(function(port) {
      console.log('listening...', port);
      if (port.sender.tab != null) {
        tabPorts[port.sender.tab.id] = port;
      }
      port.onMessage.addListener(function(msg) {
        var diff;
        switch (msg.id) {
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
