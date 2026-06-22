import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue') },
  { path: '/formula', name: 'formula', component: () => import('../views/Formula.vue') },
  { path: '/equation', name: 'equation', component: () => import('../views/Equation.vue') },
  { path: '/reaction', name: 'reaction', component: () => import('../views/Reaction.vue') },
  { path: '/ion', name: 'ion', component: () => import('../views/Ion.vue') },
  { path: '/live-equation', name: 'live-equation', component: () => import('../views/LiveEquation.vue') },
  { path: '/structure', name: 'structure', component: () => import('../views/StructureViewer.vue') },
  { path: '/mol-editor', name: 'mol-editor', component: () => import('../views/MolEditor.vue') },
  { path: '/database', name: 'database', component: () => import('../views/Database.vue') },
  { path: '/providers', name: 'providers', component: () => import('../views/Providers.vue') },
  { path: '/plugins', name: 'plugins', component: () => import('../views/Plugins.vue') },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue') },
  { path: '/:pathMatch(.*)*', name: 'not-found', redirect: '/' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
