const BundleTracker = require('webpack-bundle-tracker')
const path = require('path')
const webpack = require('webpack')

let publicPath = process.env.NODE_ENV === 'production'
  ? '/static/frontend' : 'http://172.20.10.6:7070/'
  // ? '/static/frontend' : 'http://localhost:7070/'

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
        main: path.join(__dirname, 'src/main'),
        common: path.join(__dirname, 'src/common'),
        lib: path.join(__dirname, 'src/lib'),
        '@common': path.join(__dirname, 'src/common'),
        '@lib': path.join(__dirname, 'src/lib'),
        '@main': path.join(__dirname, 'src/main'),
        '@static': path.join(__dirname, '../app/static'),
      }
    },
  },

  pages: {
    main: {
      entry: 'src/main/main.js',
    },
    print_shot_feedback: {
      entry: 'src/print_shot_feedback/main.js',
    },
    prints: {
      entry: 'src/prints/main.js',
    },
    printers: {
      entry: 'src/printers/main.js',
    },
    printer_settings: {
      entry: 'src/printers/settings.main.js',
    },
    octoprint_tunnel: {
      entry: 'src/octoprint_tunnel/TunnelMain.js',
    },
    users: {
      entry: 'src/users/main.js',
    },
    common: {
      entry: 'src/common/main.js',
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
