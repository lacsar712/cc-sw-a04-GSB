<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'

const router = useRouter()
const rush = ref([])
const normal = ref([])
const next = ref(null)
const err = ref('')
let timer

async function refresh() {
  if (!localStorage.getItem('tok')) return
  try {
    const data = await api('/api/lanes')
    rush.value = data.rush
    normal.value = data.normal
    next.value = data.next
    err.value = ''
  } catch (e) {
    err.value = String(e.message || e)
  }
}

function goDetail(id) {
  router.push(`/jobs/${id}`)
}

onMounted(() => {
  refresh()
  timer = setInterval(refresh, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div>
    <p v-if="err" style="color:#b00020">{{ err }}</p>
    <div class="lanes">
      <section class="lane lane-rush">
        <h3>急测待处理（{{ rush.length }}）</h3>
        <p v-if="!rush.length" class="empty">空</p>
        <ul v-else>
          <li v-for="j in rush" :key="j.id" @click="goDetail(j.id)">
            <span class="badge">急测</span>
            #{{ j.id }} {{ j.lamp }}（{{ j.nominal_nm }} / {{ j.measured_nm }}）
          </li>
        </ul>
      </section>
      <section class="lane lane-normal">
        <h3>普通待处理（{{ normal.length }}）</h3>
        <p v-if="!normal.length" class="empty">空</p>
        <ul v-else>
          <li v-for="j in normal" :key="j.id" @click="goDetail(j.id)">
            #{{ j.id }} {{ j.lamp }}（{{ j.nominal_nm }} / {{ j.measured_nm }}）
          </li>
        </ul>
      </section>
      <section class="lane lane-next">
        <h3>下一笔将领</h3>
        <p v-if="!next" class="empty">无待处理</p>
        <div v-else class="next-card" @click="goDetail(next.id)">
          <p>
            <span v-if="next.urgent" class="badge">急测</span>
            <span v-else class="badge badge-normal">普通</span>
            #{{ next.id }} {{ next.lamp }}
          </p>
          <p>标称 {{ next.nominal_nm }} nm / 实测 {{ next.measured_nm }} nm</p>
          <p class="hint">领取侧先清空急测，再按编号升序领普通</p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.lanes {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin: 16px 0;
}
.lane {
  flex: 1;
  min-width: 0;
  padding: 12px;
  border: 1px solid #ccc;
}
.lane-rush {
  border-color: #c0392b;
}
.lane-next {
  border-color: #1a6fc0;
}
.lane h3 {
  margin-top: 0;
}
.lane ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.lane li {
  padding: 6px 4px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}
.lane li:hover {
  background: #f4f7fa;
}
.badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  background: #c0392b;
  color: #fff;
  font-size: 12px;
}
.badge-normal {
  background: #8a97a5;
}
.next-card {
  padding: 8px;
  border: 1px dashed #1a6fc0;
  cursor: pointer;
}
.next-card:hover {
  background: #f4f7fa;
}
.empty {
  color: #888;
}
.hint {
  color: #666;
  font-size: 13px;
}
</style>
