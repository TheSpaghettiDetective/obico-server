const BundleTracker = require("webpack-bundle-tracker");

let vueConfig = {
    publicPath: process.env.NODE_ENV === 'production'
      ? '/static/vue-demo'
      : 'http://localhost:7070/',
    outputDir: process.env.NODE_ENV === 'production'
      ? '/app/static_build/vue-demo'
      : '/app/dev-builds/vue-demo',
    runtimeCompiler: true,
    filenameHashing: false,

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
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": "*"})
            }

        };

module.exports = vueConfig;
