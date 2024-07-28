import mountVue from '@src/mount'
import { router, components } from '@src/pages'
import store from '@entSrc/sliceSettings/state' 

mountVue(router, components, store)
