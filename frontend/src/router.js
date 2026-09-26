import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import LaneView from './views/LaneView.vue'
import JobDetailView from './views/JobDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/lane', name: 'lane', component: LaneView },
    { path: '/jobs/:id', name: 'job-detail', component: JobDetailView, props: true },
  ],
})

export default router
