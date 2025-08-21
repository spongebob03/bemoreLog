import { createRouter, createWebHistory } from 'vue-router'
import MandalartTable from '../components/MandalartTable.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MandalartTable
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
