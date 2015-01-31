var React = require("react");

var AnnotatedWord = React.createClass({
	render: () => {
		<h1>hi</h1>
	}
});

var AnnotatedWordList = React.createClass({
	render: () => {
		<ul class="inline-list annotated-words style-a">
			{ this.props.vocab.map( (v) => {
				<li>
					<AnnotatedWord word={v.word} />
				</li>
			})}
		</ul>
	}
});