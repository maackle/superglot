(function() {
  var SRS_RATING_CHOICES, addMeaningTooltip, markWords, setupAnnotation,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  SRS_RATING_CHOICES = [1, 2, 3, 4];

  markWords = function(lemmata, rating, after) {
    var lemmataString;
    if (rating === 'known') {
      rating = 4;
    } else if (rating === 'learning') {
      rating = 2;
    }
    rating = parseInt(rating, 10);
    lemmataString = lemmata.join("\n");
    return $.post('/api/user/words/update/', {
      lemmata: lemmataString,
      rating: rating
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
    $popup = $('#word-rating-popup');
    $popupChoices = $popup.find('.ratings .choice');
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
    updateWord = function(el, rating) {
      var lemma;
      lemma = $(el).attr('data-lemma');
      return markWords([lemma], rating, function(data) {
        var $set;
        if (data) {
          $set = $(".word[data-lemma='" + lemma + "']");
          $set.attr('data-rating', rating);
          return deselectWords();
        }
      });
    };
    setPopupScore = function(rating) {
      $popupChoices.removeClass('selected');
      return $popupChoices.filter("[data-rating=" + rating + "]").addClass('selected');
    };
    showWordScorePopup = function(el) {
      $popup.addClass('visible').focus();
      $popup.find('.lemma').text($(el).attr('data-lemma'));
      setPopupScore($(el).attr('data-rating'));
      $popupChoices.click(function(e) {
        var rating;
        rating = parseInt($(this).attr('data-rating'), 10);
        setPopupScore(rating);
        return updateWord(el, rating);
      });
      $(document).on('keyup', function(e) {
        if (e.keyCode === 27) {
          return deselectWords();
        }
      });
      return $(document).on('keypress', function(e) {
        var char, rating;
        char = String.fromCharCode(e.keyCode);
        rating = parseInt(char, 10);
        if (__indexOf.call(SRS_RATING_CHOICES, rating) >= 0) {
          return $popup.find(".choice[data-rating=\"" + rating + "\"]").trigger('click');
        }
      });
    };
    hideWordScorePopup = function(el) {
      $popup = $('#word-rating-popup');
      $popup.removeClass('visible');
      $popupChoices.off('click');
      return $(document).off('keyup keypress');
    };
    attachAnnotationControls = function($el) {
      $popup = $('#word-rating-popup');
      return $el.click(function(e) {
        return selectWord(this);
      });
    };
    return attachAnnotationControls($('.annotated-words .word:not([data-rating="-1"])'));
  };

  $(function() {
    setupAnnotation();
    $('.annotated-words .controls .mark-all').click(function(e) {
      var $affected, label, lemmata;
      label = $(this).attr('data-group-label');
      $affected = $('.annotated-words .word').filter(function(i, el) {
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
      var $el, el, wordId;
      el = this;
      $el = $(el);
      wordId = $el.data('id');
      if ($el.data('translation') === void 0) {
        $(el).data('translation', '');
        return $.get('/api/words/translate/', {
          word_id: wordId
        }, (function(_this) {
          return function(data) {
            var meaning;
            meaning = data.target;
            addMeaningTooltip(el, meaning);
            $el.data('translation', meaning);
            return $el.trigger('mouseenter');
          };
        })(this));
      }
    });
    return $('.accordion').accordion({
      header: '.header',
      collapsible: true
    });
  });

}).call(this);
