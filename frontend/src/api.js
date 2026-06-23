const BASE = ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || err.message || `HTTP ${res.status}`)
  }
  return res.json()
}

export default {
  // ==================== Auth ====================
  login(username, password) {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },

  logout() {
    return request('/api/auth/logout', { method: 'POST' })
  },

  me() {
    return request('/api/auth/me')
  },

  // ==================== Dashboard ====================
  dashboard() {
    return request('/api/dashboard')
  },

  // ==================== Customers ====================
  customers(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/api/customers?${q}`)
  },

  customer(id) {
    return request(`/api/customers/${id}`)
  },

  createCustomer(data) {
    return request('/api/customers', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateCustomer(id, data) {
    return request(`/api/customers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  patchCustomer(id, data) {
    return request(`/api/customers/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  deleteCustomer(id) {
    return request(`/api/customers/${id}`, { method: 'DELETE' })
  },

  // ==================== Lines (Services) ====================
  lines(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/api/lines?${q}`)
  },

  line(id) {
    return request(`/api/lines/${id}`)
  },

  createLine(data) {
    return request('/api/lines', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateLine(id, data) {
    return request(`/api/lines/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  patchLine(id, data) {
    return request(`/api/lines/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  deleteLine(id) {
    return request(`/api/lines/${id}`, { method: 'DELETE' })
  },

  // ==================== Reservations ====================
  reservations(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/api/reservations?${q}`)
  },

  reservation(id) {
    return request(`/api/reservations/${id}`)
  },

  createReservation(data) {
    return request('/api/reservations', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateReservation(id, data) {
    return request(`/api/reservations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  updateReservationStatus(id, status) {
    return request(`/api/reservations/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    })
  },

  // Available Slots (برای فرم رزرو)
  availableSlots(line_id = null) {
    const params = line_id ? `?line_id=${line_id}` : ''
    return request(`/api/reservations/available-slots${params}`)
  },

  // ==================== Schedules (Work Schedules) ====================
  schedules(params = {}) {
    const q = new URLSearchParams(params).toString()
    return request(`/api/schedules?${q}`)
  },

  schedule(id) {
    return request(`/api/schedules/${id}`)
  },

  createSchedule(data) {
    return request('/api/schedules', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  updateSchedule(id, data) {
    return request(`/api/schedules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  patchSchedule(id, data) {
    return request(`/api/schedules/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  deleteSchedule(id) {
    return request(`/api/schedules/${id}`, { method: 'DELETE' })
  },
}