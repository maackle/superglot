var coffee = require('gulp-coffee');
var concat = require('gulp-concat');
var gulp = require('gulp');
var livereload = require('gulp-livereload');
var path = require('path');
var sass = require('gulp-sass');

var lrPort = 35729;

var paths = {
    'src': './assets/',
    'srcStyles': './assets/styles/',
    'dest': './superglot/static/build/',
    'templates': './superglot/templates/',
};

var files = {
    'coffee': './assets/scripts/*.coffee',
    'jadeMixins': 'superglot/components/**/*.mixin.jade',
    'sass': './assets/styles/*.scss',
    'sassComponents': './superglot/components/**/*.scss',
};

gulp.task('jade-mixins', function() {
    gulp.src([files.jadeMixins])
        .pipe(concat('mixins-collected.jade'))
        .pipe(gulp.dest(paths.templates))
});

gulp.task('sass-collect', function () {
    return gulp.src(files.sassComponents)
        .pipe(concat('_components.scss'))
        // .pipe(sass())
        .pipe(gulp.dest(path.join(paths.srcStyles, 'build/')));
});

gulp.task('sass', ['sass-collect'], function () {
    gulp.src(files.sass)
        .pipe(sass())
        .pipe(gulp.dest(paths.dest))
        .pipe(livereload({port: lrPort}));
});

gulp.task('coffee', function() {
    gulp.src(files.coffee)
        .pipe(coffee({bare: false}))
        .pipe(gulp.dest(paths.dest));
});

gulp.task('watch', function() {
    livereload.listen();
    gulp.watch(files.jadeMixins, ['jade-mixins']);
    gulp.watch(files.sassComponents, ['sass-collect', 'sass']);
    gulp.watch(files.sass, ['sass']);
    gulp.watch(files.coffee, ['coffee']);
    // gulp.watch('**/*.mixin.jade', ['jade-mixins']);
})

gulp.task('default', [
    'watch',
    'jade-mixins',
    'sass-collect',
    'sass',
    'coffee'
], function() {

});