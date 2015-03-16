el = (dom, className, children) ->
    dom {className: className}, children

FlashcardStudySession = React.createClass
    getInitialState: ->
        currentCard: 0
        vocab: @props.initialVocab.map (v) =>
            v.isFlipped = false
            v

    finishStudying: ->
        console.log('TODO: no more cards!')

    getRatingCounts: ->
        _.countBy @state.vocab, (v) => v.rating

    getCurrentVocabWord: ->
        @state.vocab[@state.currentCard]

    getMeaningByLemma: (lemma) ->
        console.log 'git it', lemma
        @props.meanings[lemma]

    answerCard: (answer) ->
        vword = @getCurrentVocabWord()
        rating = answer
        $.post Flask.url_for('api.update_word'),
            lemmata: vword.word.lemma
            rating: rating
            =>
                vword.isFlipped = true
                @setState vocab: @state.vocab

            # =>
            #     # TODO: no need to make a whole roundtrip for this
            #     $.get Flask.url_for('api.due_vocab'),
            #         (data) =>
            #             @setState vocab: data.due_vocab

    advanceCard: ->
        nextCard = @state.currentCard + 1
        @setState
            currentCard: nextCard

        if nextCard >= @state.vocab.length
            @finishStudying()

    render: ->
        vocab = @state.vocab;
        {div} = React.DOM

        cards = vocab.map (v, i) =>
            if i == @state.currentCard
                status = 'current'
            else if i < @state.currentCard
                status = 'completed'
            else
                status = 'upcoming'

            Flashcard
                vword: v
                meaning: @getMeaningByLemma(v.word.lemma)
                status: status
                answerCard: @answerCard
                advanceCard: @advanceCard

        return \
        div className: 'study-panel',
            StudyStatusTabs
                ratingCounts: @getRatingCounts()
                vword: @getCurrentVocabWord()
            div className: 'flashcard-stack',
                cards


Flashcard = React.createClass
    render: ->
        {div, h1, h2, a} = React.DOM
        vword = @props.vword
        contents = null
        assemblyClass = ' ' + @props.status
        cardClass = if vword.isFlipped then ' flipped' else ''

        return \
        div {className: 'flashcard-assembly' + assemblyClass + cardClass},
            div {className: 'flashcard '},
                div {className:'flashcard-side flashcard-front'},
                    h1 {className: 'prompt'}, vword.word.lemma
                div className:"flashcard-side flashcard-back",
                    h1 {className:"prompt"}, vword.word.lemma
                    h2 {className:"answer"}, @props.meaning
            div {className: 'flashcard-controls'},
                div {className:'pre-answer'},
                    AnswerSelector
                        selectRating: @props.answerCard
                        selectAction: @props.answerCard
                div {className:'post-answer'},
                    a {className:"next", onClick: @props.advanceCard}, '›'


StudyStatusTabs = React.createClass

    render: ->
        {ul, li, div} = React.DOM
        numbers =
            1: 'one'
            2: 'two'
            3: 'three'
        countTabs = [1, 2, 3].map (n) =>
            iconColor = if @props.vword.rating == n then "background-rating-#{n}" else ''
            countColor = ''  # "color-rating-#{n}"
            li {className: 'flashcard-status-tab'},
                div {className: "count #{countColor}"}, @props.ratingCounts[n] or 0
                div {className: "icon icon-die-#{numbers[n]} #{iconColor}"}

        return \
        ul {className: 'flashcard-status'},
            countTabs


AnswerSelector = React.createClass
    render: ->
        {div, ul, li} = React.DOM

        return \
        div className:"flashcard-answer-selector",
            ul className:"flashcard-answer-set flashcard-answer-ratings",
                li {'data-rating':1, className:"review-choice number", onClick: () => @props.selectRating(1)}, 1
                li {'data-rating':2, className:"review-choice number", onClick: () => @props.selectRating(2)}, 2
                li {'data-rating':3, className:"review-choice number", onClick: () => @props.selectRating(3)}, 3
            ul className:"flashcard-answer-set flashcard-answer-other",
                li {className:"review-choice other", onClick:() => @props.selectAction(0)}, '×'
                li {className:"review-choice other", onClick:() => @props.selectAction(-1)}, '⃠'
                # li {className:"review-choice other", onClick:() => @props.selectAction('bury')}, 'bury'

window.Superglot.renderFlashcardStudySession = (el) ->
    $.get Flask.url_for('api.due_vocab'), (data) =>
        $.post Flask.url_for('api.translate_words'),
            word_ids: data.due_vocab.map (v) => v.word.id
            (translations) =>
                component = FlashcardStudySession
                    initialVocab: data.due_vocab
                    meanings: translations.meanings
                React.withContext {}, => React.render component, el
