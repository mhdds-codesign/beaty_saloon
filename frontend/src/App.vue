<template>
  <div id="app-shell">
    <nav class="navbar" v-if="loggedIn">
      <div class="container">
        <router-link to="/" class="navbar-brand">
         <i class="fas fa-spa" style="margin-left: 9px; color: #f0dce8;"></i>پنل مدیریت رز بیوتی (rose beauty)
        </router-link>
        
        <ul class="navbar-nav">
          <li>
            <router-link to="/">
              <i class="fas fa-chart-pie"></i> داشبورد
            </router-link>
          </li>
          <li>
            <router-link to="/customers">
              <i class="fas fa-users"></i> مشتریان
            </router-link>
          </li>
          <li>
            <router-link to="/lines">
              <i class="fas fa-cut"></i> سرویس ها و لاین‌ها
            </router-link>
          </li>
          <li>
            <router-link to="/reservations">
              <i class="fas fa-calendar-check"></i> نوبت ها
            </router-link>
          </li>
          <li>
            <router-link to="/schedules">
              <i class="fas fa-clock"></i> برنامه کاری
            </router-link>
          </li>

          <li class="nav-right">
            <a href="#" @click.prevent="doLogout" style="color:#f87171;">
              <i class="fas fa-sign-out-alt"></i> خروج
            </a>
          </li>
        </ul>
      </div>
    </nav>

    <main class="container" style="margin-top: 2rem;">
      <router-view />
    </main>
  </div>
</template>

<script>
import api from './api.js'
import { auth, loadAuth, clearAuth } from './auth.js'

export default {
  data() {
    return {
      loggedIn: false,
      auth,
    }
  },
  async created() {
    try {
      await loadAuth()
      this.loggedIn = true
    } catch {
      this.loggedIn = false
      }
  },
  methods: {
    async doLogout() {
      await api.logout()
      clearAuth()
      this.loggedIn = false
      this.$router.push('/login')
    },
  },
}
</script>