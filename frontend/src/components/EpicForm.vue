<template>
  <form @submit.prevent="handleSubmit" class="epic-form">
    <div class="form-row">
      <div class="form-group">
        <label for="title" class="form-label">제목 *</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          required
          class="form-input"
          placeholder="Epic 제목을 입력하세요"
        />
      </div>
      
      <div class="form-group">
        <label for="status" class="form-label">상태 *</label>
        <select
          id="status"
          v-model="form.status"
          required
          class="form-select"
        >
          <option value="todo">할 일</option>
          <option value="running">진행 중</option>
          <option value="done">완료</option>
          <option value="blocked">차단됨</option>
        </select>
      </div>
    </div>
    
    <div class="form-group">
      <label for="description" class="form-label">설명</label>
      <textarea
        id="description"
        v-model="form.description"
        class="form-textarea"
        rows="3"
        placeholder="Epic에 대한 설명을 입력하세요"
      ></textarea>
    </div>
    
    <div class="form-group">
      <label for="core_epic_id" class="form-label">상위 Epic (선택사항)</label>
      <select
        id="core_epic_id"
        v-model="form.core_epic_id"
        class="form-select"
      >
        <option value="">상위 Epic 없음 (Core Epic)</option>
        <option 
          v-for="epic in coreEpics" 
          :key="epic.id" 
          :value="epic.id"
        >
          {{ epic.title }}
        </option>
      </select>
    </div>
    
    <div class="form-actions">
      <button 
        type="submit" 
        class="btn-primary"
        :disabled="loading"
      >
        {{ loading ? '생성 중...' : 'Epic 생성' }}
      </button>
      <button 
        type="button" 
        @click="resetForm"
        class="btn-secondary"
      >
        초기화
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import epicService, { type Epic } from '../services/epicService';

interface EpicCreate {
  title: string;
  description: string;
  status: string;
  core_epic_id?: number | null;
}

const emit = defineEmits<{
  'epic-created': [];
}>();

const form = ref<EpicCreate>({
  title: '',
  description: '',
  status: 'todo',
  core_epic_id: null
});

const coreEpics = ref<Epic[]>([]);
const loading = ref(false);

// Core Epic 목록 로드 (depth 0인 epic들)
const loadCoreEpics = async () => {
  try {
    const allEpics = await epicService.getEpics();
    coreEpics.value = allEpics.filter(epic => epic.depth === 0);
  } catch (error) {
    console.error('Failed to load core epics:', error);
  }
};

// 폼 제출
const handleSubmit = async () => {
  try {
    loading.value = true;
    
    const epicData: EpicCreate = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      status: form.value.status,
      core_epic_id: form.value.core_epic_id || null
    };
    
    await epicService.createEpic(epicData);
    
    // 성공 시 폼 초기화 및 이벤트 발생
    resetForm();
    emit('epic-created');
    
    // Core Epic 목록 새로고침
    await loadCoreEpics();
    
  } catch (error) {
    console.error('Failed to create epic:', error);
    alert('Epic 생성에 실패했습니다.');
  } finally {
    loading.value = false;
  }
};

// 폼 초기화
const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    status: 'todo',
    core_epic_id: null
  };
};

// 컴포넌트 마운트 시 Core Epic 목록 로드
onMounted(() => {
  loadCoreEpics();
});
</script>

<style scoped>
.epic-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input,
.form-select,
.form-textarea {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-start;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
