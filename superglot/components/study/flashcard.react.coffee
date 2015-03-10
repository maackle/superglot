StudyPanel = React.createClass
    getInitialState: ->
        currentCard: 0
    answerCard: (answer) ->
        if answer > 0  # a rating
            # update rating and flip
            @setState({cardFlipped: true})
    nextCard: -> {

    }
    render: ->
        vocab = this.props.vocab;
        {div} = React.DOM
        cards = vocab.map (v) =>
            Flashcard {vword: v, answerCard: @answerCard}, []

        div className: 'study-panel',
            StudyTabs {}
            cards

StudyTabs = React.createClass
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
        @setState isFlipped: true
        this.props.answerCard(answer)
    render: ->
        {div, h1, h2, a} = React.DOM
        vword = @props.vword
        contents = null
        cardClass = if @state.isFlipped then 'flipped' else ''
        div {className: 'flashcard' + cardClass},
            div {className:'flashcard-side flashcard-front'},
                h1 {className: 'prompt'}, vword.word.lemma
                AnswerSelector {selectRating: @props.answerCard, selectAction: @props.answerCard}
            div className:"flashcard-side flashcard-back",
                h1 {className:"prompt"}, vword.word.lemma
                h2 {className:"answer"}, '(n.) cheeseball'
                a {onClick: @props.nextCard}, 'next'

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

window.renderFlashcardStudyPane = (vocab, el) ->
    React.withContext {}, ->
        React.render (StudyPanel {vocab: vocab}), el
