(function() {
  var SRS_SCORE_CHOICES, addMeaningTooltip, markWords, setupAnnotation,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  SRS_SCORE_CHOICES = [1, 2, 3, 4];

  markWords = function(lemmata, score, after) {
    var lemmataString;
    if (score === 'known') {
      score = 4;
    } else if (score === 'learning') {
      score = 2;
    }
    score = parseInt(score, 10);
    lemmataString = lemmata.join("\n");
    return $.post('/api/user/words/update/', {
      lemmata: lemmataString,
      score: score
    }, after);
  };

  addMeaningTooltip = function(el, meaning) {
    return $(el).tooltip({
      title: meaning,
      placement: 'left'
    });
  };

  setupAnnotation = function() {
    var $popup, $popupChoices, attachAnnotationControls, deselectWords, hideWordScorePopup, selectWord, setPopupScore, showWordScorePopup, updateWord;
    $popup = $('#word-score-popup');
    $popupChoices = $popup.find('.scores .choice');
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
      if (score <= 0) {
        label = null;
      } else if (score < 3) {
        label = 'learning';
      } else {
        label = 'known';
      }
      return markWords([lemma], score, function(data) {
        if (data) {
          $(el).attr('data-group-label', label);
          $(el).attr('data-score', score);
          return deselectWords();
        }
      });
    };
    setPopupScore = function(score) {
      $popupChoices.removeClass('selected');
      return $popupChoices.filter("[data-score=" + score + "]").addClass('selected');
    };
    showWordScorePopup = function(el) {
      $popup.addClass('visible').focus();
      $popup.find('.lemma').text($(el).attr('data-lemma'));
      setPopupScore($(el).attr('data-score'));
      $popupChoices.click(function(e) {
        var score;
        score = $(this).attr('data-score');
        if (score >= 0 && score <= 5) {
          setPopupScore(score);
          return updateWord(el, score);
        }
      });
      $(document).on('keyup', function(e) {
        if (e.keyCode === 27) {
          return deselectWords();
        }
      });
      return $(document).on('keypress', function(e) {
        var char, score;
        char = String.fromCharCode(e.keyCode);
        score = parseInt(char, 10);
        if (__indexOf.call(SRS_SCORE_CHOICES, score) >= 0) {
          return $popup.find(".choice[data-score=\"" + score + "\"]").trigger('click');
        }
      });
    };
    hideWordScorePopup = function(el) {
      $popup = $('#word-score-popup');
      $popup.removeClass('visible');
      $popupChoices.off('click');
      return $(document).off('keyup keypress');
    };
    attachAnnotationControls = function($el) {
      $popup = $('#word-score-popup');
      return $el.click(function(e) {
        return selectWord(this);
      });
    };
    return attachAnnotationControls($('.annotated-word-list li:not([data-group-label="ignored"])'));
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
