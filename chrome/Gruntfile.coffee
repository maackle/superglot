module.exports = (grunt) ->

	src = "src"

	grunt.initConfig

		pkg: grunt.file.readJSON("package.json")

		watch:
			# options:
			# 	livereload: true
			js:
				files: ["#{src}/coffee/*.coffee"]
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

		coffee:
			compile:
				options:
					join: true
				files: 
					"build/main.js": [
						"#{src}/coffee/main.coffee",
					] 
					"build/background.js": [
						"#{src}/coffee/background.coffee",
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
						dest: "build/zepto.min.js"
					}
				]

	grunt.loadNpmTasks("grunt-contrib-coffee")
	grunt.loadNpmTasks("grunt-contrib-watch")
	grunt.loadNpmTasks("grunt-contrib-sass")
	grunt.loadNpmTasks('grunt-contrib-jade')
	grunt.loadNpmTasks('grunt-contrib-copy')
	grunt.loadNpmTasks("grunt-notify")

	grunt.registerTask "default", [
		"jade"
		"coffee"
		"sass"
		"copy"
		"watch"
	]

# npm install --save-dev \
# grunt-contrib-coffee \
# grunt-contrib-watch \
# grunt-contrib-sass \
# grunt-contrib-jade \
# grunt-contrib-copy \
# grunt-notify