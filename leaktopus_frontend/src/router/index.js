import { createRouter, createWebHashHistory } from 'vue-router'
import ScansView from '../views/ScansView.vue'

const routes = [
  {
    path: '/',
    name: 'scans',
    component: ScansView
  },
  {
    path: '/github-preferences',
    name: 'github-prefs',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/GithubPrefsView.vue')
  },
  {
    path: '/leaks',
    name: 'leaks',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/LeaksView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
