<template>
  <div class="card" style="max-width: 420px; margin: 4rem auto;">
    <div class="card-header">
      <i class="fas fa-lock"></i> Admin Login
    </div>
    <div class="card-body">
      <div v-if="error" class="error-msg">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>

      <form @submit.prevent="doLogin">
        <div class="form-group">
          <label><i class="fas fa-user"></i> نام کاربری</label>
          <input
            v-model="username"
            type="text"
            required
            autofocus
            placeholder="نام کاربری"
          />
        </div>

        <div class="form-group">
          <label><i class="fas fa-key"></i> رمز عبور</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="رمز عبور"
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary"
          style="width: 100%;"
          :disabled="loading"
        >
          <i class="fas fa-sign-in-alt"></i>
          {{ loading ? 'در حال ورود...' : 'ورود' }}
        </button>
      </form>

      <div class="text-center mt-3">
        <small class="text-muted">سالن زیبایی - پنل مدیریت</small>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: null,
      loading: false
    }
  },
  methods: {
    async doLogin() {
      this.loading = true
      this.error = null

      try {
        await api.login(this.username, this.password)
        
        // بعد از لاگین موفق به داشبورد می‌رویم
        this.$router.push('/')
        
      } catch (e) {
        this.error = e.message || 'نام کاربری یا رمز عبور اشتباه است'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>