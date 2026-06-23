<template>
  <div>
    <h2><i class="fas fa-users"></i> مشتریان</h2>

    <div style="margin:1rem 0;">
      <router-link to="/customers/new" class="btn btn-primary">
        <i class="fas fa-plus"></i> مشتری جدید
      </router-link>
    </div>

    <!-- مرتب‌سازی -->
    <div class="sort-controls">
      <span>مرتب‌سازی بر اساس:</span>
      <button 
        v-for="s in sortOptions" 
        :key="s.key" 
        class="btn btn-sm" 
        :class="{ 'btn-active': sort === s.key }"
        @click="sort = s.key; load()"
      >
        {{ s.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">در حال بارگذاری...</div>

    <div v-else class="card">
      <div class="card-header">
        <i class="fas fa-table"></i> همه مشتریان ({{ total }})
      </div>
      <div class="card-body" style="padding:0;">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>نام</th>
              <th>شماره تلفن</th>
              <th>تاریخ ثبت</th>
              <th>آدرس</th>
              <th>عملیات</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in customers" :key="c.id">
              <td>#{{ c.id }}</td>
              <td>{{ c.name }}</td>
              <td>{{ c.phone_number || '—' }}</td>
              <td>{{ c.register_date ? c.register_date.slice(0,10) : '—' }}</td>
              <td style="max-width: 250px;">
                <small>{{ c.address ? c.address.substring(0, 60) + '...' : '—' }}</small>
              </td>
              <td>
                <router-link 
                  :to="`/customers/${c.id}/edit`" 
                  class="btn btn-warning btn-sm"
                >
                  <i class="fas fa-edit"></i>
                </router-link>
                <button 
                  class="btn btn-danger btn-sm" 
                  @click="doDelete(c)"
                >
                  <i class="fas fa-trash-alt"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!customers.length">
              <td colspan="6" class="text-center py-4">هنوز مشتری ثبت نشده است.</td>
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
  name: 'Customers',
  data() {
    return {
      customers: [],
      total: 0,
      page: 1,
      totalPages: 1,
      sort: 'default',
      loading: true,
      sortOptions: [
        { key: 'default', label: 'پیش‌فرض' },
        { key: 'name', label: 'نام' },
        { key: 'phone', label: 'شماره تلفن' },
        { key: 'register_date', label: 'تاریخ ثبت' }
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
        const res = await api.customers({
          sort: this.sort,
          page: this.page
          // per_page اگر خواستی بعداً اضافه کن
        })
        
        this.customers = res.customers || []
        this.total = res.total || 0
        this.totalPages = res.total_pages || 1
      } catch (e) {
        console.error(e)
        alert('خطا در بارگذاری مشتریان: ' + (e.message || 'لطفاً دوباره تلاش کنید'))
      } finally {
        this.loading = false
      }
    },

    goPage(n) {
      if (n < 1 || n > this.totalPages) return
      this.page = nthis.load()
    },

    async doDelete(customer) {
      if (!confirm(`آیا از حذف مشتری "${customer.name}" مطمئن هستید؟`)) return
      
      try {
        await api.deleteCustomer(customer.id)
        alert('مشتری با موفقیت حذف شد')
        this.load() // بروزرسانی لیست
      } catch (e) {
        alert('خطا در حذف مشتری: ' + (e.message || ''))
      }
    }
  }
}
</script>