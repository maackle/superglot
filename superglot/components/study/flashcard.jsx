

var StudyPanel = React.createClass({
    getInitialState: function() {
        return {
            currentCard: 0,
        };
    },
    answerCard: function(answer) {
        if (answer > 0) { // a rating
            // update rating and flip
            this.setState({cardFlipped: true});
        }
    },
    nextCard: function() {

    },
    render: function() {
        var vocab = this.props.vocab;
        return (
            <div className="study-panel">
                <StudyTabs />
                { vocab.map( (v) => (
                    <Flashcard vword={ v }
                               answerCard={ this.answerCard }
                    />
                ))}
            </div>
        )
    }
});

var StudyTabs = React.createClass({
    render: function() {
        return (
            <ul class="">
                <li>tab 1</li>
                <li>tab 2</li>
                <li>tab 3</li>
            </ul>
        )
    }
});

var Flashcard = React.createClass({
    getInitialState: function () {
        return {
            isFlipped: false
        };
    },
    answerCard: function(answer) {
        this.setState({isFlipped: true});
        return this.props.answerCard(answer);
    },
    render: function() {
        var vword = this.props.vword;
        var contents = null;
        var cardClass = this.state.isFlipped ? 'flipped' : '';
        return (
            <div className={ "flashcard " + cardClass }>
                <div className="flashcard-side flashcard-front">
                    <h1 className="prompt">{ vword.word.lemma }</h1>
                    <AnswerSelector selectRating={ this.props.answerCard } selectAction={ this.props.answerCard }/>
                </div>
                <div className="flashcard-side flashcard-back">
                    <h1 className="prompt">{ vword.word.lemma }</h1>
                    <h2 className="answer">(n.) cheeseball</h2>
                    <a onClick={ this.props.nextCard }>next</a>
                </div>
            </div>
        );
    }
});

var AnswerSelector = React.createClass({
    render: function() {

        return (
            <div className="flashcard-answer-selector">
                <ul className="flashcard-answer-set flashcard-answer-ratings">
                    <li data-rating={1} className="review-choice number" onClick={ () => this.props.selectRating(1) }>1</li>
                    <li data-rating={2} className="review-choice number" onClick={ () => this.props.selectRating(2) }>2</li>
                    <li data-rating={3} className="review-choice number" onClick={ () => this.props.selectRating(3) }>3</li>
                </ul>
                <ul className="flashcard-answer-set flashcard-answer-other">
                    <li className="review-choice other" onClick={ () => this.props.selectAction(0) }>&times;</li>
                    <li className="review-choice other" onClick={ () => this.props.selectAction(-1) }>⃠</li>
                    <li className="review-choice other" onClick={ () => this.props.selectAction('bury') }>(bury)</li>
                </ul>
            </div>
        );
    }
});

window.renderFlashcardStudyPane = function(vocab, el) {
    React.withContext({

    }, function() {
        React.render(<StudyPanel vocab={ vocab } />, el);
    })
};