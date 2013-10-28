(function() {
  var DocumentInfo, LemmaDiff, LemmaPartition, NLP, binarysearch, enums, multiBinarySearch, util;

  binarysearch = function(haystack, needle) {
    var l, m, u;
    l = 0;
    u = haystack.length;
    m = void 0;
    while (l <= u) {
      if (needle > haystack[(m = Math.floor((l + u) / 2))]) {
        l = m + 1;
      } else {
        u = (needle === haystack[m] ? -2 : m - 1);
      }
    }
    if (u === -2) {
      return m;
    } else {
      return -1;
    }
  };

  multiBinarySearch = function(haystack, needles) {
    var l, lastHit, m, needle, u, _i, _len, _results;
    l = lastHit = -1;
    _results = [];
    for (_i = 0, _len = needles.length; _i < _len; _i++) {
      needle = needles[_i];
      l = lastHit;
      m = void 0;
      u = haystack.length;
      while (l <= u) {
        if (needle > haystack[(m = Math.floor((l + u) / 2))]) {
          l = m + 1;
        } else {
          u = (needle === haystack[m] ? -2 : m - 1);
        }
      }
      if (u === -2) {
        lastHit = m;
        _results.push(m);
      } else {
        _results.push(-1);
      }
    }
    return _results;
  };

  if (typeof exports !== "undefined" && exports !== null) {
    exports.binarysearch = binarysearch;
    exports.multiBinarySearch = multiBinarySearch;
  } else {
    window.util = {
      binarysearch: binarysearch,
      multiBinarySearch: multiBinarySearch
    };
  }

  if (typeof exports !== "undefined" && exports !== null) {
    util = require('./util');
  } else {
    util = window.util;
  }

  enums = {
    KINDS: ['known', 'learning', 'ignored', 'common', 'untracked'],
    USER_KINDS: ['known', 'learning', 'ignored'],
    STATIC_KINDS: ['common', 'invalid']
  };

  DocumentInfo = (function() {
    DocumentInfo.prototype.language = 'en';

    function DocumentInfo(_arg) {
      this.stats = _arg.stats;
    }

    return DocumentInfo;

  })();

  LemmaPartition = (function() {
    LemmaPartition.prototype.language = 'en';

    LemmaPartition.prototype.known = null;

    LemmaPartition.prototype.learning = null;

    LemmaPartition.prototype.ignored = null;

    function LemmaPartition(_arg) {
      this.known = _arg.known, this.learning = _arg.learning, this.untracked = _arg.untracked;
      this.ignored = "the be to of and a in that have i it for not on with he she him her his hers as you do at this but by from they we or an will my would there their what so its is".split(' ');
    }

    LemmaPartition.prototype.applyDiff = function(diff) {
      var i, kind, lemma, lemmata, source, target, _i, _j, _len, _len1, _ref, _ref1;
      console.assert((diff.removeFrom != null) && (diff.addTo != null));
      source = this[diff.removeFrom];
      target = this[diff.addTo];
      lemmata = diff.lemmata;
      _ref = enums.USER_KINDS;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        kind = _ref[_i];
        source = this[kind];
        _ref1 = (function() {
          var _k, _len1, _results;
          _results = [];
          for (_k = 0, _len1 = lemmata.length; _k < _len1; _k++) {
            lemma = lemmata[_k];
            _results.push(util.binarysearch(source, lemma));
          }
          return _results;
        })();
        for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
          i = _ref1[_j];
          if (i >= 0) {
            source.splice(i, 1);
          }
        }
      }
      if (target != null) {
        target = target.concat(lemmata);
        target.sort();
      }
      this[diff.removeFrom] = source;
      return this[diff.addTo] = target;
    };

    LemmaPartition.prototype.getIntersections = function(lemmata) {
      var intersect;
      intersect = function(list, words) {
        var ixs;
        ixs = util.multiBinarySearch(list, words);
        return words.filter(function(w, i) {
          return ixs[i] >= 0;
        });
      };
      return {
        known: intersect(this.known, lemmata),
        learning: intersect(this.learning, lemmata),
        ignored: intersect(this.ignored, lemmata)
      };
    };

    return LemmaPartition;

  })();

  LemmaDiff = (function() {
    function LemmaDiff(_arg) {
      this.removeFrom = _arg.removeFrom, this.addTo = _arg.addTo, this.lemmata = _arg.lemmata;
    }

    LemmaDiff.prototype.idempotent = function() {
      return (this.addTo === this.removeFrom) || this.lemmata.length === 0;
    };

    return LemmaDiff;

  })();

  (typeof exports !== "undefined" && exports !== null ? exports : window).LemmaPartition = LemmaPartition;

  (typeof exports !== "undefined" && exports !== null ? exports : window).LemmaDiff = LemmaDiff;

  (typeof exports !== "undefined" && exports !== null ? exports : window).enums = enums;

  NLP = (function() {
    function NLP() {}

    NLP.prototype.segment = function(text) {
      return text.split(/\s+|(?=[^a-zA-Z\s]+)/).filter(function(s) {
        return s;
      });
    };

    NLP.prototype.lemmatize = function(token) {
      if (typeof token === 'object') {
        return token.map(this.lemmatize);
      } else {
        return token.toLowerCase().replace(" ", '');
      }
    };

    return NLP;

  })();

  if (typeof window !== "undefined" && window !== null) {
    window.nlp = {};
  }

  (typeof exports !== "undefined" && exports !== null ? exports : nlp).NLP = NLP;

}).call(this);
