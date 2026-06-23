<template>
  <div>
    <h2><i class="fas fa-box"></i> خدمات و لاین‌ها</h2>

    <!-- فیلتر و جستجو -->
    <div class="card">
      <div class="card-header"><i class="fas fa-filter"></i> جستجو و فیلتر</div>
      <div class="card-body">
        <div class="d-flex gap-2" style="flex-wrap:wrap;">
          <div style="flex:2;">
            <label>جستجو</label>
            <input v-model="filters.q" placeholder="نام لاین یا خدمت..." />
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
      <router-link to="/lines/new" class="btn btn-primary">
        <i class="fas fa-plus"></i> خدمت / لاین جدید
      </router-link>
    </div>

    <!-- مرتب‌سازی -->
    <div class="sort-controls">
      <span>مرتب‌سازی بر اساس:</span>
      <button 
        v-for="s in sortOptions" 
        :key="s.key" 
        class="btn btn-sm" 
        :class="{ 'btn-active': filters.sort === s.key }"
        @click="filters.sort = s.key; load()"
      >
        {{ s.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">در حال بارگذاری...</div>

    <template v-else>
      <div class="card">
        <div class="card-header">
          <i class="fas fa-table"></i> همه خدمات ({{ total }})
        </div>
        <div class="card-body" style="padding:0;">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>نام لاین</th>
                <th>نام خدمت</th>
                <th>قیمت</th>
                <th>مدت زمان (دقیقه)</th>
                <th>عملیات</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="line in lines" :key="line.id">
                <td>#{{ line.id }}</td>
                <td>{{ line.name_line }}</td>
                <td>{{ line.name_service }}</td>
                <td>{{ line.price ? line.price.toLocaleString() + ' تومان' : '—' }}</td>
                <td>{{ line.duration || '—' }}</td>
                <td>
                  <router-link 
                    :to="`/lines/${line.id}/edit`" 
                    class="btn btn-warning btn-sm"
                  >
                    <i class="fas fa-edit"></i>
                  </router-link>
                  <button 
                    class="btn btn-danger btn-sm" 
                    @click="doDelete(line)"
                  >
                    <i class="fas fa-trash-alt"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!lines.length">
                <td colspan="6" class="text-center py-4">هنوز خدمتی ثبت نشده است.</td>
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
    </template>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Lines',
  data() {
    return {
      lines: [],
      total: 0,
      page: 1,
      totalPages: 1,
      loading: true,
      filters: { 
        sort: 'default',q: '' 
      },
      sortOptions: [
        { key: 'default', label: 'پیش‌فرض' },
        { key: 'name_line', label: 'نام لاین' },
        { key: 'name_service', label: 'نام خدمت' },
        { key: 'price', label: 'قیمت' }
      ]
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
          sort: this.filters.sort, 
          page: this.page 
        }
        if (this.filters.q) params.q = this.filters.q

        const res = await api.lines(params)
        
        this.lines = res.lines || []
        this.total = res.total || 0
        this.totalPages = res.total_pages || 1
      } catch (e) {
        console.error(e)
        alert('خطا در بارگذاری خدمات: ' + (e.message || ''))
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
      this.filters = { sort: 'default', q: '' }
      this.page = 1
      this.load()
    },

    async doDelete(line) {
      if (!confirm(`آیا از حذف خدمت "${line.name_service}" مطمئن هستید؟`)) return
      
      try {
        await api.deleteLine(line.id)
        alert('خدمت با موفقیت حذف شد')
        this.load()
      } catch (e) {
        alert('خطا در حذف: ' + (e.message || ''))
      }
    }
  }
}
</script>