(function() {
  var NLP, Superglot, bg, port, superglot, wordCollection,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  superglot = {};

  bg = {
    lemmata: {}
  };

  NLP = new nlp.NLP;

  wordCollection = function(classification) {
    switch (classification) {
      case 'sg-known':
        return bg.lemmata.known;
      case 'sg-learning':
        return bg.lemmata.learning;
      case 'sg-ignored':
        return bg.lemmata.ignored;
      case 'sg-common':
        return bg.lemmata.common;
      default:
        throw "invalid classification: " + classification;
    }
  };

  port = chrome.runtime.connect();

  port.onMessage.addListener(function(msg) {
    var diff, kind, lemma, lemmata, stats, text, _i, _len, _ref, _results;
    switch (msg.id) {
      case 'load-words':
        bg.lemmata = msg.data.lemmata;
        bg.lemmata.user = new LemmaPartition(bg.lemmata.user);
        return superglot.transform();
      case 'word-diff':
        diff = msg.data.diff;
        kind = diff.addTo;
        bg.lemmata.user.applyDiff(diff);
        _ref = diff.lemmata;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          lemma = _ref[_i];
          _results.push(superglot.updateKind(lemma, kind));
        }
        return _results;
        break;
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

    Superglot.prototype.excludedTags = ['script', 'style', 'iframe', 'head', 'code', 'pre', 'textarea', 'input', 'svg', 'canvas'];

    function Superglot($root) {
      this.$root = $root;
    }

    Superglot.prototype.updateKind = function(lemma, kind) {
      var _this = this;
      return this.$root.find(".sg[data-lemma=" + lemma + "]").each(function(i, el) {
        var k;
        $(el).removeClass(((function() {
          var _i, _len, _ref, _results;
          _ref = enums.KINDS;
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            k = _ref[_i];
            _results.push('sg-' + k);
          }
          return _results;
        })()).join(' '));
        if (kind) {
          return $(el).addClass('sg-' + kind);
        }
      });
    };

    Superglot.prototype.classify = function(lemma) {
      var w;
      w = lemma;
      if (__indexOf.call(bg.lemmata.common, w) >= 0) {
        return 'common';
      } else if (__indexOf.call(bg.lemmata.user.ignored, w) >= 0) {
        return 'ignored';
      } else if (__indexOf.call(bg.lemmata.user.known, w) >= 0) {
        return 'known';
      } else if (__indexOf.call(bg.lemmata.user.learning, w) >= 0) {
        return 'learning';
      } else if (util.binarysearch(bg.lemmata.all, w) >= 0) {
        return 'untracked';
      } else {
        return 'invalid';
      }
    };

    Superglot.prototype.bindEvents = function() {
      var _this = this;
      return this.$root.find(this.tokenSelector).on('click', function(e) {
        var $el, diff, inclusionKind, kind, lemma;
        $el = $(e.currentTarget);
        lemma = $el.data('lemma');
        kind = _this.classify(lemma);
        if (__indexOf.call(enums.STATIC_KINDS, kind) >= 0) {

        } else {
          inclusionKind = e.ctrlKey ? 'known' : 'learning';
          diff = new LemmaDiff({
            lemmata: [lemma],
            removeFrom: kind,
            addTo: (function() {
              switch (kind) {
                case 'common':
                case 'ignored':
                  return kind;
                case inclusionKind:
                  return 'untracked';
                default:
                  return inclusionKind;
              }
            })()
          });
          if (!diff.idempotent()) {
            return port.postMessage({
              action: 'word-diff',
              data: {
                diff: diff
              }
            });
          } else {
            return console.warn('idempotent diff', diff);
          }
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
              var kind, lemma;
              lemma = NLP.lemmatize(w);
              kind = _this.classify(lemma);
              return " \n<span data-lemma=\"" + lemma + "\" class=\"sg sg-" + kind + "\">" + w + "</span>";
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
