var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var merge = require('merge-stream');

gulp.task('sass', function() {
    sassStream = gulp
        .src('app/static/scss/**/*.scss') // Gets all files ending with .scss in app/scss and children dirs
        .pipe(
            sass({
                errLogToConsole: true,
            }),
        );

    return merge(sassStream)
        .pipe(concat('app.css'))
        .pipe(gulp.dest('app/static/css'));
});

gulp.task('watch', function() {
    gulp.watch('app/static/scss/**/*.scss', gulp.series('sass'));
});
