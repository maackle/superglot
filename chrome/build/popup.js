(function() {
  var API, xhrUser;

  API = API_URL;

  xhrUser = $.ajax({
    url: API + '/user',
    type: 'get',
    dataType: 'json'
  });

  xhrUser.done(function(user) {
    console.log('user', user);
    if (user != null) {
      return chrome.tabs.query({
        active: true,
        currentWindow: true
      }, function(tabs) {
        var tab;
        tab = tabs[0];
        return chrome.tabs.sendMessage(tab.id, {
          id: 'stats-request'
        }, function(response) {
          var ignored, known, learning, mkPercent, stats, totalCount, uniqueCount, _ref;
          mkPercent = function(r) {
            var p;
            p = 100 * r;
            if (p < 10) {
              return p.toFixed(1);
            } else {
              return parseInt(p);
            }
          };
          stats = response.data.stats;
          totalCount = stats.totalWordCount;
          uniqueCount = stats.uniqueWords.length;
          _ref = stats.intersections, known = _ref.known, learning = _ref.learning, ignored = _ref.ignored;
          return $(function() {
            $('.percent-known').text(mkPercent(known.length / uniqueCount));
            $('.percent-learning').text(mkPercent(learning.length / uniqueCount));
            $('.total-all').text(totalCount);
            $('.total-unique').text(uniqueCount);
            $('.total-known').text(known.length);
            $('.total-learning').text(learning.length);
            $('.total-ignored').text(ignored.length);
            return $('.case.logged-in').show();
          });
        });
      });
    } else {
      return $(function() {
        return $('.case.logged-out').show().find('form').on('submit', function(e) {
          var xhrLogin;
          console.log('submit');
          xhrLogin = $.ajax({
            url: SITE_URL + '/login',
            type: 'post',
            data: {
              username: $(this).find('[name=username]').val()
            }
          });
          xhrLogin.done(function(res) {
            return console.log('login: ', res);
          });
          return xhrLogin.fail(function() {
            return console.log('failure', arguments);
          });
        });
      });
    }
  });

  xhrUser.fail(function(err) {
    console.error('error:', arguments);
    return $('.case.error').show();
  });

}).call(this);
