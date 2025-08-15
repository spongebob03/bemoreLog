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
    
    <div class="form-row">
      <div class="form-group">
        <label for="depth" class="form-label">깊이 (Depth)</label>
        <select
          id="depth"
          v-model.number="form.depth"
          class="form-select"
        >
          <option :value="0">0 - Core Epic (최상위)</option>
          <option :value="1">1 - 하위 Epic</option>
          <option :value="2">2 - 세부 Epic</option>
          <option :value="3">3 - 세부 세부 Epic</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="position" class="form-label">위치 (9x9 테이블)</label>
        <div class="position-inputs">
          <div class="position-input-group">
            <label for="position_x" class="position-label">X:</label>
            <input
              id="position_x"
              v-model="form.positionX"
              type="number"
              min="0"
              max="8"
              class="position-input"
              placeholder="0-8"
            />
          </div>
          <div class="position-input-group">
            <label for="position_y" class="position-label">Y:</label>
            <input
              id="position_y"
              v-model="form.positionY"
              type="number"
              min="0"
              max="8"
              class="position-input"
              placeholder="0-8"
            />
          </div>
        </div>
        <small class="form-help">0-8 사이의 값을 입력하세요. 예: X=4, Y=4는 중앙 위치입니다.</small>
      </div>
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
        {{ submitLabel }}
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
import { ref, onMounted, computed, watch } from 'vue';
import epicService, { type Epic } from '../services/epicService';

type Mode = 'create' | 'edit';

interface EpicCreate {
  title: string;
  description: string;
  status: string;
  depth: number;
  position?: string;
  positionX?: number;
  positionY?: number;
  core_epic_id?: number | null;
}

const props = defineProps<{
  mode?: Mode;
  initialEpic?: Epic;
  defaultCoreEpicId?: number | null;
}>();

const emit = defineEmits<{
  'epic-created': [];
  'epic-saved': [];
}>();

const effectiveMode = computed<Mode>(() => props.mode || (props.initialEpic ? 'edit' : 'create'));

const form = ref<EpicCreate>({
  title: '',
  description: '',
  status: 'todo',
  depth: 0,
  positionX: undefined,
  positionY: undefined,
  core_epic_id: null
});

const coreEpics = ref<Epic[]>([]);
const loading = ref(false);

const submitLabel = computed(() => {
  if (loading.value) return effectiveMode.value === 'edit' ? '저장 중...' : '생성 중...';
  return effectiveMode.value === 'edit' ? '저장' : 'Epic 생성';
});

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
    // positionX와 positionY를 사용하여 position 문자열 생성
    const position = (form.value.positionX !== undefined && form.value.positionY !== undefined) 
      ? `(${form.value.positionX}, ${form.value.positionY})` 
      : undefined;
    
    const epicData: EpicCreate = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      status: form.value.status,
      depth: form.value.depth,
      position: position,
      core_epic_id: form.value.core_epic_id || null
    };

    if (effectiveMode.value === 'edit' && props.initialEpic) {
      await epicService.updateEpic(props.initialEpic.id, epicData);
      emit('epic-saved');
    } else {
      await epicService.createEpic(epicData);
      resetForm();
      emit('epic-created');
    }

    await loadCoreEpics();
  } catch (error) {
    console.error('Failed to submit epic:', error);
    alert(effectiveMode.value === 'edit' ? 'Epic 저장에 실패했습니다.' : 'Epic 생성에 실패했습니다.');
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
    depth: 0,
    position: '',
    positionX: undefined,
    positionY: undefined,
    core_epic_id: null
  };
};

// initialEpic 변경 시 폼 채우기
watch(
  () => props.initialEpic,
  (epic) => {
    if (epic) {
      // 기존 position 값을 파싱하여 positionX, positionY 설정
      let positionX = undefined;
      let positionY = undefined;
      if (epic.position) {
        const match = epic.position.match(/\((\d+),\s*(\d+)\)/);
        if (match) {
          positionX = parseInt(match[1]);
          positionY = parseInt(match[2]);
        }
      }
      
      form.value = {
        title: epic.title,
        description: epic.description || '',
        status: epic.status,
        depth: epic.depth,
        position: epic.position || '',
        positionX: positionX,
        positionY: positionY,
        core_epic_id: epic.core_epic_id ?? null,
      };
    } else {
      resetForm();
    }
  },
  { immediate: true }
);

// defaultCoreEpicId가 주어졌고 생성 모드인 경우 core_epic_id 기본 설정
watch(
  () => [props.defaultCoreEpicId, effectiveMode.value],
  ([defaultId, mode]) => {
    if (mode === 'create') {
      if (defaultId !== undefined && defaultId !== null) {
        form.value.core_epic_id = defaultId as number;
      } else if (form.value.core_epic_id === null) {
        form.value.core_epic_id = null;
      }
    }
  },
  { immediate: true }
);

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

.position-inputs {
  display: flex;
  gap: 12px;
  align-items: center;
}

.position-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.position-label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
}

.position-input {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  transition: border-color 0.2s ease;
}

.position-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-help {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
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
