(function() {
  var NLP, Superglot, bg, port, superglot, wordCollection,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  superglot = {};

  bg = {
    words: {}
  };

  NLP = new nlp.NLP;

  wordCollection = function(classification) {
    switch (classification) {
      case 'sg-known':
        return bg.words.known;
      case 'sg-untracked':
        return bg.words.untracked;
      case 'sg-common':
        return bg.words.common;
      default:
        throw "invalid classification: " + classification;
    }
  };

  port = chrome.runtime.connect();

  port.onMessage.addListener(function(msg) {
    var classification, collection, lemma, lemmata, loser, stats, text, _i, _len, _ref, _ref1;
    switch (msg.id) {
      case 'load-words':
        bg.words = msg.data;
        console.log(bg.words);
        return superglot.transform();
      case 'update-word':
        _ref = msg.data, lemma = _ref.lemma, classification = _ref.classification;
        superglot.updateClassification(lemma, classification);
        collection = wordCollection(classification);
        _ref1 = bg.words;
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          loser = _ref1[_i];
          _.without(loser, lemma);
        }
        collection.push(lemma);
        return collection.sort();
      case 'show-stats':
        text = msg.text;
        lemmata = _.uniq(NLP.lemmatize(NLP.segment(text)));
        stats = {
          known: _.intersection(lemmata, bg.words.known),
          untracked: _.intersection(lemmata, bg.words.untracked),
          invalid: _.intersection(lemmata, bg.words.invalid)
        };
        return console.log(stats);
      default:
        return console.warn('got invalid message: ', msg);
    }
  });

  Superglot = (function() {
    Superglot.prototype.tokenSelector = 'span.sg';

    Superglot.prototype.excludedTags = ['script', 'style', 'iframe', 'head', 'code'];

    function Superglot($root) {
      this.$root = $root;
    }

    Superglot.prototype.updateClassification = function(lemma, klass) {
      var _this = this;
      return this.$root.find(".sg[data-lemma=" + lemma + "]").each(function(i, el) {
        $(el).removeClass('sg-known sg-untracked');
        return $(el).addClass(klass);
      });
    };

    Superglot.prototype.toggleClassification = function(wordEl) {
      var $el;
      $el = $(wordEl);
      if ($el.hasClass('sg-untracked')) {
        $el.removeClass('sg-untracked');
        return $el.addClass('sg-known');
      } else {
        $el.removeClass('sg-known');
        return $el.addClass('sg-untracked');
      }
    };

    Superglot.prototype.classify = function(lemma) {
      var w;
      w = lemma;
      if (__indexOf.call(bg.words.common, w) >= 0) {
        return 'sg-common';
      } else if (__indexOf.call(bg.words.known, w) >= 0) {
        return 'sg-known';
      } else if (util.binarysearch(bg.words.untracked, w) >= 0) {
        return 'sg-untracked';
      } else {
        return 'sg-invalid';
      }
    };

    Superglot.prototype.bindEvents = function() {
      var _this = this;
      return this.$root.find(this.tokenSelector).on('click', function(e) {
        var $el, lemma;
        $el = $(e.currentTarget);
        lemma = $el.data('lemma');
        if ($el.hasClass('sg-untracked')) {
          return port.postMessage({
            action: 'add-word',
            data: {
              lemma: lemma
            }
          });
        } else if ($el.hasClass('sg-known')) {
          return port.postMessage({
            action: 'remove-word',
            data: {
              lemma: lemma
            }
          });
        }
      });
    };

    Superglot.prototype.transform = function() {
      var go,
        _this = this;
      go = function($node) {
        var c, contents, html, onlyChild, tokens, words, _i, _len, _ref, _results;
        contents = $node.contents();
        onlyChild = contents.length === 1;
        _results = [];
        for (_i = 0, _len = contents.length; _i < _len; _i++) {
          c = contents[_i];
          if (c.nodeType === 3 && c.length > 2) {
            words = NLP.segment(c.data);
            tokens = words.map(function(w) {
              var klass, lemma;
              lemma = NLP.lemmatize(w);
              klass = _this.classify(lemma);
              return " \n<span data-lemma=\"" + lemma + "\" class=\"sg " + klass + "\">" + w + "</span>";
            });
            html = tokens.join('');
            if (onlyChild) {
              _results.push($node.html(html));
            } else {
              _results.push($(c).after(html).remove());
            }
          } else {
            if (_ref = c.nodeName.toLowerCase(), __indexOf.call(_this.excludedTags, _ref) < 0) {
              _results.push(go($(c)));
            } else {
              _results.push(void 0);
            }
          }
        }
        return _results;
      };
      this.$root.addClass('superglot');
      go(this.$root);
      return this.bindEvents();
    };

    return Superglot;

  })();

  $(function() {
    console.debug('superglot: DOM loaded');
    return superglot = new Superglot($('body'));
  });

}).call(this);
