module.exports = (grunt) ->

	grunt.initConfig

		paths:
			templates: "templates"
			src: "assets"
			dest: "static/build"

		pkg: grunt.file.readJSON("package.json")

		watch:
			livereload:
				files: [
					"<%= paths.dest %>/**/*.css"
					# "<%= paths.templates %>/**/*"
				]
				options:
					livereload: 54739
			js:
				files: ["<%= paths.src %>/scripts/{,**}/*.coffee"]
				tasks: ["coffee"]
			sass:
				files: ["<%= paths.src %>/styles/{,**}/*.{sass,scss}"]
				tasks: ["compass"]


		coffee:
			compile:
				options:
					join: true
				files: [
					"<%= paths.dest %>/main.js": [
						"<%= paths.src %>/scripts/util.coffee"
						"<%= paths.src %>/scripts/main.coffee"
						"<%= paths.src %>/scripts/*.coffee"
					]
					# {
					# 	expand: true # Enable dynamic expansion.
					# 	cwd: "<%= paths.src %>/coffee/pages/" # Src matches are relative to this path.
					# 	src: ["*.coffee"] # Actual pattern(s) to match.
					# 	dest: "<%= paths.dest %>/scripts/pages/" # Destination path prefix.
					# 	ext: ".js" # Dest filepaths will have this extension.
					# }
				]


		compass:
			dist:
				options:
					noLineComments: false
					# debugInfo: true
					sassDir: '<%= paths.src %>/styles'
					cssDir: '<%= paths.dest %>/'
					environment: 'development'
					require: [
						'susy'
						'bootstrap-sass'
						# 'breakpoint'
					]

		copy:
			dist:
				files: [

				]


	grunt.loadNpmTasks("grunt-contrib-coffee")
	grunt.loadNpmTasks("grunt-contrib-watch")
	grunt.loadNpmTasks("grunt-contrib-compass")
	# grunt.loadNpmTasks('grunt-contrib-copy')
	grunt.loadNpmTasks("grunt-notify")

	grunt.registerTask "default", [
		"coffee"
		"compass"
		"watch"
	]


# npm install --save-dev \
# grunt-contrib-coffee \
# grunt-contrib-watch \
# grunt-contrib-sass \
# grunt-contrib-copy \
# grunt-notify