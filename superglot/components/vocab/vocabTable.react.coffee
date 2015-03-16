defaultFilter =
    prefix: ''
    size: 100
    page: 0
    rating: null

ratingInfo = [
    {name: 'Any', rating: null, colorClass: ''}
    {name: '1', rating: 1, colorClass: 'background-rating-1'}
    {name: '2', rating: 2, colorClass: 'background-rating-2'}
    {name: '3', rating: 3, colorClass: 'background-rating-3'}
]

console.log ratingInfo

ratingColorClass = (rating, prefix) ->
    if 1 <= rating and rating <= 3
        prefix + '-rating-' + rating
    else
        ''

VocabSearch = React.createClass

    getInitialState: ->
        vocab: []
        filterArgs: defaultFilter
        stats:
            total: 0

    updateFilter: (args) ->
        @refreshVocab _.assign @state.filterArgs, args

    refreshVocab: (args) ->
        payload = args
        $.get Flask.url_for('api.vocab_search'), payload,
            (data) =>
                console.log 'got vocab', data
                @setState
                    filterArgs: args
                    vocab: data.vocab
                    stats:
                        total: data.total

    componentDidMount: ->
        console.debug 'mounted'
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
            }


Toolbar = React.createClass

    getSortTypes: ->
        alpha: 'A-Z'
        frequency: 'Frequency'

    setRating: (rating) ->
        console.debug 'sat rating', rating
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
                        console.log colorClass, r
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

    render: ->
        {table, thead, tbody, tr, th, td} = React.DOM

        return \
        table {className:'table table-compact'},
            # thead {},
            #     tr {},
            #         th {}, 'Word'
            tbody {},
                @props.vocab.map (vword) =>
                    tr {key:vword.id},
                        td {className: ratingColorClass(vword.rating, 'color')}, vword.word.lemma

module.exports =
    VocabTable: VocabTable
    VocabSearch: VocabSearch