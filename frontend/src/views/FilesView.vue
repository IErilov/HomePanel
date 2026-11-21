<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Archive, ArrowDownToLine, ArrowUpDown, File, FileImage, FileText, FileVideo, FolderOpen, Globe2, HardDrive, LoaderCircle, MoreHorizontal, Pencil, RefreshCw, Search, Trash2, Upload, X } from 'lucide-vue-next'
import AppShell from '../components/AppShell.vue'
import { api, errorMessage } from '../api.ts'
import { useAuthStore } from '../stores/auth.ts'
import type { Bucket, BucketsResponse, BucketFilesResponse, StoredFile } from '../types.ts'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const buckets = ref<Bucket[]>([])
const activeBucketId = ref('')
const activeBucket = computed(() => buckets.value.find(bucket => bucket.id === activeBucketId.value) || null)
const isOpen = computed(() => activeBucket.value?.bucket_type === 'OPEN')
const data = ref<BucketFilesResponse | null>(null)
const files = computed(() => data.value?.files || [])
const search = ref('')
const sortNewest = ref(true)
const filteredFiles = computed(() => {
  const q = search.value.trim().toLowerCase()
  const result = files.value.filter(f => f.filename.toLowerCase().includes(q))
  return [...result].sort((a, b) => sortNewest.value
    ? (b.last_modified || '').localeCompare(a.last_modified || '')
    : a.filename.localeCompare(b.filename))
})
const loading = ref(false)
const bucketsLoading = ref(false)
const uploading = ref(false)
const error = ref('')
const notice = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const menuFor = ref<string | null>(null)
const renameTarget = ref<StoredFile | null>(null)
const newName = ref('')
const deleting = ref<string | null>(null)

const totalBytes = computed(() => files.value.reduce((sum, f) => sum + f.size, 0))
const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} Б`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} МБ`
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} ГБ`
}
const formatDate = (date: string | null) => date ? new Intl.DateTimeFormat('ru-RU', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(date)) : '—'
const iconFor = (name: string) => {
  const ext = name.split('.').pop()?.toLowerCase()
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext || '')) return FileImage
  if (['mp4', 'mov', 'mkv', 'webm'].includes(ext || '')) return FileVideo
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext || '')) return Archive
  if (['pdf', 'doc', 'docx', 'txt', 'rtf'].includes(ext || '')) return FileText
  return File
}
const isAdmin = computed(() => auth.user?.role === 'super_user')
const canManage = computed(() => !!activeBucket.value && (activeBucket.value.bucket_type === 'PERSONAL' || isAdmin.value))
const canUpload = computed(() => !!activeBucket.value && (isOpen.value || auth.isAuthenticated()))

async function loadBuckets() {
  bucketsLoading.value = true
  error.value = ''
  try {
    const { data: response } = await api.get<BucketsResponse>('/api/buckets/')
    buckets.value = response.buckets || []
    const requested = typeof route.query.bucket === 'string' ? route.query.bucket : ''
    const requestedBucket = buckets.value.find(bucket => bucket.id === requested || bucket.bucket_type.toLowerCase() === requested.toLowerCase())
    const preferred = requestedBucket || buckets.value.find(bucket => bucket.bucket_type === 'PERSONAL') || buckets.value.find(bucket => bucket.bucket_type === 'OPEN')
    activeBucketId.value = preferred?.id || ''
    if (activeBucketId.value) await loadFiles()
    else {
      data.value = null
      error.value = 'Для этого аккаунта пока нет доступных хранилищ.'
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    bucketsLoading.value = false
  }
}

async function loadFiles() {
  if (!activeBucketId.value) return
  error.value = ''
  notice.value = ''
  loading.value = true
  try {
    const response = await api.get<BucketFilesResponse>(`/api/buckets/${activeBucketId.value}/files`)
    data.value = response.data
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function chooseBucket(bucket: Bucket) {
  activeBucketId.value = bucket.id
  data.value = null
  router.replace({ path: '/app', query: { bucket: bucket.id } })
  await loadFiles()
}

async function uploadSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const selected = input.files
  if (!selected?.length || !activeBucketId.value) return
  uploading.value = true
  error.value = ''
  notice.value = ''
  try {
    for (const file of Array.from(selected)) {
      const form = new FormData()
      form.append('file', file)
      await api.post(`/api/buckets/${activeBucketId.value}/upload`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    notice.value = selected.length === 1 ? 'Файл загружен' : `Загружено файлов: ${selected.length}`
    await loadFiles()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function downloadFile(file: StoredFile) {
  if (!activeBucketId.value) return
  try {
    const path = encodeURIComponent(file.filename).replaceAll('%2F', '/')
    const response = await api.get(`/api/buckets/${activeBucketId.value}/download/${path}`, { responseType: 'blob' })
    const objectUrl = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = objectUrl
    a.download = file.filename.split('/').pop() || file.filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(objectUrl)
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function removeFile(file: StoredFile) {
  if (!activeBucketId.value || !confirm(`Удалить файл «${file.filename}»?`)) return
  deleting.value = file.filename
  error.value = ''
  try {
    const path = encodeURIComponent(file.filename).replaceAll('%2F', '/')
    await api.delete(`/api/buckets/${activeBucketId.value}/files/${path}`)
    notice.value = 'Файл удалён'
    menuFor.value = null
    await loadFiles()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    deleting.value = null
  }
}

function beginRename(file: StoredFile) {
  renameTarget.value = file
  newName.value = file.filename
  menuFor.value = null
}
async function saveRename() {
  if (!activeBucketId.value || !renameTarget.value || !newName.value.trim()) return
  try {
    const path = encodeURIComponent(renameTarget.value.filename).replaceAll('%2F', '/')
    await api.patch(`/api/buckets/${activeBucketId.value}/files/${path}`, { new_filename: newName.value.trim() })
    renameTarget.value = null
    notice.value = 'Файл переименован'
    await loadFiles()
  } catch (e) {
    error.value = errorMessage(e)
  }
}

onMounted(async () => {
  if (auth.isAuthenticated() && !auth.user) {
    try { await auth.fetchMe() } catch { auth.logout(); router.push('/login') ; return }
  }
  await loadBuckets()
})
watch(() => route.query.bucket, async (next) => {
  if (typeof next !== 'string' || !buckets.value.length) return
  const target = buckets.value.find(bucket => bucket.id === next || bucket.bucket_type.toLowerCase() === next.toLowerCase())
  if (target && target.id !== activeBucketId.value) {
    activeBucketId.value = target.id
    await loadFiles()
  }
})
</script>

<template>
  <AppShell>
    <div class="files-page">
      <div class="page-heading">
        <div><h1>Файловое хранилище</h1><p class="muted">Все ваши файлы и хранилища в одном месте.</p></div>
        <button class="secondary-button refresh-btn" @click="loadBuckets" :disabled="loading || bucketsLoading"><RefreshCw :size="16" :class="{ spinning: loading || bucketsLoading }" /> Обновить</button>
      </div>

      <div class="bucket-tabs" v-if="buckets.length">
        <button v-for="bucket in buckets" :key="bucket.id" :class="{ selected: activeBucketId === bucket.id }" @click="chooseBucket(bucket)">
          <Globe2 v-if="bucket.bucket_type === 'OPEN'" :size="17" /><HardDrive v-else :size="17" />
          {{ bucket.name }}
          <span class="access-pill">{{ bucket.bucket_type }}</span>
        </button>
      </div>

      <section class="storage-panel" v-if="activeBucket">
        <div class="storage-top">
          <div class="storage-icon"><FolderOpen :size="22" /></div>
          <div class="storage-info"><h2>{{ activeBucket.name }}</h2><p>{{ activeBucket.bucket_type }} · {{ isOpen ? 'Общий доступ' : 'Личное хранилище' }}</p></div>
          <span class="status-dot"><i></i> {{ isOpen ? 'Доступно гостям' : 'Только вы' }}</span>
        </div>
        <div class="storage-stats">
          <div><span>Файлов</span><strong>{{ files.length }}</strong></div>
          <div><span>Занято</span><strong>{{ formatBytes(totalBytes) }}</strong></div>
          <div><span>Тип хранилища</span><strong>{{ activeBucket.bucket_type }}</strong></div>
        </div>
      </section>

      <section class="file-section">
        <div class="file-toolbar">
          <div><h2>Содержимое</h2><p class="muted">{{ filteredFiles.length }} {{ filteredFiles.length === 1 ? 'элемент' : 'элементов' }}</p></div>
          <div class="toolbar-actions">
            <label class="search-box"><Search :size="17" /><input v-model="search" placeholder="Найти файл..." /></label>
            <button class="icon-button" title="Изменить сортировку" @click="sortNewest = !sortNewest"><ArrowUpDown :size="17" /></button>
            <input ref="fileInput" type="file" multiple hidden @change="uploadSelected" />
            <button v-if="canUpload" class="primary-button upload-button" @click="fileInput?.click()" :disabled="uploading || !activeBucketId"><LoaderCircle v-if="uploading" class="spinning" :size="17" /><Upload v-else :size="17" /> {{ uploading ? 'Загрузка…' : 'Загрузить' }}</button>
            <RouterLink v-else to="/login" class="primary-button upload-button">Войти для загрузки</RouterLink>
          </div>
        </div>

        <div v-if="loading || bucketsLoading" class="state-box"><LoaderCircle class="spinning" :size="25" /><span>Загружаем хранилища и файлы…</span></div>
        <div v-else-if="!error && filteredFiles.length === 0" class="empty-state">
          <div class="empty-icon"><FolderOpen :size="30" /></div>
          <h3>{{ search ? 'Ничего не найдено' : 'Здесь пока пусто' }}</h3>
          <p>{{ search ? 'Попробуйте изменить поисковый запрос.' : 'Загрузите первый файл в это хранилище.' }}</p>
          <button v-if="!search && canUpload && activeBucketId" class="secondary-button" @click="fileInput?.click()"><Upload :size="16" /> Выбрать файлы</button>
        </div>
        <div v-else-if="!error" class="file-table-wrap">
          <table class="file-table">
            <thead><tr><th>ИМЯ</th><th>РАЗМЕР</th><th>ИЗМЕНЁН</th><th></th></tr></thead>
            <tbody>
              <tr v-for="file in filteredFiles" :key="file.filename">
                <td><div class="file-name"><span class="file-type-icon"><component :is="iconFor(file.filename)" :size="19" /></span><span class="file-name-text"><strong>{{ file.filename }}</strong><small>{{ file.filename.split('.').pop()?.toUpperCase() || 'FILE' }}</small></span></div></td>
                <td class="muted">{{ formatBytes(file.size) }}</td>
                <td class="muted">{{ formatDate(file.last_modified) }}</td>
                <td class="actions-cell">
                  <button class="icon-button small" title="Скачать" @click="downloadFile(file)"><ArrowDownToLine :size="16" /></button>
                  <div class="menu-wrap">
                    <button class="icon-button small" title="Другие действия" @click="menuFor = menuFor === file.filename ? null : file.filename"><MoreHorizontal :size="18" /></button>
                    <div v-if="menuFor === file.filename" class="context-menu">
                      <button v-if="canManage" @click="beginRename(file)"><Pencil :size="15" /> Переименовать</button>
                      <button v-if="canManage" class="danger-action" @click="removeFile(file)"><Trash2 :size="15" /> Удалить</button>
                      <span v-if="!canManage" class="menu-hint">Изменение доступно владельцу или администратору</span>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <div v-if="renameTarget" class="modal-backdrop" @click.self="renameTarget = null">
        <form class="modal-card" @submit.prevent="saveRename">
          <h3>Переименовать файл</h3><p class="muted">{{ renameTarget.filename }}</p>
          <input v-model="newName" class="text-input" autofocus required />
          <div class="modal-actions"><button type="button" class="secondary-button" @click="renameTarget = null">Отмена</button><button class="primary-button">Сохранить</button></div>
        </form>
      </div>
    </div>
  </AppShell>
</template>
