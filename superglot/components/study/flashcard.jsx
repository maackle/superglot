

var StudyPanel = React.createClass({
    answerWord: function() {

    },
    render: function() {
        var vocab = this.props.vocab;
        return (
            <div className="study-panel">
                <StudyTabs />
                <Flashcard vword={ vocab[0] }
                           answerWord={ this.answerWord }/>
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
    getInitialState: function() {
        return {
            isFlipped: false
        };
    },
    render: function() {
        var vword = this.props.vword;
        var contents = null;
        var cardClass = this.props.isFlipped ? 'back' : 'front';
        if (this.state.isFlipped) {
            contents = (
                <div>
                    <h1>{ vword.word.lemma }</h1>
                    <h2>You answered it.</h2>
                </div>
            );
        } else {
            contents = (
                <div>
                    <h1>{ vword.word.lemma }</h1>
                    <AnswerSelector selectRating={ this.props.answerWord }/>
                </div>
            );
        }
        return (
            <div className={ "card " + cardClass }>
                { contents }
            </div>
        );
    }
});

var AnswerSelector = React.createClass({
    selectRating: function(rating) {

    },
    render: function() {

        return (
            <div className="flashcard-answer-selector">
                <ul className="flashcard-answer-set flashcard-answer-ratings">
                    <li data-rating={1} className="review-choice number" onClick={ this.props.selectRating(1) }>1</li>
                    <li data-rating={2} className="review-choice number" onClick={ this.props.selectRating(2) }>2</li>
                    <li data-rating={3} className="review-choice number" onClick={ this.props.selectRating(3) }>3</li>
                </ul>
                <ul className="flashcard-answer-set flashcard-answer-other">
                    <li className="review-choice other">⃠</li>
                    <li className="review-choice other">&times;</li>
                    <li className="review-choice other">(bury)</li>
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