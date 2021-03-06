﻿var gulp = require('gulp'),
	//less = require('gulp-less'),
	autoprefixer = require('gulp-autoprefixer'),
	plumber = require('gulp-plumber'),
	uglify = require('gulp-uglify'),
	//gutil = require('gulp-util'),
	htmlify = require('gulp-angular-htmlify'),
	iife = require('gulp-iife'),
	concat = require('gulp-concat'),
	ngAnnotate = require('gulp-ng-annotate'),
	watch = require('gulp-watch'),
	livereload = require('gulp-livereload'),
	serve = require('gulp-serve');

gulp.task('js-deps', function () {
  gulp.src([
	'./bower_components/jquery/dist/jquery.js',
	'./bower_components/mousetrap/mousetrap.min.js',
	'./bower_components/lodash/lodash.js',
	'./bower_components/angular/angular.js',
	'./bower_components/angular-ui-router/release/angular-ui-router.min.js',
	'./bower_components/angular-bootstrap/ui-bootstrap-tpls.js'
  ])
	.pipe(concat('deps.js'))
	.pipe(ngAnnotate())
	.pipe(uglify())
	//.pipe(uglify().on('error', gutil.log))
	.pipe(gulp.dest('./build/js'));
});

gulp.task('partials', function () {
  gulp.src('./app/modules/**/*.html')
	.pipe(htmlify({
	  customPrefixes: ['ui-']
	}))
	.pipe(gulp.dest('./build/partials'))
	.pipe(livereload());
});

gulp.task('css-deps', function () {
  gulp.src([
	"./bower_components/bootstrap/dist/css/bootstrap.min.css",
	"./bower_components/font-awesome/css/font-awesome.min.css"
  ])
	.pipe(concat('css-deps.css'))
	.pipe(gulp.dest('./build/css'));

  gulp.src('./bower_components/font-awesome/fonts/*')
	.pipe(gulp.dest('./build/fonts'));
});

gulp.task('js', function () {
  var baseDir = __dirname + '/app/modules',
	outputDir = __dirname + '/build/js',
	outputFilename = 'app.js';

  gulp.src([
	baseDir + "/*module.js",
	baseDir + "/**/*module.js",
	baseDir + "/**/*.js"
  ])
	.pipe(iife())
	.pipe(concat(outputFilename))
	.pipe(ngAnnotate())
	.pipe(uglify())
	.pipe(gulp.dest(outputDir))
	.pipe(livereload());
});


gulp.task('serve', serve('.'));

gulp.task('watch', function () {
  livereload.listen();
  watch(['./app/modules/*.js', './app/modules/**/*.js'], function () {
	gulp.start('js');
  });

  watch(['./app/modules/*.html', './app/modules/**/*.html'], function () {
	gulp.start('partials');
  });
});

gulp.task('default', ['js-deps', 'partials', 'css-deps', 'js', 'watch', 'serve']);