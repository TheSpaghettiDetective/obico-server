import mountVue from '@src/mount'
import { router, components } from '@src/pages'
import store from '@src/store'

mountVue(store, router, components)
