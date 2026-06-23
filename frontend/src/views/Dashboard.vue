<template>
  <div>
    <h2><i class="fas fa-chart-pie"></i> داشبورد سالن زیبایی</h2>

    <div v-if="loading" class="loading">در حال بارگذاری...</div>

    <template v-else-if="data">
      <!-- آمار کلی -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin:1.5rem 0;">
        <div class="card text-center">
          <div class="card-header">خدمات</div>
          <div class="card-body">
            <span style="font-size:2.5rem;font-weight:700;color:#2b9348;">{{ data.total_services }}</span>
          </div>
        </div>

        <div class="card text-center">
          <div class="card-header">انواع خدمات</div>
          <div class="card-body">
            <span style="font-size:2.5rem;font-weight:700;color:#2b9348;">{{ data.total_line_types }}</span>
          </div>
        </div>

        <div class="card text-center">
          <div class="card-header">مشتریان</div>
          <div class="card-body">
            <span style="font-size:2.5rem;font-weight:700;color:#2b9348;">{{ data.total_customers }}</span>
          </div>
        </div>

        <div class="card text-center">
          <div class="card-header">نوبت‌ها</div>
          <div class="card-body">
            <span style="font-size:2.5rem;font-weight:700;color:#2b9348;">{{ data.total_reservations }}</span>
          </div>
        </div>

        <div class="card text-center">
          <div class="card-header">درآمد کل</div>
          <div class="card-body">
            <span style="font-size:2.5rem;font-weight:700;color:#2b9348;">{{ data.total_revenue.toLocaleString() }} تومان</span>
          </div>
        </div>

        <div class="card text-center" v-if="data.most_popular_service">
          <div class="card-header">محبوب‌ترین خدمت</div>
          <div class="card-body">
            <strong>{{ data.most_popular_service.name_service }}</strong><br>
            <small>{{ data.most_popular_service.name_line }}</small>
            <div class="mt-2">
              <span class="badge bg-warning" style="font-size:2.5rem;font-weight:700;color:#2b9348;">{{ data.most_popular_service.busy_slots }} نوبت مشغول</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- آخرین نوبت‌ها -->
      <div class="card mt-4">
        <div class="card-header">
          <i class="fas fa-clock"></i> آخرین نوبت‌ها
        </div>
        <div class="card-body p-0">
          <table class="table">
            <thead>
              <tr>
                <th>#</th>
                <th>مشتری</th>
                <th>خدمت</th>
                <th>قیمت</th>
                <th>وضعیت</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="res in data.recent_reservations" :key="res.id">
                <td>#{{ res.id }}</td>
                <td>{{ res.customer_name }}</td>
                <td>
                  {{ res.line_name }}<br>
                  <small>{{ res.service_name }}</small>
                </td>
                <td>{{ res.total_price.toLocaleString() }} تومان</td>
                <td>
                  <span class="badge" :class="getStatusClass(res.status)">
                    {{ getStatusText(res.status) }}
                  </span>
                </td>
                <td>
                  <router-link :to="`/reservations/${res.id}`" class="btn btn-sm btn-primary">
                    مشاهده
                  </router-link>
                </td>
              </tr>
              <tr v-if="!data.recent_reservations || data.recent_reservations.length === 0">
                <td colspan="6" class="text-center py-4">هنوز نوبت ثبت نشده است.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- دکمه‌های سریع -->
      <div class="actions mt-4">
        <router-link to="/customers/new" class="btn btn-primary">
          <i class="fas fa-plus"></i> مشتری جدید
        </router-link>
        <router-link to="/lines/new" class="btn btn-primary">
          <i class="fas fa-plus"></i> خدمت جدید
        </router-link>
        <router-link to="/reservations/new" class="btn btn-primary">
          <i class="fas fa-plus"></i> نوبت جدید
        </router-link>
        <router-link to="/schedules/new" class="btn btn-primary">
          <i class="fas fa-plus"></i> برنامه کاری
        </router-link>
      </div>
    </template>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Dashboard',
  data() {
    return {
      data: null,
      loading: true
    }
  },
  async created() {
    try {
      this.data = await api.dashboard()
    } catch (e) {
      console.error(e)
      alert('خطا در بارگذاری داشبورد: ' + (e.message || 'لطفاً دوباره تلاش کنید'))
    } finally {
      this.loading = false
    }
  },
  methods: {
    getStatusText(status) {
      const texts = {
        pending: 'در انتظار',
        confirmed: 'تایید شده',
        completed: 'انجام شده',
        cancelled: 'لغو شده'
      }
      return texts[status] || status
    },
    getStatusClass(status) {
      const classes = {
        pending: 'bg-warning',
        confirmed: 'bg-success',
        completed: 'bg-info',
        cancelled: 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    }
  }
}
</script>