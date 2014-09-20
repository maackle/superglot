(function() {
  var addMeaningTooltip, markWords, setupAnnotation;

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

  setupAnnotation = function() {
    var attachAnnotationControls, deselectWords, hideWordScorePopup, selectWord, showWordScorePopup, updateWord;
    selectWord = function(el) {
      var $word;
      $word = $(el);
      if (!$word.hasClass('selected')) {
        deselectWords();
        $word.addClass('selected');
        return showWordScorePopup(el);
      } else {
        return deselectWords();
      }
    };
    deselectWords = function() {
      $('.annotated-words li').removeClass('selected');
      return hideWordScorePopup();
    };
    updateWord = function(el, score) {
      var label, lemma;
      lemma = $(el).attr('data-lemma');
      if (score < 3) {
        label = 'learning';
      } else {
        label = 'known';
      }
      return markWords([lemma], label, function(data) {
        if (data) {
          $("[data-lemma='" + lemma + "']").attr('data-group-label', label);
          return deselectWords();
        }
      });
    };
    showWordScorePopup = function(el) {
      var $popup;
      $popup = $('#word-score-popup');
      $popup.show().focus();
      return $(document).on('keypress', function(e) {
        var char, score;
        char = String.fromCharCode(e.keyCode);
        score = parseInt(char, 10);
        if (score >= 0 && score <= 5) {
          $popup.find("input[value=\"" + score + "\"]").prop('checked', 1);
          return updateWord(el, score);
        }
      });
    };
    hideWordScorePopup = function(el) {
      var $popup;
      $popup = $('#word-score-popup');
      $popup.hide();
      return $(document).off('keypress');
    };
    attachAnnotationControls = function($el) {
      var $popup;
      $popup = $('#word-score-popup');
      return $el.click(function(e) {
        return selectWord(this);
      });
    };
    return attachAnnotationControls($('.annotated-word-list li'));
  };

  $(function() {
    setupAnnotation();
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
