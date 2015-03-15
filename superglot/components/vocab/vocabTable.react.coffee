
VocabSearch = React.createClass

    getInitialState: ->
        vocab: []
        query: ''

    filterVocab: ->
        console.debug 'filtering vocab', arguments

    refreshVocab: ->
        $.get Flask.url_for('api.vocab_search'),
            query: @state.query
            (data) =>
                console.log 'got vocab', data
                @setState vocab: data.vocab

    componentDidMount: ->
        @refreshVocab()

    render: ->
        {div} = React.DOM

        return \
        div {},
            VocabFilter {onChange: @filterVocab}
            VocabTable {vocab: @state.vocab}



VocabFilter = React.createClass

    render: ->
        {div, input} = React.DOM

        return \
        div {},
            input {type:'text', onChange: @props.onChange}


VocabTable = React.createClass

    render: ->
        {table, thead, tbody, tr, th, td} = React.DOM

        return \
        table {className:'table'},
            thead {},
                tr {},
                    th {}, 'Word'
            @props.vocab.map (vword) =>
                tr {},
                    td {}, vword.word.lemma

module.exports =
    VocabTable: VocabTable
    VocabSearch: VocabSearch