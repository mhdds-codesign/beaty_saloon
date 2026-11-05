import { reactive } from 'vue'
import api from './api.js'

// وضعیت احراز هویت مشترک بین همه کامپوننت‌ها
export const auth = reactive({
  loaded: false,
  id: null,
  username: null,
  role: null,          // "admin" | "user"
  customer_id: null,
})

export function isAdmin() {
  return auth.role === 'admin'
}

// اطلاعات حساب لاگین‌شده را از سرور می‌گیرد و در store می‌ریزد
export async function loadAuth() {
  try {
    const me = await api.me()
    auth.id = me.id
    auth.username = me.username
    auth.role = me.role
    auth.customer_id = me.customer_id
    auth.loaded = true
    return me
  } catch (e) {
    clearAuth()
    throw e
  }
}

export function clearAuth() {
  auth.loaded = false
  auth.id = null
  auth.username = null
  auth.role = null
  auth.customer_id = null
}
