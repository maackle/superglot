(function() {
  $(function() {
    return $('a').click(function(e) {
      return console.log('haaallloo');
    });
  });

  chrome.tabs.query({
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
      $('.percent-known').text(mkPercent(known.length / uniqueCount));
      $('.percent-learning').text(mkPercent(learning.length / uniqueCount));
      $('.total-all').text(totalCount);
      $('.total-unique').text(uniqueCount);
      $('.total-known').text(known.length);
      $('.total-learning').text(learning.length);
      return $('.total-ignored').text(ignored.length);
    });
  });

}).call(this);
