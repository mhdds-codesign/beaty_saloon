<template>
  <div>
    <h2><i class="fas fa-calendar-alt"></i> برنامه کاری آرایشگران / لاین‌ها</h2>

    <div style="margin:1rem 0;">
      <router-link to="/schedules/new" class="btn btn-primary">
        <i class="fas fa-plus"></i> برنامه کاری جدید
      </router-link>
    </div>

    <div v-if="loading" class="loading">در حال بارگذاری...</div>

      <div v-else class="card">
        <div class="card-header">
          <i class="fas fa-table"></i> همه برنامه‌ها ({{ total }})
        </div>
        <div class="card-body" style="padding:0;">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>لاین / خدمت</th>
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
                <td>{{ getWeekdayName(s.weekday) }}</td>
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
        <button class="btn btn-sm" :class="page<=1?'btn-disabled':''" :disabled="page <= 1" @click="goPage(page-1)">قبلی</button>
        <span v-for="n in totalPages" :key="n" class="btn btn-sm" :class="{ 'btn-active': n === page }" @click="goPage(n)">{{ n }}</span>
        <button class="btn btn-sm" :class="page>=totalPages?'btn-disabled':''" :disabled="page >= totalPages" @click="goPage(page+1)">بعدی</button>
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
    }
  },
  async created() {
    await this.load()
  },
  methods: {
    async load() {
      this.loading = true
      try {
        const res = await api.schedules({ page: this.page })
        this.schedules = res.schedules || []
        this.total = res.total || 0
        this.totalPages = res.total_pages || 1
      } catch (e) {
        console.error(e)
        alert('خطا در بارگذاری برنامه کاری')
      } finally {
        this.loading = false
      }
    },

    goPage(n) {
      if (n < 1 || n > this.totalPages) return
      this.page = n
      this.load()
    },

    async doDelete(schedule) {
      if (!confirm(`آیا از حذف این برنامه کاری مطمئن هستید؟`)) return
      try {
        await api.deleteSchedule(schedule.id)
        this.load()
      } catch (e) {
        alert('خطا در حذف')
      }
    },

    getWeekdayName(weekday) {
      const days = ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه']
      return days[weekday] || 'نامشخص'
    },

    getStatusText(status) {
      const map = { free: 'آزاد', busy: 'رزرو شده' }
      return map[status] || status
    },

    getStatusClass(status) {
      const map = { free: 'bg-success', busy: 'bg-warning', reserved: 'bg-danger' }
      return map[status] || 'bg-secondary'
    }
  }
}
</script>