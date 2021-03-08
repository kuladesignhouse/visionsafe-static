const gulp = require('gulp');
const nunjucks = require('gulp-nunjucks');
 
exports.default = () => (
    gulp.src('templates/*.html')
        .pipe(nunjucks.compile())
        .pipe(gulp.dest('dist'))
);