module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset'
  ],
  plugins: [
    [
      'component',
      {
        libraryName: 'maz-ui',
        styleLibraryName: 'css'
      }
    ]
  ]
}
