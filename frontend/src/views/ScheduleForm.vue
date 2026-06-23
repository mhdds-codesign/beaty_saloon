<template>
  <div class="card" style="max-width: 560px; margin: 2rem auto;">
    <div class="card-header">
      <i :class="'fas ' + (isEdit ? 'fa-pen' : 'fa-plus')"></i>
      {{ isEdit ? 'ویرایش برنامه کاری' : 'برنامه کاری جدید' }}
    </div>
    <div class="card-body">
      <div v-if="error" class="error-msg">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>

      <form @submit.prevent="doSave">
        <div class="form-group">
          <label>لاین / خدمت <span class="text-danger">*</span></label>
          <select v-model.number="form.line_id" required>
            <option value="">انتخاب لاین</option>
            <option 
              v-for="line in lines" 
              :key="line.id" 
              :value="line.id"
            >
              {{ line.name_line }} — {{ line.name_service }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>روز هفته <span class="text-danger">*</span></label>
          <select v-model.number="form.weekday" required>
            <option :value="0">یکشنبه</option>
            <option :value="1">دوشنبه</option>
            <option :value="2">سه‌شنبه</option>
            <option :value="3">چهارشنبه</option>
            <option :value="4">پنجشنبه</option>
            <option :value="5">جمعه</option>
            <option :value="6">شنبه</option>
          </select>
        </div>

        <div class="row">
          <div class="form-group col-6">
            <label>ساعت شروع <span class="text-danger">*</span></label>
            <select v-model="form.start_time" required @change="updateEndTime">
              <option value="">انتخاب کنید</option>
              <option v-for="slot in timeSlots" :key="slot.start" :value="slot.start">
                {{ slot.start }}
              </option>
            </select>
          </div>
          <div class="form-group col-6">
            <label>ساعت پایان</label>
            <input v-model="form.end_time" type="time" disabled class="disabled-input" style:"background-color: #6c757d; cursor: not-allowed;" />
          </div>
        </div>

        <div class="d-flex gap-2 mt-4">
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="saving"
            style="flex: 1;"
          >
            <i class="fas fa-save"></i>
            {{ saving ? 'در حال ذخیره...' : (isEdit ? 'به‌روزرسانی' : 'ثبت برنامه') }}
          </button>
          <router-link to="/schedules" class="btn btn-secondary" style="flex: 1;">
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
  name: 'ScheduleForm',
  data() {
    return {
      isEdit: false,
      saving: false,
      error: null,
      lines: [],
      timeSlots: [
        { start: "09:00", end: "11:00" },
        { start: "11:00", end: "13:00" },
        { start: "13:00", end: "15:00" },
        { start: "15:00", end: "17:00" },
        { start: "17:00", end: "19:00" }
      ],
      form: {
        line_id: null,
        weekday: 0,
        start_time: '',
        end_time: '',
        status: 'free'
      }
    }
  },
  async created() {
    await this.loadLines()
    
    const id = this.$route.params.id
    this.isEdit = !!id

    if (id) {
      try {
        const schedule = await api.schedule(id)
        this.form = {
          line_id: schedule.line_id,
          weekday: schedule.weekday,
          start_time: schedule.start_time,
          end_time: schedule.end_time,
          status: 'free'
        }
      } catch (e) {
        this.error = 'خطا در دریافت اطلاعات برنامه کاری'
        console.error(e)
      }
    }
  },
  methods: {
    async loadLines() {
      try {
        const res = await api.lines({ per_page: 100 })
        this.lines = res.lines || []
      } catch (e) {
        console.error('خطا در لود لاین‌ها', e)
        this.error = 'خطا در دریافت لیست خدمات'
      }
    },

    updateEndTime() {
      const slot = this.timeSlots.find(s => s.start === this.form.start_time)
      if (slot) {
        this.form.end_time = slot.end
      }
    },

    async doSave() {
      this.saving = true
      this.error = null

      try {
        if (this.isEdit) {
          await api.updateSchedule(this.$route.params.id, this.form)
        } else {
          await api.createSchedule(this.form)
        }
        this.$router.push('/schedules')
      } catch (e) {
        this.error = e.message || 'خطا در ذخیره اطلاعات'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>