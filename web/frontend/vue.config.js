const BundleTracker = require("webpack-bundle-tracker");

let vueConfig = {
    publicPath: "http://localhost:8080/", // The base URL your application bundle will be deployed at
    outputDir: './builds', //The directory where the production build files will be generated in when running vue-cli-service build
    runtimeCompiler: true,

    pages: {
        simple: {
            entry: 'src/simple/main.js',
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

        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{filename: 'webpack-stats.json', path: '/code/builds/'}])

        config.resolve.alias
            .set('__STATIC__', 'static')

        config.devServer
            .public('http://0.0.0.0:8080')
            .host('0.0.0.0')
            .port(8080)
            .inline(true)
            .clientLogLevel("debug")
            .progress(true)
            .hotOnly(true)
            .watchOptions({poll: true})
            .https(false)
            .headers({"Access-Control-Allow-Origin": "*"})
            }

        };

module.exports = vueConfig;
