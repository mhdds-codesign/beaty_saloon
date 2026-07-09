<template>
  <div class="card" style="max-width: 560px; margin: 2rem auto;">
    <div class="card-header">
      {{ isEdit ? 'ویرایش سرویس / لاین' : 'سرویس / لاین جدید' }}
    </div>
    <div class="card-body">
      <div v-if="error" class="error-msg">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>

      <form @submit.prevent="doSave">
        <div class="form-group">
          <label>نام لاین <span class="text-danger">*</span></label>
          <input v-model="form.name_line" type="text" required placeholder="مثال: مو ، میکاپ، ..." />
        </div>

        <div class="form-group">
          <label>نام سرویس <span class="text-danger">*</span></label>
          <input v-model="form.name_service" type="text" required placeholder="مثال: رنگساژ لایت، کوتاهی مردانه" />
        </div>

        <div class="row">
          <div class="form-group col-6">
            <label>قیمت (تومان) <span class="text-danger">*</span></label>
            <input v-model.number="form.price" type="number" min="0" required />
          </div>
          <div class="form-group col-6">
            <label>مدت زمان (دقیقه) <span class="text-danger">*</span></label>
            <input v-model.number="form.duration_minutes" type="number" min="0" required />
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
            {{ saving ? 'در حال ذخیره...' : (isEdit ? 'به‌روزرسانی' : 'ثبت سرویس') }}
          </button>
          <router-link to="/lines" class="btn btn-secondary" style="flex: 1;">
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
  name: 'LineForm',
  data() {
    return {
      isEdit: false,
      saving: false,
      error: null,
      form: {
        name_line: '',
        name_service: '',
        price: 0,
        duration_minutes: 0,
      }
    }
  },
  async created() {
    const id = this.$route.params.id
    this.isEdit = !!id

    if (id) {
      try {
        const line = await api.line(id)
        this.form = {
          name_line: line.name_line || '',
          name_service: line.name_service || '',
          price: line.price || 0,
          duration_minutes: line.duration_minutes || 0,
        }
      } catch (e) {
        this.error = 'خطا در دریافت اطلاعات سرویس'
        console.error(e)
      }
    }
  },
  methods: {
    async doSave() {
      this.saving = true
      this.error = null

      try {
        if (this.isEdit) {
          await api.updateLine(this.$route.params.id, this.form)
          alert('اطلاعات لاین / سرویس با موفقیت بروزرسانی شد')
        } else {
          await api.createLine(this.form)
          alert('اطلاعات لاین / سرویس با موفقیت ثبت شد')
        }

        this.$router.push('/lines')
      } catch (e) {
        this.error = e.message || 'خطا در ذخیره اطلاعات'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
