import mountVue from '@src/mount'
import { routes, components } from '@src/pages'
import store from '@src/store'

mountVue(store, routes, components)
