(function() {
  var API;

  API = 'http://localhost:3000';

  $.json(API + '/users/0', function(user) {
    var a, words;
    words = {};
    words.common = "i you am a the he she it we they him her".split(' ');
    words.untracked = (function() {
      var _i, _results;
      _results = [];
      for (a = _i = 1; _i <= 999999; a = ++_i) {
        _results.push(Math.random().toString(32).slice(2, 7));
      }
      return _results;
    })();
    words.tracked = ['walrus'];
    words.common.sort();
    words.tracked.sort();
    words.untracked.sort();
    return chrome.runtime.onConnect.addListener(function(port) {
      port.onMessage.addListener(function(msg) {
        switch (msg) {
          case 'debug-load':
            return 0;
        }
      });
      return port.postMessage({
        id: 'load-words',
        data: words
      });
    });
  });

}).call(this);
