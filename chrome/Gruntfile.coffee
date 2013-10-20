module.exports = (grunt) ->

	src = "src"

	grunt.initConfig

		pkg: grunt.file.readJSON("package.json")

		watch:
			# options:
			# 	livereload: true
			js:
				files: ["#{src}/coffee/*.coffee", "../common/*.coffee"]
				tasks: ["coffee"]
			css:
				files: ["#{src}/sass/*.{sass,scss}"]
				tasks: ["sass"]
			jade:
				files: ["#{src}/jade/*.jade"]
				tasks: ["jade"]
			copy:
				files: ["#{src}/*"]
				tasks: ["copy"]
			http:
				files: ["#{src}/**", "../common/*.coffee"]
				tasks: ["shell:chrome-reload"]

		coffee:
			compile:
				options:
					join: true
				files: 
					"build/common.js": [
						"../common/util.coffee"
						"../common/nlp.coffee"
					] 
					"build/main.js": [
						"#{src}/coffee/main.coffee"
					] 
					"build/background.js": [
						"#{src}/coffee/background.coffee"
					]

		sass:
			dist:
				options:
					style: 'expanded'
				files:
					"build/main.css": "#{src}/sass/main.sass"


		jade:
			dist:
				options:
					pretty: true
				files: [{
					expand: true
					cwd: 'src/jade'
					dest: "build"
					src: '*.jade'
					ext: '.html'
				}]

		copy:
			dist:
				files: [
					{
						expand: true
						cwd: "#{src}/"
						src: "*"
						dest: 'build/'
						filter: "isFile"
					}
					{
						src: "bower_components/zepto/zepto.min.js"
						dest: "build/lib/zepto.min.js"
					}
					{
						src: "bower_components/async/lib/async.js"
						dest: "build/lib/async.js"
					}
					{
						src: "bower_components/underscore/underscore.js"
						dest: "build/lib/underscore.js"
					}
				]

		shell:
			'chrome-reload':
				command: 'google-chrome --app=http://reload.extensions'

	grunt.loadNpmTasks("grunt-contrib-coffee")
	grunt.loadNpmTasks("grunt-contrib-watch")
	grunt.loadNpmTasks("grunt-contrib-sass")
	grunt.loadNpmTasks('grunt-contrib-jade')
	grunt.loadNpmTasks('grunt-contrib-copy')
	grunt.loadNpmTasks('grunt-shell')
	grunt.loadNpmTasks("grunt-notify")

	grunt.registerTask "default", [
		"jade"
		"coffee"
		"sass"
		"copy"
		"shell:chrome-reload"
		"watch"
	]

# npm install --save-dev \
# grunt-contrib-coffee \
# grunt-contrib-watch \
# grunt-contrib-sass \
# grunt-contrib-jade \
# grunt-contrib-copy \
# grunt-notify