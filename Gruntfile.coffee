module.exports = (grunt) ->

	grunt.initConfig

		paths:
			# common:
			# 	src: "common/assets"
			# 	dest: "common/build"
			server:
				templates: "./templates"
				src: "./assets"
				dest: "./static/build"

		pkg: grunt.file.readJSON("package.json")

		watch:
			livereload:
				files: [
					"<%= paths.server.dest %>/**/*.css"
					# "<%= paths.server.templates %>/**/*"
				]
				options:
					livereload: 54739
			js:
				files: ["<%= paths.server.src %>/scripts/{,**}/*.coffee"]
				tasks: ["coffee"]
			sass:
				files: ["<%= paths.server.src %>/styles/{,**}/*.{sass,scss}"]
				tasks: ["compass"]


		coffee:
			compile:
				options:
					join: true
				files: [
					"<%= paths.server.dest %>/main.js": [
						"<%= paths.server.src %>/scripts/util.coffee"
						"<%= paths.server.src %>/scripts/main.coffee"
						"<%= paths.server.src %>/scripts/*.coffee"
					]
				]


		compass:
			dist:
				options:
					noLineComments: false
					# debugInfo: true
					sassDir: '<%= paths.server.src %>/styles'
					cssDir: '<%= paths.server.dest %>/'
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