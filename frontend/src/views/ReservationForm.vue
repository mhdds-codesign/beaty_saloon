<template>
  <div class="card" style="max-width: 620px; margin: 2rem auto;">
    <div class="card-header">
      <i :class="'fas ' + (isEdit ? 'fa-pen' : 'fa-plus')"></i>
      {{ isEdit ? 'ویرایش نوبت' : 'نوبت جدید' }}
    </div>
    <div class="card-body">
      <div v-if="error" class="error-msg">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>

      <form @submit.prevent="doSave">
        <!-- انتخاب مشتری -->
        <div class="form-group">
          <label>مشتری <span class="text-danger">*</span></label>
          <select v-model.number="form.customer_id" required>
            <option value="">انتخاب مشتری</option>
            <option v-for="c in customers" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>

        <!-- انتخاب لاین -->
        <div class="form-group">
          <label>خدمت / لاین <span class="text-danger">*</span></label>
          <select v-model.number="form.line_id" required @change="onLineChange">
            <option value="">انتخاب خدمت</option>
            <option v-for="line in lines" :key="line.id" :value="line.id">
              {{ line.name_line }} — {{ line.name_service }} — {{ line.price }}
            </option>
          </select>
        </div>

        <!-- انتخاب اسلات زمانی آزاد -->
        <div class="form-group">
          <label>زمان نوبت <span class="text-danger">*</span></label>
          <select v-model.number="form.schedule_id" required>
            <option value="">انتخاب زمان</option>
            <option 
              v-for="slot in availableSlots" 
              :key="slot.id" 
              :value="slot.id"
            >
              {{ slot.weekday }} — {{ slot.start_time }} تا {{ slot.end_time }}
            </option>
          </select>
        </div>

        <!-- قیمت نهایی (غیرقابل ویرایش) -->
        <div class="form-group">
          <label>قیمت نهایی (تومان)</label>
          <input 
            :value="finalPrice.toLocaleString()" 
            type="text" 
            class="disabled-input" 
            disabled 
          />
        </div>

        <div class="d-flex gap-2 mt-4">
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="saving"
            style="flex: 1;"
          >
            <i class="fas fa-save"></i>
            {{ saving ? 'در حال ذخیره...' : (isEdit ? 'به‌روزرسانی نوبت' : 'ثبت نوبت') }}
          </button>
          <router-link to="/reservations" class="btn btn-secondary" style="flex: 1;">
            انصراف
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'ReservationForm',
  data() {
    return {
      isEdit: false,
      saving: false,
      error: null,
      customers: [],
      lines: [],
      availableSlots: [],
      finalPrice: 0,
      form: {
        customer_id: null,
        line_id: null,
        schedule_id: null,
        status: 'confirmed'
      }
    }
  },
  async created() {
    await Promise.all([this.loadCustomers(), this.loadLines()])
    
    const id = this.$route.params.id
    this.isEdit = !!id

    if (id) {
      try {
        const res = await api.reservation(id)

        this.form = {
          customer_id: res.customer_id,
          line_id: res.line_id,
          schedule_id: res.schedule_id,
          status: res.status || 'confirmed'
        }
        this.finalPrice = res.price || 0
        if (res.line_id) await this.loadAvailableSlots(res.line_id, res)
      } catch (e) {
        this.error = 'خطا در دریافت اطلاعات نوبت'
      }
    }
  },
  methods: {
    async loadCustomers() {
      try {
        const res = await api.customers({ per_page: 100 })
        this.customers = res.customers || []
      } catch (e) {
        console.error(e)
      }
    },

    async loadLines() {
      try {
        const res = await api.lines({ per_page: 100 })
        this.lines = res.lines || []
      } catch (e) {
        console.error(e)
      }
    },

    async loadAvailableSlots(line_id, reservation = null) {
      try {
        const res = await api.availableSlots(line_id)
        let slots = res.slots || res || []
        
        this.availableSlots = slots
      
      } catch (e) {
        console.error(e)
        this.availableSlots = []
      }
    },

    async onLineChange() {
      this.form.schedule_id = null
      if (this.form.line_id) {
        await this.loadAvailableSlots(this.form.line_id)
        // پیدا کردن قیمت لاین
        const selectedLine = this.lines.find(l => l.id === this.form.line_id)
        this.finalPrice = selectedLine ? selectedLine.price || 0 : 0
      } else {
        this.finalPrice = 0
      }
    },

    async doSave() {
      this.saving = true
      this.error = null

      try {
        if (this.isEdit) {
          await api.updateReservation(this.$route.params.id, this.form)
        } else {
          await api.createReservation(this.form)
        }
        this.$router.push('/reservations')
      } catch (e) {
        this.error = e.message || 'خطا در ثبت نوبت'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>