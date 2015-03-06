
var replaceNode = function ($node) {

};

/** WIP **/
var annotateNode = function ($node, it) {
	var subNodes = $node.contents();
	var onlyChild = subNodes.length == 1;
	var textNodes = subNodes.filter(c => c.nodeType == 3);
	for (let n of textNodes) {
		var text = n.data;
		var index = 0;
		for (var occurrence in it) {
			var index = text.indexOf(occurrence.reading);
			if (index > -1) {
				text = text.substring(index);

				break;
			}
		}
		while (index < 0) {
			var occurrence = it.next();
		}
	}
};