(function() {
  var Superglot, TEXT_NODE_TYPE, bg, port,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  TEXT_NODE_TYPE = 3;

  bg = {
    words: {}
  };

  port = chrome.runtime.connect();

  port.onMessage.addListener(function(msg) {
    switch (msg.id) {
      case 'load-words':
        bg.words = msg.data;
        return $(function() {
          var superglot;
          console.debug('DOM loaded');
          superglot = new Superglot($('body'));
          return superglot.transform();
        });
      default:
        return console.debug('got message: ', msg);
    }
  });

  Superglot = (function() {
    Superglot.prototype.tokenSelector = 'span.sg';

    Superglot.prototype.excludedTags = ['script', 'style', 'iframe', 'head', 'code'];

    function Superglot($root) {
      this.$root = $root;
    }

    Superglot.prototype.tokenize = function(text) {
      return text.split(/\s+|(?=[^a-zA-Z\s]+)/).filter(function(s) {
        return s;
      });
    };

    Superglot.prototype.lemmatize = function(word) {
      return word.toLowerCase().replace(" ", '');
    };

    Superglot.prototype.toggleClassification = function(wordEl) {
      var $el;
      $el = $(wordEl);
      if ($el.hasClass('sg-untracked')) {
        $el.removeClass('sg-untracked');
        return $el.addClass('sg-tracked');
      } else {
        $el.removeClass('sg-tracked');
        return $el.addClass('sg-untracked');
      }
    };

    Superglot.prototype.classify = function(lemma) {
      var w;
      w = lemma;
      if (__indexOf.call(bg.words.common, w) >= 0) {
        return 'sg-common';
      } else if (__indexOf.call(bg.words.tracked, w) >= 0) {
        return 'sg-tracked';
      } else if (bg.words.untracked.binarysearch(w) >= 0) {
        return 'sg-untracked';
      } else {
        return 'sg-unknown';
      }
    };

    Superglot.prototype.bindEvents = function() {
      var _this = this;
      return this.$root.find(this.tokenSelector).on('click', function(e) {
        var $el, lemma;
        $el = $(e.currentTarget);
        lemma = $el.data('lemma');
        _this.$root.find(".sg[data-lemma=" + lemma + "]").each(function(i, el) {
          return _this.toggleClassification(el);
        });
        return port.postMessage({
          action: 'update-word',
          data: {
            lemma: lemma
          }
        });
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
          if (c.nodeType === TEXT_NODE_TYPE && c.length > 2) {
            words = _this.tokenize(c.data);
            tokens = words.map(function(w) {
              var klass, lemma;
              lemma = _this.lemmatize(w);
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

}).call(this);
