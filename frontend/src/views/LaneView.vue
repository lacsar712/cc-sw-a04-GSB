<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'

// 急测插队车道专页：急测队 / 普通队 / 下一笔将领 三栏并排总览
const router = useRouter()
const role = ref(localStorage.getItem('role') || '')
const lane = ref({ urgent_queue: [], normal_queue: [], next_job: null })
const err = ref('')
// 急测勾选只存在于提交表单：校准员提交时随单冻结，此后不可改
const form = ref({ lamp: '', nominal_nm: 0.15, measured_nm: 0.15, urgent: false })
let timer

async function refresh() {
  if (!localStorage.getItem('tok')) return
  try {
    lane.value = await api('/api/lane')
    err.value = ''
  } catch (e) {
    err.value = String(e.message || e)
  }
}

async function submit() {
  err.value = ''
  try {
    await api('/api/jobs', { method: 'POST', body: JSON.stringify(form.value) })
    form.value = { ...form.value, lamp: '', urgent: false }
    await refresh()
  } catch (e) {
    err.value = String(e.message || e)
  }
}

function goDetail(id) {
  router.push(`/jobs/${id}`)
}

onMounted(() => {
  role.value = localStorage.getItem('role') || ''
  refresh()
  timer = setInterval(refresh, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div>
    <p v-if="err" style="color:#b00020">{{ err }}</p>

    <section v-if="role === 'writer'" style="margin:16px 0; padding:12px; border:1px solid #ccc;">
      <h3>提交校准（校准员）</h3>
      <label>灯种 <input v-model="form.lamp" /></label>
      <label>标称 nm <input type="number" step="0.01" v-model.number="form.nominal_nm" /></label>
      <label>实测 nm <input type="number" step="0.01" v-model.number="form.measured_nm" /></label>
      <label class="urgent-check">
        <input type="checkbox" v-model="form.urgent" />
        急测（提交后随单冻结，不可再改）
      </label>
      <button @click="submit">入队</button>
    </section>
    <p v-else class="hint">巡检员视角：急测记号可见，但不可勾选、不可提交。</p>

    <div class="lane-grid">
      <section class="lane-col lane-urgent">
        <h3>急测队（待处理 {{ lane.urgent_queue.length }}）</h3>
        <table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
          <thead>
            <tr><th>编号</th><th>灯种</th><th>急测</th></tr>
          </thead>
          <tbody>
            <tr
              v-for="j in lane.urgent_queue"
              :key="j.id"
              style="cursor:pointer"
              @click="goDetail(j.id)"
            >
              <td>{{ j.id }}</td>
              <td>{{ j.lamp }}</td>
              <td>{{ j.urgent ? '急测' : '—' }}</td>
            </tr>
            <tr v-if="!lane.urgent_queue.length"><td colspan="3" class="empty">无</td></tr>
          </tbody>
        </table>
      </section>

      <section class="lane-col lane-normal">
        <h3>普通队（待处理 {{ lane.normal_queue.length }}）</h3>
        <table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
          <thead>
            <tr><th>编号</th><th>灯种</th><th>急测</th></tr>
          </thead>
          <tbody>
            <tr
              v-for="j in lane.normal_queue"
              :key="j.id"
              style="cursor:pointer"
              @click="goDetail(j.id)"
            >
              <td>{{ j.id }}</td>
              <td>{{ j.lamp }}</td>
              <td>{{ j.urgent ? '急测' : '—' }}</td>
            </tr>
            <tr v-if="!lane.normal_queue.length"><td colspan="3" class="empty">无</td></tr>
          </tbody>
        </table>
      </section>

      <section class="lane-col lane-next">
        <h3>下一笔将领</h3>
        <div v-if="lane.next_job" class="next-card" style="cursor:pointer" @click="goDetail(lane.next_job.id)">
          <p><strong>#{{ lane.next_job.id }}</strong> {{ lane.next_job.lamp }}</p>
          <p>车道：<span :class="lane.next_job.urgent ? 'tag-urgent' : 'tag-normal'">{{ lane.next_job.urgent ? '急测' : '普通' }}</span></p>
          <p class="hint">领取规则：急测清空后再碰普通，同档按编号升序</p>
        </div>
        <p v-else class="empty">待处理队列为空</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.lane-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  align-items: start;
}
.lane-col {
  border: 1px solid #ccc;
  padding: 10px;
  background: #fff;
}
.lane-urgent {
  border-color: #c0392b;
  background: #fdf3f2;
}
.lane-col h3 {
  margin: 0 0 8px;
  font-size: 15px;
}
.urgent-check {
  margin: 0 12px;
  font-weight: 600;
  color: #c0392b;
}
.tag-urgent {
  color: #fff;
  background: #c0392b;
  padding: 1px 8px;
  border-radius: 3px;
  font-weight: 700;
}
.tag-normal {
  color: #333;
  background: #e6e6e6;
  padding: 1px 8px;
  border-radius: 3px;
}
.next-card {
  border: 1px dashed #888;
  padding: 8px;
}
.next-card p {
  margin: 4px 0;
}
.empty {
  color: #888;
  text-align: center;
}
.hint {
  color: #666;
  font-size: 12px;
}
</style>
