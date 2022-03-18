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
    devtool: 'source-map',
    resolve: {
      alias: {
        '@src': path.join(__dirname, 'src'),
        '@config': path.join(__dirname, 'src/config'),
        '@static': path.join(__dirname, 'static'),
      }
    },
  },

  pages: {
    root: {
      entry: 'src/main.js',
    },
    styles: {
      entry: 'src/styles/index.js',
    },
  },

  chainWebpack: config => {
    Object.keys(vueConfig.pages).forEach(function (key) {
      config.plugins.delete('html-' + key)
      config.plugins.delete('preload-' + key)
      config.plugins.delete('prefetch-' + key)
    })

    config.plugin('ignore-plugin').use(webpack.IgnorePlugin, [/^\.\/locale$/, /moment$/])
    config.plugin('provide-plugin').use(webpack.ProvidePlugin, [{adapter: 'webrtc-adapter'}])

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
      .clientLogLevel('debug')
      .progress(true)
      .hotOnly(true)
      .watchOptions({ poll: 1000 })
      .https(false)
      .headers({ 'Access-Control-Allow-Origin': '*' })
  }

}

module.exports = vueConfig
