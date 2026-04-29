import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import HomeView from '../HomeView.vue'

vi.mock('@/api/health', () => ({
  fetchHealth: vi.fn().mockResolvedValue({ status: 'ok', version: '0.1.0' }),
}))

vi.mock('@/api/auth', () => ({
  me: vi.fn().mockResolvedValue({
    id: '1',
    email: 'admin@test.com',
    role: 'admin',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
  }),
  login: vi.fn(),
}))

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: HomeView },
      { path: '/login', component: { template: '<div />' } },
    ],
  })
}

describe('HomeView', () => {
  it('renders the dashboard content', async () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [createPinia(), makeRouter()] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Estado del backend')
  })

  it('shows backend status after mount', async () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [createPinia(), makeRouter()] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('ok')
  })
})
