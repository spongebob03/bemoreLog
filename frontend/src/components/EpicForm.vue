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
        <label for="depth" class="form-label">깊이 (Depth) - 자동 설정</label>
        <div class="readonly-field">
          <span class="readonly-value">{{ getDepthText() }}</span>
          <span class="auto-set-badge">자동 설정됨</span>
        </div>
        <small class="form-help">{{ getDepthHelpText() }}</small>
      </div>
      
      <div class="form-group">
        <label for="position" class="form-label">위치 (시계방향 번호) - 자동 설정</label>
        <div class="readonly-field">
          <span class="readonly-value">{{ getPositionText() }}</span>
          <span class="auto-set-badge">자동 설정됨</span>
        </div>
        <div class="position-visual-help">
          <div class="position-grid">
            <div class="position-cell">1</div>
            <div class="position-cell">2</div>
            <div class="position-cell">3</div>
            <div class="position-cell">8</div>
            <div class="position-cell center">0</div>
            <div class="position-cell">4</div>
            <div class="position-cell">7</div>
            <div class="position-cell">6</div>
            <div class="position-cell">5</div>
          </div>
          <small>시계방향 위치 번호</small>
        </div>
      </div>
    </div>
    
    <div class="form-group">
      <label for="core_epic_id" class="form-label">상위 Epic (자동 설정)</label>
      <div v-if="form.core_epic_id" class="auto-parent-epic">
        <div class="parent-epic-info">
          <span class="parent-epic-title">{{ getParentEpicTitle() }}</span>
          <span class="auto-set-badge">자동 설정됨</span>
        </div>
        <small class="form-help">
          {{ getParentEpicHelpText() }}
        </small>
      </div>
      <div v-else class="no-parent-epic">
        <span class="no-parent-text">{{ getNoParentEpicText() }}</span>
      </div>
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
  position?: number;
  core_epic_id?: number | null;
}

const props = defineProps<{
  mode?: Mode;
  initialEpic?: Epic;
  defaultCoreEpicId?: number | null;
  selectedPosition?: { row: number; col: number } | null; // 3x3 그리드 내 상대 위치 (0-2, 0-2)
  gridIndex?: number; // 3x3 그리드의 인덱스 (0-8)
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
  position: 0,
  core_epic_id: null
});

const coreEpics = ref<Epic[]>([]);
const loading = ref(false);

const submitLabel = computed(() => {
  if (loading.value) return effectiveMode.value === 'edit' ? '저장 중...' : '생성 중...';
  return effectiveMode.value === 'edit' ? '저장' : 'Epic 생성';
});

// Core Epic 목록 로드 (depth 0과 1인 epic들 - 상위 epic으로 사용)
const loadCoreEpics = async () => {
  try {
    const allEpics = await epicService.getEpics();
    // depth=0 (core epic)과 depth=1 (sub epic)을 모두 포함
    coreEpics.value = allEpics.filter(epic => epic.depth === 0 || epic.depth === 1);
    console.log('Loaded core epics for parent selection:', coreEpics.value.map(e => `${e.title} (depth: ${e.depth}) at ${e.position}`));
  } catch (error) {
    console.error('Failed to load core epics:', error);
  }
};

// position을 기반으로 상위 epic 자동 찾기
const findParentEpicByPosition = (position: number): Epic | null => {
  // depth=0인 epic은 상위 epic이 없음
  if (form.value.depth === 0) return null;
  
  console.log(`Position ${position} -> Looking for parent epic with depth ${form.value.depth - 1}`);
  console.log(`Grid Index: ${props.gridIndex}`);
  
  // gridIndex를 기반으로 상위 epic 찾기
  let parentEpic: Epic | null = null;
  
  if (props.gridIndex === 4) {
    // 중앙 그리드에서 생성하는 경우
    if (form.value.depth === 1) {
      // depth=1 epic의 상위는 depth=0 epic (중앙)
      parentEpic = coreEpics.value.find(epic => epic.depth === 0 && epic.position === 0) || null;
    }
  } else {
    // 주변 그리드에서 생성하는 경우
    if (form.value.depth === 2) {
      // depth=2 epic의 상위는 해당 그리드의 중앙에 있는 depth=1 epic
      // gridIndex를 position으로 변환하여 찾기
      let targetPosition = 0;
      switch (props.gridIndex) {
        case 0: targetPosition = 1; break; // 좌상단
        case 1: targetPosition = 2; break; // 상단
        case 2: targetPosition = 3; break; // 우상단
        case 3: targetPosition = 8; break; // 좌측
        case 5: targetPosition = 4; break; // 우측
        case 6: targetPosition = 7; break; // 좌하단
        case 7: targetPosition = 6; break; // 하단
        case 8: targetPosition = 5; break; // 우하단
        default: targetPosition = 0;
      }
      
      // 해당 position을 가진 depth=1 epic 찾기
      parentEpic = coreEpics.value.find(epic => 
        epic.depth === 1 && epic.position === targetPosition
      ) || null;
      
      console.log(`Looking for depth=1 epic with position ${targetPosition} in grid ${props.gridIndex}`);
    }
  }
  
  if (!parentEpic) {
    console.log(`No parent epic found for position ${position} with depth ${form.value.depth} in grid ${props.gridIndex}`);
    console.log('Available core epics:', coreEpics.value.map(e => `${e.title} (depth: ${e.depth}) at ${e.position}`));
  } else {
    console.log(`Found parent epic: ${parentEpic.title} (depth: ${parentEpic.depth}, position: ${parentEpic.position})`);
  }
  
  return parentEpic;
};

// 폼 제출
const handleSubmit = async () => {
  try {
    loading.value = true;
    
    // position을 기반으로 상위 epic 자동 설정
    let coreEpicId = form.value.core_epic_id;
    if (form.value.position !== undefined) {
      const parentEpic = findParentEpicByPosition(form.value.position);
      if (parentEpic) {
        coreEpicId = parentEpic.id;
        console.log(`자동으로 상위 epic 설정: ${parentEpic.title} (ID: ${parentEpic.id})`);
      }
    }
    
    // 폼 제출 전 depth와 position 값 확인
    console.log(`=== Epic 제출 전 폼 데이터 ===`);
    console.log(`Title: ${form.value.title}`);
    console.log(`Depth: ${form.value.depth}`);
    console.log(`Position: ${form.value.position}`);
    console.log(`Core Epic ID: ${coreEpicId}`);
    console.log(`===============================`);
    
    const epicData: EpicCreate = {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      status: form.value.status,
      depth: form.value.depth,
      position: form.value.position,
      core_epic_id: coreEpicId
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
    position: 0,
    core_epic_id: null
  };
};

// initialEpic 변경 시 폼 채우기
watch(
  () => props.initialEpic,
  (epic) => {
    if (epic) {
      form.value = {
        title: epic.title,
        description: epic.description || '',
        status: epic.status,
        depth: epic.depth,
        position: epic.position || 0,
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

// selectedPosition 변경 시 position과 depth 자동 설정
watch(
  () => props.selectedPosition,
  (position) => {
    if (position && !props.initialEpic) {
      // row, col을 시계방향 위치 번호로 변환
      // 3x3 그리드 내에서의 상대 위치를 시계방향 번호로 변환
      let relativePosition = 0;
      if (position.row === 0 && position.col === 0) relativePosition = 1;      // 좌상단
      else if (position.row === 0 && position.col === 1) relativePosition = 2;  // 상단
      else if (position.row === 0 && position.col === 2) relativePosition = 3;  // 우상단
      else if (position.row === 1 && position.col === 2) relativePosition = 4;  // 우측
      else if (position.row === 2 && position.col === 2) relativePosition = 5;  // 우하단
      else if (position.row === 2 && position.col === 1) relativePosition = 6;  // 하단
      else if (position.row === 2 && position.col === 0) relativePosition = 7;  // 좌하단
      else if (position.row === 1 && position.col === 0) relativePosition = 8;  // 좌측
      else if (position.row === 1 && position.col === 1) relativePosition = 0;  // 중앙
      
      console.log(`Selected position [${position.row}, ${position.col}] -> 시계방향 번호: ${relativePosition}`);
      form.value.position = relativePosition;
      
      // 위치에 따른 depth 자동 설정
      if (relativePosition === 0) {
        // 중앙 셀은 해당 3x3 그리드의 core epic
        if (props.gridIndex === 4) {
          // 중앙부 3x3 그리드 (index 4)의 중앙 → depth=0 (최상위 Core Epic)
          form.value.depth = 0;
        } else {
          // 주변부 3x3 그리드의 중앙 → depth=1 (중앙부 3x3의 1~8번 epic)
          form.value.depth = 1;
        }
      } else {
        // 주변 셀은 해당 3x3 그리드의 subs epic
        if (props.gridIndex === 4) {
          // 중앙부 3x3 그리드의 주변 셀 → depth=1 (중앙부 3x3의 subs epic)
          form.value.depth = 1;
        } else {
          // 주변부 3x3 그리드의 주변 셀 → depth=2 (주변부 3x3의 subs epic)
          form.value.depth = 2;
        }
      }
      
      console.log(`=== Depth 자동 설정 디버깅 ===`);
      console.log(`Grid Index: ${props.gridIndex}`);
      console.log(`Selected Position: [${props.selectedPosition?.row}, ${props.selectedPosition?.col}]`);
      console.log(`Relative Position: ${relativePosition}`);
      console.log(`Is Center Cell: ${relativePosition === 0}`);
      console.log(`Is Center Grid: ${props.gridIndex === 4}`);
      console.log(`Form Depth Before: ${form.value.depth}`);
      
      // depth 설정 후 확인
      console.log(`Form Depth After: ${form.value.depth}`);
      console.log(`Form Position: ${form.value.position}`);
      console.log(`===============================`);
    }
  },
  { immediate: true }
);

// 상위 epic 제목 가져오기
const getParentEpicTitle = (): string => {
  if (!form.value.core_epic_id) return '';
  const parentEpic = coreEpics.value.find(epic => epic.id === form.value.core_epic_id);
  return parentEpic ? parentEpic.title : '';
};

// 상위 epic 도움말 텍스트 가져오기
const getParentEpicHelpText = (): string => {
  if (!form.value.core_epic_id) return '';
  const parentEpic = coreEpics.value.find(epic => epic.id === form.value.core_epic_id);
  if (!parentEpic) return '';
  
  if (parentEpic.depth === 0) {
    return 'Core Epic (depth=0)이 상위 epic으로 설정되었습니다.';
  } else if (parentEpic.depth === 1) {
    return 'Sub Epic (depth=1)이 상위 epic으로 설정되었습니다.';
  }
  return '위치 기반으로 자동 설정되었습니다. 수동으로 변경하려면 위치를 먼저 변경하세요.';
};

// 상위 epic이 없을 때 텍스트 가져오기
const getNoParentEpicText = (): string => {
  if (form.value.depth === 0) {
    return 'Core Epic (depth=0)은 상위 epic이 없습니다.';
  } else if (form.value.depth === 1) {
    return '위치를 설정하면 Core Epic (depth=0)이 자동으로 상위 epic으로 설정됩니다.';
  } else if (form.value.depth === 2) {
    return '위치를 설정하면 Sub Epic (depth=1)이 자동으로 상위 epic으로 설정됩니다.';
  }
  return '위치를 설정하면 적절한 상위 epic이 자동으로 설정됩니다.';
};

// Depth 텍스트 가져오기
const getDepthText = (): string => {
  switch (form.value.depth) {
    case 0: return '0 - Core Epic (최상위)';
    case 1: return '1 - 하위 Epic';
    case 2: return '2 - 세부 Epic';
    case 3: return '3 - 세부 세부 Epic';
    default: return `${form.value.depth} - Epic`;
  }
};

// Depth 도움말 텍스트 가져오기
const getDepthHelpText = (): string => {
  switch (form.value.depth) {
    case 0: return 'Core Epic은 최상위 Epic으로, 다른 Epic의 상위가 될 수 있습니다.';
    case 1: return '하위 Epic은 Core Epic의 직접적인 하위 Epic입니다.';
    case 2: return '세부 Epic은 하위 Epic의 세부 Epic입니다.';
    case 3: return '세부 세부 Epic은 가장 하위 레벨의 Epic입니다.';
    default: return 'Epic의 계층 레벨입니다.';
  }
};

// Position 텍스트 가져오기
const getPositionText = (): string => {
  switch (form.value.position) {
    case 0: return '0 - 중앙';
    case 1: return '1 - 좌상단';
    case 2: return '2 - 상단';
    case 3: return '3 - 우상단';
    case 4: return '4 - 우측';
    case 5: return '5 - 우하단';
    case 6: return '6 - 하단';
    case 7: return '7 - 좌하단';
    case 8: return '8 - 좌측';
    default: return `${form.value.position} - 위치`;
  }
};

// position 변경 시 상위 epic 자동 업데이트
watch(
  () => [form.value.position, form.value.depth],
  ([position, depth]) => {
    if (position !== undefined && depth !== undefined && depth > 0) {
      const parentEpic = findParentEpicByPosition(position);
      if (parentEpic) {
        form.value.core_epic_id = parentEpic.id;
        console.log(`Position 변경으로 상위 epic 자동 업데이트: ${parentEpic.title}`);
      }
    }
  }
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

.readonly-field {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  min-height: 42px;
}

.readonly-value {
  font-weight: 500;
  color: #374151;
  flex: 1;
}

.position-visual-help {
  margin-top: 12px;
  text-align: center;
}

.position-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  max-width: 120px;
  margin: 0 auto 8px;
}

.position-cell {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.position-cell.center {
  background: #3b82f6;
  color: white;
  border-color: #2563eb;
}

.auto-parent-epic {
  padding: 12px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
}

.parent-epic-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.parent-epic-title {
  font-weight: 600;
  color: #0369a1;
}

.auto-set-badge {
  background: #10b981;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
}

.no-parent-epic {
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.no-parent-text {
  color: #6b7280;
  font-style: italic;
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
