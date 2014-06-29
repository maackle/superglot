(function() {
  $(function() {
    return $('.annotated-word-list li').click(function(e) {
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
      return $.post('/api/user/words/update/', {
        lemma: lemma,
        group: newGroup
      }, function(data) {
        if (data) {
          return $("[data-lemma='" + lemma + "']").attr('data-group', newGroup);
        }
      });
    });
  });

}).call(this);
