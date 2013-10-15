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
        bg.words.tracked = window.corncobWords;
        return $(function() {
          var superglot;
          console.log('DOM loaded');
          superglot = new Superglot($('body'));
          return superglot.transform();
        });
      default:
        return console.log('got message: ', msg);
    }
  });

  Superglot = (function() {
    Superglot.prototype.tokenSelector = 'span.w';

    Superglot.prototype.excludedTags = ['script', 'style', 'iframe', 'head'];

    function Superglot($root) {
      this.$root = $root;
    }

    Superglot.prototype.tokenize = function(text) {
      return text.split(/\s+|(?=[^a-zA-Z\s]+)/).filter(function(s) {
        return s;
      });
    };

    Superglot.prototype.classify = function(word) {
      var w;
      w = word.toLowerCase();
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
        return port.postMessage({
          action: 'mark',
          word: $(e.currentTarget).text()
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
              var klass;
              klass = _this.classify(w);
              return " \n<span class=\"sg " + klass + "\">" + w + "</span>";
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
      return go(this.$root);
    };

    return Superglot;

  })();

}).call(this);
