(function() {
  var addMeaningTooltip, markWords;

  markWords = function(lemmata, label, after) {
    var lemmataString;
    lemmataString = lemmata.join("\n");
    return $.post('/api/user/words/update/', {
      lemmata: lemmataString,
      label: label
    }, after);
  };

  addMeaningTooltip = function(el, meaning) {
    return $(el).tooltip({
      title: meaning,
      placement: 'left'
    });
  };

  $(function() {
    $('.annotated-word-list li').click(function(e) {
      var $el, label, lemma, newGroup;
      $el = $(this);
      if ($el.attr('data-group-label') === 'ignored') {
        return false;
      }
      lemma = $el.data('lemma');
      label = $el.attr('data-group-label');
      if (label === 'known') {
        newGroup = 'learning';
      } else {
        newGroup = 'known';
      }
      return markWords([lemma], newGroup, function(data) {
        if (data) {
          return $("[data-lemma='" + lemma + "']").attr('data-group-label', newGroup);
        }
      });
    });
    $('.annotated-word-list .controls .mark-all').click(function(e) {
      var $affected, label, lemmata;
      label = $(this).attr('data-group-label');
      $affected = $('.annotated-word-list li').filter(function(i, el) {
        return $(el).attr('data-group-label') !== label;
      });
      lemmata = $affected.map(function(i, el) {
        return $(el).attr('data-lemma');
      }).get();
      return markWords(lemmata, label, function(data) {
        return $affected.attr('data-group-label', label);
      });
    });
    $('.vocab-list li').mouseenter(function(e) {
      var $el, el, wordId,
        _this = this;
      el = this;
      $el = $(el);
      wordId = $el.data('id');
      if ($el.data('translation') === void 0) {
        $(el).data('translation', '');
        return $.get('/api/words/translate/', {
          word_id: wordId
        }, function(data) {
          var meaning;
          meaning = data.target;
          addMeaningTooltip(el, meaning);
          $el.data('translation', meaning);
          return $el.trigger('mouseenter');
        });
      }
    });
    return $('.accordion').accordion({
      header: '.header',
      collapsible: true
    });
  });

}).call(this);
