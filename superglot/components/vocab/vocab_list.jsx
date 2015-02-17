var React = require("react");

var AnnotatedWord = React.createClass({
	render: function () {
		var word = this.props.word;
		return (
			<span
			className="annotated-word"
			data-lemma="{ word.lemma }"
			data-rating="{ word.rating }">
				{ this.props.word.reading }
			</span>
		)
	}
});

var AnnotatedWordList = React.createClass({
	render: function () {
		var vocab = this.props.vocab;
		return (
			<ul className="inline-list annotated-words style-a">
				{ vocab.map( v =>
					<li>
						<AnnotatedWord word={ v } />
					</li>
				)}
			</ul>
		)
	}
});

window.renderVocabList = function(vocab, el) {
	React.render(
		<AnnotatedWordList vocab={ vocab } />,
		el
	);
};