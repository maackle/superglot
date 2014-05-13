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
					"build/main.js": [
						"#{src}/coffee/common.coffee"
						"#{src}/coffee/main.coffee"
					]
					"build/background.js": [
						"#{src}/coffee/common.coffee"
						"#{src}/coffee/background.coffee"
					]
					"build/popup.js": [
						"#{src}/coffee/common.coffee"
						"#{src}/coffee/popup.coffee"
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
						expand: true
						cwd: "#{src}/images/"
						src: "*"
						dest: 'build/images/'
						filter: "isFile"
					}
					{
						src: "bower_components/jquery/jquery.js"
						dest: "build/lib/jquery.js"
					}
					{
						src: "bower_components/async/lib/async.js"
						dest: "build/lib/async.js"
					}
					{
						src: "bower_components/lodash/dist/lodash.min.js"
						dest: "build/lib/lodash.min.js"
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