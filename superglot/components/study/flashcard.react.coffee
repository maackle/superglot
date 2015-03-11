FlashcardStudySession = React.createClass
    getInitialState: ->
        currentCard: 0

    finishStudying: ->
        console.log('TODO: no more cards!')

    answerCard: (answer) ->
        if answer > 0  # a rating
            $.post Flask.url_for('api.update_word'), {
                lemmata: lemmataString
                rating: rating
            }, after
            @setState({cardFlipped: true})

    advanceCard: ->
        nextCard = @state.currentCard + 1
        @setState
            currentCard: nextCard

        if nextCard >= @props.vocab.length
            @finishStudying()

    render: ->
        vocab = this.props.vocab;
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

        div className: 'study-panel',
            StudyStatusTabs {}
            div className: 'flashcard-stack',
                cards

StudyStatusTabs = React.createClass
    render: ->
        {ul, li} = React.DOM
        ul {},
            li {}, 'tab 1'
            li {}, 'tab 2'
            li {}, 'tab 3'

Flashcard = React.createClass
    getInitialState: ->
        isFlipped: false
    answerCard: (answer) ->
        console.log('card answer', answer)
        @setState isFlipped: true
        this.props.answerCard(answer)
    render: ->
        {div, h1, h2, a} = React.DOM
        vword = @props.vword
        contents = null
        cardClass = @props.status
        if @state.isFlipped
            cardClass += ' flipped'

        div {className: 'flashcard ' + cardClass},
            div {className:'flashcard-side flashcard-front'},
                h1 {className: 'prompt'}, vword.word.lemma
                AnswerSelector {selectRating: @answerCard, selectAction: @answerCard}
            div className:"flashcard-side flashcard-back",
                h1 {className:"prompt"}, vword.word.lemma
                h2 {className:"answer"}, '(n.) cheeseball'
                a {onClick: @props.advanceCard}, 'next'

AnswerSelector = React.createClass
    render: ->
        {div, ul, li} = React.DOM

        div className:"flashcard-answer-selector",
            ul className:"flashcard-answer-set flashcard-answer-ratings",
                li {'data-rating':1, className:"review-choice number", onClick: () => @props.selectRating(1)}, 1
                li {'data-rating':2, className:"review-choice number", onClick: () => @props.selectRating(2)}, 2
                li {'data-rating':3, className:"review-choice number", onClick: () => @props.selectRating(3)}, 3
            ul className:"flashcard-answer-set flashcard-answer-other",
                li {className:"review-choice other", onClick:() => @props.selectAction(0)}, '×'
                li {className:"review-choice other", onClick:() => @props.selectAction(-1)}, '⃠'
                li {className:"review-choice other", onClick:() => @props.selectAction('bury')}, 'bury'

window.Superglot.renderFlashcardStudySession = (vocab, el) ->
    React.withContext {}, ->
        React.render (FlashcardStudySession {vocab: vocab}), el
