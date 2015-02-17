var browserify = require('browserify');
var coffee = require('gulp-coffee');
var concat = require('gulp-concat');
var es6transpiler = require('gulp-es6-transpiler');
var gulp = require('gulp');
var livereload = require('gulp-livereload');
var reactify = require('reactify');
var path = require('path');
var sass = require('gulp-sass');

var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var sourcemaps = require('gulp-sourcemaps');

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
    'jsx': ['superglot/components/**/*.js', 'superglot/components/**/*.jsx'],
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

// gulp.task('js', function() {
//     gulp.src(files.js)
//         .pipe(es6transpiler())
//         .pipe(gulp.dest(paths.dest));
// });

// gulp.task('jsx', function() {
//     gulp.src(files.jsx)
//         .pipe(react({harmony: true}))
//         .pipe(concat('react-components.js'))
//         .pipe(gulp.dest(paths.dest));
// });

gulp.task('jsx', function() {
  // https://hacks.mozilla.org/2014/08/browserify-and-gulp-with-react/

  var getBundleName = function () {
      var version = require('./package.json').version;
      var name = require('./package.json').name;
      return version + '.' + name + '.' + 'min';
  };

  var bundler = browserify({
    entries: [
      './superglot/components/app.js',
    ],
    debug: true
  });

  var bundle = function() {
    return bundler
      .transform(reactify)
      .bundle()
      .pipe(source(getBundleName() + '.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        // .pipe(react({harmony: true}))
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest(paths.dest));
  };

  return bundle();
});

gulp.task('watch', function() {
    // livereload.listen();
    gulp.watch(files.coffee, ['coffee']);
    gulp.watch(files.jadeMixins, ['jade-mixins']);
    gulp.watch(files.jsx, ['jsx']);
    gulp.watch(files.sassComponents, ['sass-collect', 'sass']);
    gulp.watch(files.sass, ['sass']);
})

gulp.task('default', [
    'watch',
    'coffee',
    'jade-mixins',
    'jsx',
    'sass-collect',
    'sass',
], function() {

});