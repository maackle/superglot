defaultFilter =
    prefix: ''
    size: 100
    page: 0
    rating: '1,2,3'

ratingInfo = [
    {name: 'Any', rating: '1,2,3', colorClass: ''}
    {name: '1', rating: '1', colorClass: 'background-rating-1'}
    {name: '2', rating: '2', colorClass: 'background-rating-2'}
    {name: '3', rating: '3', colorClass: 'background-rating-3'}
]

unicodeDigit =
    1: "\u2776"
    2: "\u2777"
    3: "\u2778"

DOM = React.DOM

ratingColorClass = (rating, prefix) ->
    if 1 <= rating and rating <= 3
        prefix + '-rating-' + rating
    else
        ''

VocabSearch = React.createClass

    getInitialState: ->
        vocab: []
        filterArgs: defaultFilter
        doneScrolling: false
        stats:
            total: 0
            hits: 0

    updateFilter: (args) ->
        @refreshVocab _.assign @state.filterArgs, args, {
            page: 0
        }

    refreshVocab: (args, append=false) ->
        payload = args
        $.get Flask.url_for('api.vocab_search'), payload,
            (data) =>
                newState = @state
                newState.filterArgs = args
                newState.stats =
                    total: data.total
                    hits: data.hits
                if not append
                    newState.vocab = []
                    newState.doneScrolling = false
                newState.vocab = newState.vocab.concat data.vocab
                if data.vocab.length == 0
                    newState.doneScrolling = true
                @setState newState

    getMoreVocab: ->
        if not @state.doneScrolling
            args = @state.filterArgs
            args.page += 1
            @refreshVocab args, true

    componentDidMount: ->
        @refreshVocab defaultFilter

    render: ->
        {div} = React.DOM

        return \
        div {},
            Toolbar {
                updateFilter: @updateFilter
                filterArgs: @state.filterArgs
                stats: @state.stats
            }
            VocabTable {
                vocab: @state.vocab
                handleInfiniteLoad: @getMoreVocab
            }


Toolbar = React.createClass

    getSortTypes: ->
        alpha: 'A-Z'
        frequency: 'Frequency'

    setRating: (rating) ->
        @props.updateFilter
            rating: rating

    render: ->
        {DOM} = React
        {div, button, ul, li, a, span, label, input} = React.DOM

        return \
        div {},
            div {className:'btn-toolbar', role:'toolbar'},
                div {className:'btn-group', role:'group'},
                    VocabFilter {updateFilter: @props.updateFilter}
                div {className:'btn-group', role:'group'},
                    button {
                        className: 'btn btn-default dropdown-toggle'
                        type: 'button'
                        'data-toggle': 'dropdown'
                    },
                        "A-Z"
                        span {className:'caret'}
                    ul className:'dropdown-menu', role:'menu',
                        li {}, a {href:'#', onClick:""}, "A-Z"
                        li {}, a {href:'#', onClick:""}, "Frequency"
                div {className:'btn-group', role:'group'},
                div {className:'btn-group', role:'group', 'data-toggle':'buttons'},
                    ratingInfo.map (r) =>
                        {name, rating, colorClass} = r
                        activeClass = if rating == (@props.filterArgs.rating) then ' active ' else ''
                        colorClass = ratingColorClass(rating, 'background')
                        label {className:'btn btn-default ' + activeClass + colorClass, onClick: => @setRating(rating)},
                            input {type:'radio'}
                            name
                    # label {className:'btn btn-default'},
                    #     input {type:'radio'}
                    #     1
                    # label {className:'btn btn-default'},
                    #     input {type:'radio'}
                    #     2
                    # label {className:'btn btn-default'},
                    #     input {type:'radio'}
                    #     3
            div {className: 'align-right'},
                DOM.i {}, 'Showing ' + @props.stats.total + ' words'



VocabFilter = React.createClass

    handleInput: ->
        @props.updateFilter
            prefix: @refs.prefixField.getDOMNode().value

    render: ->
        {div, input} = React.DOM

        return \
        div {},
            input
                type:'text'
                ref:'prefixField'
                placeholder: 'Filter'
                onChange: @handleInput


VocabTable = React.createClass

    scrollConfig:
        longDelay: 1000
        shortDelay: 250
        margin: 1200

    updateInfScroll: ->
        $(window).off 'scroll'
        el = @getDOMNode()
        rect = el.getBoundingClientRect()
        bottom = rect.bottom # el.scrollHeight
        if bottom < @scrollConfig.margin
            @props.handleInfiniteLoad()
        $(window).one 'scroll', (e) =>
            _.delay @updateInfScroll, if bottom < @scrollConfig.margin then @scrollConfig.longDelay else @scrollConfig.shortDelay

    componentDidUpdate: ->
        _.delay @updateInfScroll, @scrollConfig.shortDelay

    componentWillUnmount: ->
        $(window).off 'scroll'

    render: ->
        {table, thead, tbody, tr, th, td, a} = React.DOM

        return \
        table {className:'table table-compact vocab-table'},
            thead {},
                tr {},
                    th {}
                    th {}, 'Word'
            tbody {},
                @props.vocab.map (vword) =>
                    tr {key:vword.id},
                        td {className: 'rating ' + ratingColorClass(vword.rating, 'color')}, unicodeDigit[vword.rating]
                        td {className: 'word'},
                            a {
                                href: Flask.url_for('frontend.vocab.word', lemma: vword.word.lemma),
                                className: ''
                            },
                                vword.word.lemma

module.exports =
    VocabTable: VocabTable
    VocabSearch: VocabSearch