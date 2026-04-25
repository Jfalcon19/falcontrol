import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HomeView from '../HomeView.vue'

vi.mock('@/api/health', () => ({
  fetchHealth: vi.fn().mockResolvedValue({ status: 'ok', version: '0.1.0' }),
}))

describe('HomeView', () => {
  it('renders the app title', async () => {
    const wrapper = mount(HomeView)
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Falcontrol')
  })

  it('shows backend status after mount', async () => {
    const wrapper = mount(HomeView)
    await flushPromises()
    expect(wrapper.text()).toContain('ok')
  })
})
