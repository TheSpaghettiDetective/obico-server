const BundleTracker = require("webpack-bundle-tracker");

let publicPath = process.env.NODE_ENV === 'production'
    ? '/static/frontend' : 'http://localhost:7070/'

let outputDir = process.env.NODE_ENV === 'production'
    ? './builds/frontend' : './dev-builds/frontend'

publicPath = process.env.PUBLIC_PATH || publicPath
outputDir = process.env.OUTPUT_DIR || outputDir

let vueConfig = {
    publicPath: publicPath,
    outputDir: outputDir,
    runtimeCompiler: true,
    filenameHashing: false,
    css: { sourceMap: true },

    pages: {
        main: {
            entry: 'src/main/main.js',
        },
        simple: {
            entry: 'src/simple/main.js',
        },
        multi: {
            entry: 'src/multi/main.js',
        },
        print_shot_feedback: {
            entry: 'src/print_shot_feedback/main.js',
        },
        prints: {
            entry: 'src/prints/main.js',
        },
    },

    chainWebpack: config => {
        Object.keys(vueConfig.pages).forEach(function (key) {
            config.plugins.delete('html-' + key);
            config.plugins.delete('preload-' + key);
            config.plugins.delete('prefetch-' + key);
        });

        config.optimization
            .splitChunks(false)

        if (process.env.NODE_ENV != 'production') {
            config
                .plugin('BundleTracker')
                .use(BundleTracker, [{
                    name: 'webpack-stats.json',
                    path: '.'
                }])
        }

        config.resolve.alias
            .set('__STATIC__', 'static')

        config.devServer
            .public('http://0.0.0.0:7070')
            .host('0.0.0.0')
            .port(7070)
            .inline(true)
            .clientLogLevel("debug")
            .progress(true)
            .hotOnly(true)
            .watchOptions({ poll: 1000 })
            .https(false)
            .headers({ "Access-Control-Allow-Origin": "*" })
    }

};

module.exports = vueConfig;
