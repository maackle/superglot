var coffee = require('gulp-coffee');
var concat = require('gulp-concat');
var gulp = require('gulp');
var path = require('path');
var sass = require('gulp-sass');

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

gulp.task('sass', function () {
    gulp.src(files.sassComponents)
        .pipe(concat('_components.scss'))
        // .pipe(sass())
        .pipe(gulp.dest(paths.srcStyles));
    gulp.src(files.sass)
        .pipe(sass())
        .pipe(gulp.dest(paths.dest));
});

gulp.task('coffee', function() {
    gulp.src(files.coffee)
        .pipe(coffee({bare: false}))
        .pipe(gulp.dest(paths.dest));
});

gulp.task('watch', function() {
    gulp.watch(files.jadeMixins, ['jade-mixins']);
    gulp.watch(files.sass, ['sass']);
    gulp.watch(files.coffee, ['coffee']);
    // gulp.watch('**/*.mixin.jade', ['jade-mixins']);
})

gulp.task('default', [
    'watch',
    'jade-mixins',
    'sass',
    'coffee'
]);