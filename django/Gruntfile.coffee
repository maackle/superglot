module.exports = (grunt) ->


    # Project configuration.
    grunt.initConfig
        pkg: grunt.file.readJSON('package.json')

        config:
            app: 'mockup'
            dist: 'mockup'

        connect:
            server:
                options:
                    port: 1337
                    base: '<%= config.dist %>'

        watch:
            coffee:
                files: ["<%= config.app %>/coffee/{,**}/*.coffee"]
                tasks: ['coffee']
            compass:
                files: ["<%= config.app %>/sass/{,**}/*.{sass,scss}"]
                tasks: ['compass']

        coffee:
            options:
                join: true
            compile:
                files:
                    "<%= config.dist %>/static/scripts/main.js": [
                        "<%= config.app %>/coffee/*",
                        "<%= config.app %>/coffee/app.coffee",
                    ] # // compile and concat into single file

        compass:
            dist:
                options:
                    sassDir: "<%= config.app %>/sass/",
                    cssDir: "<%= config.dist %>/static/styles/",
                    environment: 'production'


    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.loadNpmTasks('grunt-contrib-copy')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-compass')
    grunt.loadNpmTasks('grunt-notify')

    #// Default task(s).
    grunt.registerTask 'default', [
        'build'
        'watch'
    ]

    grunt.registerTask 'build', [
        'coffee:compile'
        'compass:dist'
    ]