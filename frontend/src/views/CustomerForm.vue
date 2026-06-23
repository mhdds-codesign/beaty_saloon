<template>
  <div class="card" style="max-width: 520px; margin: 2rem auto;">
    <div class="card-header">
      <i :class="'fas ' + (isEdit ? 'fa-pen' : 'fa-plus')"></i>
      {{ isEdit ? 'ویرایش مشتری' : 'مشتری جدید' }}
    </div>
    <div class="card-body">
      <div v-if="error" class="error-msg">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>

      <form @submit.prevent="doSave">
        <div class="form-group">
          <label>نام و نام خانوادگی <span class="text-danger">*</span></label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="form-group">
          <label>شماره تلفن <span class="text-danger">*</span></label>
          <input v-model="form.phone_number" type="tel" required />
        </div>

        <div class="form-group">
          <label>آدرس</label>
          <textarea v-model="form.address" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label>یادداشت‌ها</label>
          <textarea v-model="form.notes" rows="3" placeholder="توضیحات اضافی..."></textarea>
        </div>

        <div class="d-flex gap-2 mt-4">
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="saving"
            style="flex: 1;"
          >
            <i class="fas fa-save"></i>
            {{ saving ? 'در حال ذخیره...' : (isEdit ? 'به‌روزرسانی' : 'ثبت مشتری') }}
          </button>
          <router-link to="/customers" class="btn btn-secondary" style="flex: 1;">
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
  name: 'CustomerForm',
  data() {
    return {
      isEdit: false,
      saving: false,
      error: null,
      form: {
        name: '',
        phone_number: '',
        address: '',
        notes: ''
      }
    }
  },
  async created() {
    const id = this.$route.params.id
    this.isEdit = !!id

    if (id) {
      try {
        const customer = await api.customer(id)
        this.form = {
          name: customer.name || '',
          phone_number: customer.phone_number || '',
          address: customer.address || '',
          notes: customer.notes || ''
        }
      } catch (e) {
        this.error = 'خطا در دریافت اطلاعات مشتری'
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
          await api.updateCustomer(this.$route.params.id, this.form)
        } else {
          await api.createCustomer(this.form)
        }

        this.$router.push('/customers')
      } catch (e) {
        this.error = e.message || 'خطا در ذخیره اطلاعات'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>