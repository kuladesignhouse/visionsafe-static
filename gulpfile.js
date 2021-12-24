const gulp = require('gulp');
const nunjucks = require('gulp-nunjucks');
var sitemap = require('gulp-sitemap'); 

exports.default = () => (
    gulp.src('templates/*.html')
        .pipe(nunjucks.compile())
        .pipe(gulp.dest('dist'))
);

gulp.task('sitemap', function () {
  return gulp.src('dist/**/*.html', {
      read: false
    })
    .pipe(sitemap({
      siteUrl: 'https://www.visionsafe.com'
    }))
    .pipe(gulp.dest('dist'));
});