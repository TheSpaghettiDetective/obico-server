var path = require('path')
var webpack = require('webpack')

const VueLoaderPlugin = require('vue-loader/lib/plugin')

// webpack.config.js
const cssModuleRegex = /\.module\.css$/;
const cssRegex = /\.css$/;

module.exports = function(webpackEnv) {
	// const isEnvDevelopment = webpackEnv === 'development';
	// const isEnvProduction = webpackEnv === 'production';
	
	return {
		module: {
			rules: [
				{
					test: /\.vue$/,
					loader: 'vue-loader',
					options: {
						loaders: {
							'scss': 'vue-style-loader!css-loader!sass-loader',
							'sass': 'vue-style-loader!css-loader!sass-loader?indentedSyntax'
						}
						// other vue-loader options go here
					}
				},
				{
					test: /\.css$/,
					use: [
						'vue-style-loader',
						'css-loader'
					],
				},
				{ 
					test: /vendor\/.+\.(jsx|js)$/,
					loader: 'imports?jQuery=jquery,$=jquery,this=>window'
				},
				{ test: /\.jsx?$/, loader: 'babel-loader' },
				{
					test: /\.scss$/,
					use: [
						{
							loader: "style-loader" // creates style nodes from JS strings
						},
						{
							loader: "css-loader", // translates CSS into CommonJS
							options:{
								sourceMap: true
							}
						}, 
						{
							loader: "sass-loader", // compiles Sass to CSS
							options:{
								sourceMap: true
							}
						}]
				},
				{
					test: /\.sass$/,
					use: [
						'vue-style-loader',
						'css-loader',
						'sass-loader?indentedSyntax'
					],
				},
				{
					test: /\.js$/,
					loader: 'babel-loader',
					exclude: /node_modules/
				},
				{
					test: /.(png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/,
					loader: 'url-loader',
					options: {
						name: '[name].[ext]?[hash]'
					}
				}
			]
			},
		resolve: {
			alias: {
					'vue$': 'vue/dist/vue.esm.js',
					'jquery': 'jquery/src/jquery.js'
			},
			extensions: ['*', '.js', '.vue', '.json']
		},
		plugins: [
			// make sure to include the plugin for the magic
			new VueLoaderPlugin()
		],
		devtool: '#eval-source-map'
	}
};