(function() {
  var NLP, binarysearch;

  binarysearch = function(a, o) {
    var l, m, u;
    l = 0;
    u = a.length;
    m = void 0;
    while (l <= u) {
      if (o > a[(m = Math.floor((l + u) / 2))]) {
        l = m + 1;
      } else {
        u = (o === a[m] ? -2 : m - 1);
      }
    }
    if (u === -2) {
      return m;
    } else {
      return -1;
    }
  };

  if (typeof window !== "undefined" && window !== null) {
    window.util = {};
  }

  (typeof exports !== "undefined" && exports !== null ? exports : util).binarysearch = binarysearch;

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
