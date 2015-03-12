el = (dom, className, children) ->
    dom {className: className}, children

FlashcardStudySession = React.createClass
    getInitialState: ->
        currentCard: 0

    finishStudying: ->
        console.log('TODO: no more cards!')

    getRatingCounts: ->
        _.countBy @props.vocab, (v) => v.rating

    answerCard: (answer) ->
        vword = @props.vocab[@state.currentCard]
        if answer > 0  # a rating
            $.post Flask.url_for('api.update_word'),
                lemmata: vword.word.lemma
                rating: answer
                =>
                    @setState({cardFlipped: true})

    advanceCard: ->
        nextCard = @state.currentCard + 1
        @setState
            currentCard: nextCard

        if nextCard >= @props.vocab.length
            @finishStudying()

    render: ->
        vocab = @props.vocab;
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
                status: status
                answerCard: @answerCard
                advanceCard: @advanceCard

        return \
        div className: 'study-panel',
            StudyStatusTabs {ratingCounts: @getRatingCounts()}
            div className: 'flashcard-stack',
                cards

StudyStatusTabs = React.createClass

    render: ->
        {ul, li, span} = React.DOM

        return \
        ul {className: 'flashcard-status'},
            li {className: 'flashcard-status-tab'},
                span {className: 'background-rating-1 icon icon-die-one'}
                span {className: 'count'}, @props.ratingCounts[1]
            li {className: 'flashcard-status-tab'},
                span {className: 'background-rating-2 icon icon-die-two'}
                span {className: 'count'}, @props.ratingCounts[2]
            li {className: 'flashcard-status-tab'},
                span {className: 'background-rating-3 icon icon-die-three'}
                span {className: 'count'}, @props.ratingCounts[3]

Flashcard = React.createClass
    getInitialState: ->
        isFlipped: false
    answerCard: (answer) ->
        console.log('card answer', answer)
        @setState isFlipped: true
        @props.answerCard(answer)
    render: ->
        {div, h1, h2, a} = React.DOM
        vword = @props.vword
        contents = null
        assemblyClass = ' ' + @props.status
        cardClass = if @state.isFlipped then ' flipped' else ''

        return \
        div {className: 'flashcard-assembly' + assemblyClass},
            div {className: 'flashcard ' + cardClass},
                div {className:'flashcard-side flashcard-front'},
                    h1 {className: 'prompt'}, vword.word.lemma
                div className:"flashcard-side flashcard-back",
                    h1 {className:"prompt"}, vword.word.lemma
                    h2 {className:"answer"}, '[answer]'
                    a {onClick: @props.advanceCard}, 'next'
            div {className: 'flashcard-controls'},
                AnswerSelector
                    selectRating: @answerCard
                    selectAction: @answerCard

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
                li {className:"review-choice other", onClick:() => @props.selectAction('bury')}, 'bury'

window.Superglot.renderFlashcardStudySession = (el) ->
    $.get Flask.url_for('api.due_vocab'),
        (data) =>
            console.log data
            component = FlashcardStudySession
                vocab: data.due_vocab
            React.withContext {}, =>
                React.render component, el
