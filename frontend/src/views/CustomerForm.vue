<template>
  <div class="card form-card">
    <div class="card-header">
      {{ isRegister ? 'ثبت‌نام مشتری' : (isEdit ? 'ویرایش مشتری' : 'مشتری جدید') }}
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
          <label>شماره تلفن<span class="text-danger">*</span></label>
          <input v-model="form.phone_number" type="tel" pattern="09[0-9]{9}" placeholder="شماره تلفن باید با 09 شروع و 11 رقم باشد" />
        </div>

        <div class="form-group">
          <label>آدرس</label>
          <textarea v-model="form.address" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label>یادداشت‌ها</label>
          <textarea v-model="form.notes" rows="3" placeholder="توضیحات اضافی..."></textarea>
        </div>

        <hr style="margin: 1.5rem 0; border: none; border-top: 1px solid #e5e7eb;" />
        <p style="color:#6b7280; font-size:0.9rem; margin-bottom:0.75rem;">
          <i class="fas fa-user-lock"></i> اطلاعات حساب کاربری {{ isRegister ? '' : '(اختیاری)' }}
          <span v-if="hasAccount" style="color:#059669;"> — این مشتری حساب کاربری دارد</span>
        </p>

        <div class="form-group">
          <label>نام کاربری <span v-if="isRegister" class="text-danger">*</span></label>
          <input v-model="form.username" type="text" autocomplete="off" :required="isRegister" placeholder="برای ورود کاربر" />
        </div>

        <div class="form-group">
          <label>رمز عبور <span v-if="isRegister" class="text-danger">*</span></label>
          <input
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            :required="isRegister"
            :placeholder="hasAccount ? 'برای حفظ رمز فعلی خالی بگذارید' : 'رمز عبور کاربر'"
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
            {{ saving ? 'در حال ذخیره...' : (isRegister ? 'ثبت‌نام' : (isEdit ? 'به‌روزرسانی' : 'ثبت مشتری')) }}
          </button>
          <router-link :to="isRegister ? '/login' : '/customers'" class="btn btn-secondary"  style="flex: 1;">
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
      isRegister: false,
      saving: false,
      error: null,
      hasAccount: false,
      form: {
        name: '',
        phone_number: '',
        address: '',
        notes: '',
        username: '',
        password: ''
      }
    }
  },
  async created() {
    // حالت ثبت‌نام عمومی مشتری (مسیر /register بدون نیاز به لاگین)
    this.isRegister = this.$route.path === '/register'

    const id = this.$route.params.id
    this.isEdit = !!id

    if (id) {
      try {
        const customer = await api.customer(id)
        this.hasAccount = !!customer.has_account
        this.form = {
          name: customer.name || '',
          phone_number: customer.phone_number || '',
          address: customer.address || '',
          notes: customer.notes || '',
          username: customer.username || '',
          password: ''
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
        if (this.isRegister) {
          await api.register(this.form)
          alert('ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.')
          this.$router.push('/login')
          return
        }

        if (this.isEdit) {
          await api.updateCustomer(this.$route.params.id, this.form)
          alert('اطلاعات مشتری با موفقیت بروزرسانی شد')
        } else {
          await api.createCustomer(this.form)
          alert('اطلاعات مشتری با موفقیت ثبت شد')
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