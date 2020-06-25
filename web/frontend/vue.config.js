const BundleTracker = require('webpack-bundle-tracker')
const path = require('path')
const webpack = require('webpack')

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

    configureWebpack: {
      resolve: {
        alias: {
          main: path.join(__dirname, 'src/main'),
          common: path.join(__dirname, 'src/common'),
          lib: path.join(__dirname, 'src/lib'),
        }
      },

    },

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

        config.plugin('ignore-plugin').use(webpack.IgnorePlugin, [/^\.\/locale$/, /moment$/])

        if (process.env.NODE_ENV != 'production') {
            config.optimization
                .splitChunks(false)
        } else {
            config.optimization
                .splitChunks({
                     cacheGroups: {
                       vendors: {
                         name: 'chunk-vendors',
                         test: /[\\/]node_modules[\\/]/,
                         priority: -10,
                         chunks: 'initial'
                       },
                       // common: {
                       //   name: 'chunk-common',
                       //   minChunks: 2,
                       //   priority: -20,
                       //   chunks: 'initial',
                       //   reuseExistingChunk: true
                       // }
                     }
                })
        }

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
