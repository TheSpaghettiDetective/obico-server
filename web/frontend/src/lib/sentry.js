// extract from @sentry/vue package

const COMPONENT_NAME_REGEXP = /(?:^|[-_/])(\w)/g
const ROOT_COMPONENT_NAME = 'root'
const ANONYMOUS_COMPONENT_NAME = 'anonymous component'

const splitPathRe = /^(\/?|)([\s\S]*?)((?:\.{1,2}|[^/]+?|)(\.[^./]*|))(?:[/]*)$/
const splitPath = (filename) => {
  const parts = splitPathRe.exec(filename)
  return parts ? parts.slice(1) : []
}

const basename = (path, ext) => {
  let f = splitPath(path)[2]
  if (ext && f.substr(ext.length * -1) === ext) {
    f = f.substr(0, f.length - ext.length)
  }
  return f
}

const getComponentName = (vm) => {
  if (!vm) {
    return ANONYMOUS_COMPONENT_NAME
  }

  if (vm.$root === vm) {
    return ROOT_COMPONENT_NAME
  }

  if (!vm.$options) {
    return ANONYMOUS_COMPONENT_NAME
  }

  if (vm.$options.name) {
    return vm.$options.name
  }

  if (vm.$options._componentTag) {
    return vm.$options._componentTag
  }

  // injected by vue-loader
  if (vm.$options.__file) {
    const unifiedFile = vm.$options.__file.replace(/^[a-zA-Z]:/, '').replace(/\\/g, '/')
    const filename = basename(unifiedFile, '.vue')
    return filename.replace(COMPONENT_NAME_REGEXP, (_, c) =>
      c ? c.toUpperCase() : '',
    )
  }

  return ANONYMOUS_COMPONENT_NAME
}

const build = (to, from, prefix, depth, maxDepth, maxKeys) => {
  let c = 0
  for (let key in from) {
    c += 1
    if (c > maxKeys) {
      break
    }
    if (typeof from[key] == 'object') {
      if (maxDepth > depth) {
        build(to, from[key], prefix + '.' + key, depth + 1, maxDepth, maxKeys)
      }
    } else {
      to[prefix + '.' + key] = from[key]
    }
  }
}

const setup = (Vue) => {
  const defaultErrorHandler = Vue.config.errorHandler

  Vue.config.errorHandler = (error, vm, info) => {
    if (window.Sentry) {
      const metadata = {}

      let obj = vm
      if (vm._original) {
        obj = vm._original
      }

      if (obj) {

        try {
          metadata.componentName = getComponentName(obj)
          build(metadata, JSON.parse(JSON.stringify(obj.$options.propsData)), 'props', 0, 2, 10)
        } catch (_oO) {
          console.log('Unable to extract metadata from Vue component.')
        }
      }

      if (info) {
        metadata.lifecycleHook = info
      }

      // Capture exception in the next event loop, to make sure that all breadcrumbs are recorded in time.
      setTimeout(() => {
        window.Sentry.getCurrentHub().withScope(scope => {
          scope.setContext('vue', metadata)
          window.Sentry.getCurrentHub().captureException(error)
        })
      })
    }

    if (typeof defaultErrorHandler === 'function') {
      defaultErrorHandler.call(Vue, error, vm, info)
    }

    if (Vue.util) {
      Vue.util.warn(`Error in ${info}: "${error.toString()}"`, vm)
    }
    console.error(error)
  }
}

export default setup
