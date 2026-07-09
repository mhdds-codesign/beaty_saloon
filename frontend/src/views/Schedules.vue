<template>
  <div>
    <h2><i class="fas fa-calendar-alt"></i> برنامه کاری لاین‌ها</h2>

    <!-- فیلتر و جستجو -->
    <div class="card">
      <div class="card-header"> جستجو و فیلتر</div>
      <div class="card-body">
        <div class="d-flex gap-2" style="flex-wrap:wrap;">
          <div style="flex:2;">
            <label>جستجو</label>
            <input v-model="filters.q" placeholder="نام لاین..." />
          </div>
          
          <div style="min-width:150px;">
            <label>وضعیت</label>
            <select v-model="filters.status">
              <option value="">همه وضعیت‌ها</option>
              <option value="free">آزاد</option>
              <option value="busy">رزرو شده</option>
            </select>
          </div>
          
          <div style="align-self:flex-end;">
            <button class="btn btn-primary" @click="load">
              <i class="fas fa-search"></i> جستجو
            </button>
            <button class="btn btn-secondary" @click="resetFilters">
              <i class="fas fa-undo-alt"></i> پاک کردن
            </button>
          </div>
        </div>
      </div>
    </div>

    <div style="margin:1rem 0;">
      <router-link to="/schedules/new" class="btn btn-primary">
        <i class="fas fa-plus"></i> برنامه کاری جدید
      </router-link>
    </div>

    <div v-if="loading" class="loading">در حال بارگذاری...</div>

    <div v-else class="card">
      <div class="card-header">
       همه برنامه‌ها ({{ total }})
      </div>
      <div class="card-body" style="padding:0;">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>لاین </th>
              <th>روز هفته</th>
              <th>ساعت شروع</th>
              <th>ساعت پایان</th>
              <th>وضعیت</th>
              <th>عملیات</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in schedules" :key="s.id">
              <td>#{{ s.id }}</td>
              <td>{{ s.line_name || '—' }}</td>
              <td>{{ s.weekday }}</td>
              <td>{{ s.start_time }}</td>
              <td>{{ s.end_time }}</td>
              <td>
                <span class="badge" :class="getStatusClass(s.status)">
                  {{ getStatusText(s.status) }}
                </span>
              </td>
              <td>
                <router-link 
                  :to="`/schedules/${s.id}/edit`" 
                  class="btn btn-warning btn-sm"
                >
                  <i class="fas fa-edit"></i>
                </router-link>
                <button 
                  class="btn btn-danger btn-sm" 
                  @click="doDelete(s)"
                >
                  <i class="fas fa-trash-alt"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!schedules.length">
              <td colspan="7" class="text-center py-4">هنوز برنامه کاری ثبت نشده است.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        class="btn btn-sm" 
        :class="page<=1?'btn-disabled':''"
        :disabled="page <= 1"
        @click="goPage(page-1)"
      >
        &larr; قبلی
      </button>
      
      <span 
        v-for="n in totalPages" 
        :key="n" 
        class="btn btn-sm" 
        :class="{ 'btn-active': n === page }"
        @click="goPage(n)"
      >
        {{ n }}
      </span>
      
      <button 
        class="btn btn-sm" 
        :class="page>=totalPages?'btn-disabled':''"
        :disabled="page >= totalPages"
        @click="goPage(page+1)"
      >
        بعدی &rarr;
      </button>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Schedules',
  data() {
    return {
      schedules: [],
      total: 0,
      page: 1,
      totalPages: 1,
      loading: true,
      filters: {
        q: '',
        status: ''
      }
    }
  },
  async created() {
    await this.load()
  },
  methods: {
    async load() {
      this.loading = true
      try {
        const params = {
          page: this.page,
          per_page: 20
        }
        
        if (this.filters.q) params.search = this.filters.q
        if (this.filters.status) params.status = this.filters.status

        const res = await api.schedules(params)
        this.schedules = res.schedules || []
        this.total = res.total || 0
        this.totalPages = res.total_pages || 1
        
        if (this.page > this.totalPages && this.totalPages > 0) {
          this.page = this.totalPages
          await this.load()
        }
      } catch (e) {
        console.error(e)
        alert('خطا در بارگذاری برنامه کاری: ' + (e.message || ''))
      } finally {
        this.loading = false
      }
    },

    goPage(n) {
      if (n < 1 || n > this.totalPages) return
      this.page = n
      this.load()
    },

    resetFilters() {
      this.filters = { q: '', status: '' }
      this.page = 1
      this.load()
    },

    async doDelete(schedule) {
      if (!confirm(`آیا از حذف این برنامه کاری مطمئن هستید؟`)) return
      try {
        await api.deleteSchedule(schedule.id)
        this.load()
      } catch (e) {
        alert('خطا در حذف: ' + (e.message || ''))
      }
    },

    getStatusText(status) {
      const map = { free: 'آزاد', busy: 'رزرو شده' }
      return map[status] || status
    },

    getStatusClass(status) {
      const map = { free: 'bg-success', busy: 'bg-danger', reserved: 'bg-warning' }
      return map[status] || 'bg-secondary'
    }
  }
}
</script>