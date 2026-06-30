<template>
  <div>
    <h2><i class="fas fa-calendar-check"></i> نوبت‌ها و رزروها</h2>

    <!-- فیلتر و جستجو -->
    <div class="card">
      <div class="card-header"><i class="fas fa-filter"></i> جستجو و فیلتر</div>
      <div class="card-body">
        <div class="d-flex gap-2" style="flex-wrap:wrap;">
          <div style="flex:2;">
            <label>جستجو</label>
            <input v-model="filters.q" placeholder="نام لاین یا سرویس..." />
          </div>
          
          <div style="min-width:150px;">
            <label>وضعیت</label>
            <select v-model="filters.status">
              <option value="">همه وضعیت‌ها</option>
              <option value="confirmed">تایید شده</option>
              <option value="completed">انجام شده</option>
              <option value="cancelled">لغو شده</option>
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
      <router-link to="/reservations/new" class="btn btn-primary">
        <i class="fas fa-plus"></i> نوبت جدید
      </router-link>
    </div>

    <div v-if="loading" class="loading">در حال بارگذاری...</div>

    <div v-else class="card">
      <div class="card-header">
        <i class="fas fa-table"></i> همه نوبت‌ها ({{ total }})
      </div>
      <div class="card-body" style="padding:0;">
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>مشتری</th>
              <th>
                <strong>لاین</strong><br>
                <small>سرویس</small>
              </th>
              <th>تاریخ و زمان</th>
              <th>قیمت</th>
              <th>وضعیت</th>
              <th>عملیات</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="res in reservations" :key="res.id">
              <td>#{{ res.id }}</td>
              <td>{{ res.customer_name || '—' }}</td>
              <td>
                <strong>{{ res.name_line }}</strong><br>
                <small>{{ res.name_service }}</small>
              </td>
              <td>
                {{ res.weekday }}<br>
                <small>{{ res.start_time }} - {{ res.end_time }}</small>
              </td>
              <td>{{ res.price ? res.price.toLocaleString() + ' تومان' : '—' }}</td>
              <td>
                <span class="badge" :class="getStatusClass(res.status)">
                  {{ getStatusText(res.status) }}
                </span>
              </td>
              <td>
                <router-link 
                  :to="`/reservations/${res.id}`" 
                  class="btn btn-sm btn-info"
                >
                  <i class="fas fa-eye"></i>
                </router-link>
                <router-link 
                  :to="`/reservations/${res.id}/edit`" 
                  class="btn btn-sm btn-warning"
                >
                  <i class="fas fa-edit"></i>
                </router-link>
              </td>
            </tr>
            <tr v-if="!reservations.length">
              <td colspan="7" class="text-center py-4">هنوز نوبت ثبت نشده است.</td>
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
  name: 'Reservations',
  data() {
    return {
      reservations: [],
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
        }
        
        if (this.filters.q) params.search = this.filters.q
        if (this.filters.status) params.status = this.filters.status

        const res = await api.reservations(params)
        this.reservations = res.reservations || []
        this.total = res.total || 0
        this.totalPages = res.total_pages || 1
        
        if (this.page > this.totalPages && this.totalPages > 0) {
          this.page = this.totalPages
          await this.load()
        }
      } catch (e) {
        console.error(e)
        alert('خطا در بارگذاری نوبت‌ها: ' + (e.message || ''))
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

    getStatusText(status) {
      const map = {
        pending: 'در انتظار',
        confirmed: 'تایید شده',
        completed: 'انجام شده',
        cancelled: 'لغو شده'
      }
      return map[status] || status
    },

    getStatusClass(status) {
      const map = {
        pending: 'bg-warning',
        confirmed: 'bg-success',
        completed: 'bg-info',
        cancelled: 'bg-danger'
      }
      return map[status] || 'bg-secondary'
    }
  }
}
</script>
