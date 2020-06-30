module.exports = {
  env: {
    browser: true,
    es6: true
  },
  extends: [
    // this one is stricter: 'plugin:vue/strongly-recommended',
    'plugin:vue/essential',
    'eslint:recommended',
  ],
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly'
  },
  parserOptions: {
    ecmaVersion: 11,
    sourceType: 'module',
    parser: 'babel-eslint'
  },
  plugins: [
    'vue'
  ],
  rules: {
    'quotes': ['error', 'single'],
    'semi': ['error', 'never'],
    'indent': ['error', 2],
    'no-multi-spaces': ['error']
  }
}
