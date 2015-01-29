var gulp = require('gulp');
var concat = require('gulp-concat');
var sass = require('gulp-sass');

var paths = {
	'src': './assets/',
	'dest': './superglot/static/build/',
	'templates': './superglot/templates/',
};

var files = {
	'jadeMixins': 'superglot/components/**/*.mixin.jade',
	'sass': './assets/styles/*.scss',
};

gulp.task('jade-mixins', function() {
  gulp.src([files.jadeMixins])
    .pipe(concat('mixins-collected.jade'))
    .pipe(gulp.dest(paths.templates))
});

gulp.task('sass', function () {
    gulp.src(files.sass)
        .pipe(sass())
        .pipe(gulp.dest(paths.dest));
});

gulp.task('watch', function() {
	gulp.watch(files.jadeMixins, ['jade-mixins']);
	gulp.watch(files.sass, ['sass']);
	// gulp.watch('**/*.mixin.jade', ['jade-mixins']);
})

gulp.task('default', ['watch', 'jade-mixins', 'sass']);