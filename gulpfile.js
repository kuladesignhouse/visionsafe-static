const gulp = require('gulp');
const nunjucks = require('gulp-nunjucks');
var sitemap = require('gulp-sitemap'); 

var reduce = require('gulp-reduce-async');
var rename = require('gulp-rename');
var S = require('string');
const algoliasearch = require("algoliasearch");
const fs = require('fs');

const client = algoliasearch("5W8GUD0LSX", "5d6cd55900f74e28578d20964aee4231");
const algoliaIndex = client.initIndex("visionsafe_dev");

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

gulp.task("send-index-to-algolia", function() {
  const index = JSON.parse(fs.readFileSync("./PagesIndex.json", "utf8"));
  return algoliaIndex.saveObjects(index);
});

gulp.task("index-site", (cb) => {
  var pagesIndex = [];

  return gulp.src("dist/*.html")
    .pipe(reduce(function(memo, content, file, cb) {

      //var section      = S(file.path).chompLeft(file.cwd + "/dist").between("/", "/").s,
      var  title        = S(content).between("<title>", "</title>").collapseWhitespace().chompRight(" | VisionSafe | EVAS").s,
        pageContent  = S(content).between('<div id="alg"></div>', '<div id="algend"></div>').stripTags().collapseWhitespace().s,
        href         = S(file.path).chompLeft(file.cwd + "/dist").s,
        pageInfo     = new Object(),
        isRestricted = false,
        blacklist    = [
          "/page/",
          "/tags/",
          "/tags/",
          "/pages/index.html",
          "/thanks",
          "404"
        ];

      // Skips post index page
      if (title === "Posts") {
        isRestricted = true;
      }

      // fixes homepage title
      if (href === "/warranty-RENAME-index.html") {
        href === "/warranty/index.html";
      }

      // remove trailing 'index.html' from qualified paths
      if (href.indexOf("/index.html") !== -1) {
        href = S(href).strip("index.html").s;
      }

      // determine if this file is restricted
      for (const ignoredString of blacklist) {
        if (href.indexOf(ignoredString) !== -1) {
          isRestricted = true;
          break;
        }
      }

      // only push files that aren't ignored
      if (!isRestricted) {
        pageInfo["objectID"] = href;
        //pageInfo["section"] = section;
        pageInfo["title"]   = title;
        pageInfo["href"]    = href;
        pageInfo["content"] = pageContent;

        pagesIndex.push(pageInfo);
      }

      cb(null, JSON.stringify(pagesIndex));
    }, "{}"))
    .pipe(rename("PagesIndex.json"))
    .pipe(gulp.dest("./"));
});