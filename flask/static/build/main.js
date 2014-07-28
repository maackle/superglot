(function() {
  var addMeaningTooltip, markWords;

  markWords = function(lemmata, group, after) {
    var lemmataString;
    lemmataString = lemmata.join("\n");
    return $.post('/api/user/words/update/', {
      lemmata: lemmataString,
      group: group
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
      var $el, group, lemma, newGroup;
      $el = $(this);
      if ($el.attr('data-group') === 'ignored') {
        return false;
      }
      lemma = $el.data('lemma');
      group = $el.attr('data-group');
      if (group === 'known') {
        newGroup = 'learning';
      } else {
        newGroup = 'known';
      }
      return markWords([lemma], newGroup, function(data) {
        if (data) {
          return $("[data-lemma='" + lemma + "']").attr('data-group', newGroup);
        }
      });
    });
    $('.annotated-word-list .controls .mark-all').click(function(e) {
      var $affected, group, lemmata;
      group = $(this).attr('data-group');
      $affected = $('.annotated-word-list li').filter(function(i, el) {
        return $(el).attr('data-group') !== group;
      });
      lemmata = $affected.map(function(i, el) {
        return $(el).attr('data-lemma');
      }).get();
      return markWords(lemmata, group, function(data) {
        return $affected.attr('data-group', group);
      });
    });
    return $('.vocab-list li').mouseenter(function(e) {
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
  });

}).call(this);
