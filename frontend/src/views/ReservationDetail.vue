<template>
  <div>
    <div v-if="loading" class="loading">در حال بارگذاری...</div>
    
    <div v-else-if="reservation">
      <h2>
        <i class="fas fa-file-invoice"></i> 
        نوبت #{{ reservation.id }}
      </h2>

      <div class="card">
        <div class="card-header">
          <i class="fas fa-info-circle"></i> اطلاعات نوبت
        </div>
        <div class="card-body">
          <table class="table">
            <tbody>
              <tr>
                <td><strong>مشتری</strong></td>
                <td>{{ reservation.customer_name || '—' }}</td>
              </tr>
              <tr>
                <td><strong>خدمت</strong></td>
                <td>
                  <strong>{{ reservation.name_line }}</strong> — 
                  {{ reservation.name_service }}
                </td>
              </tr>
              <tr>
                <td><strong>روز و ساعت</strong></td>
                <td>
                  {{ reservation.weekday}}<br>
                  <strong>{{ reservation.start_time }} - {{ reservation.end_time }}</strong>
                </td>
              </tr>
              <tr>
                <td><strong>قیمت نهایی</strong></td>
                <td>
                  <strong>{{ reservation.price ? reservation.price.toLocaleString() + ' تومان' : '—' }}</strong>
                </td>
              </tr>
              <tr>
                <td><strong>وضعیت</strong></td>
                <td>
                  <span class="badge" :class="getStatusClass(reservation.status)">
                    {{ getStatusText(reservation.status) }}
                  </span>
                  
                  <select v-model="newStatus" class="btn-sm" style="width:auto; margin-left:12px;">
                    <option value="confirmed">تایید شده</option>
                    <option value="completed">انجام شده</option>
                    <option value="cancelled">لغو شده</option>
                  </select>
                  
                  <button 
                    class="btn btn-sm btn-primary" 
                    @click="updateStatus"
                    style="margin-left:8px;"
                  >
                    بروزرسانی وضعیت
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style="margin-top: 1.5rem;">
        <router-link to="/reservations" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i> بازگشت به لیست نوبت‌ها
        </router-link>
      </div>
    </div>

    <div v-else class="text-center">
      <p>نوبت مورد نظر یافت نشد.</p>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'ReservationDetail',
  data() {
    return {
      reservation: null,
      loading: true,
      newStatus: 'confirmed'
    }
  },
  async created() {
    await this.loadReservation()
  },
  methods: {
    async loadReservation() {
      try {
        this.reservation = await api.reservation(this.$route.params.id)
        this.newStatus = this.reservation.status || 'confirmed'
      } catch (e) {
        console.error(e)
        alert('خطا در بارگذاری اطلاعات نوبت')
      } finally {
        this.loading = false
      }
    },

    async updateStatus() {
      if (!this.newStatus) return
      
      try {
        const updated = await api.updateReservationStatus(this.$route.params.id, this.newStatus)
        alert('وضعیت نوبت با موفقیت بروزرسانی شد')

      } catch (e) {
        alert('خطا در بروزرسانی وضعیت: ' + (e.message || ''))
      }
    },

    getStatusText(status) {
      const map = {
        confirmed: 'تایید شده',
        completed: 'انجام شده',
        cancelled: 'لغو شده'
      }
      return map[status] || status
    },

    getStatusClass(status) {
      const map = {
        confirmed: 'bg-info',
        completed: 'bg-success',
        cancelled: 'bg-danger'
      }
      return map[status] || 'bg-secondary'
    }
  }
}
</script>