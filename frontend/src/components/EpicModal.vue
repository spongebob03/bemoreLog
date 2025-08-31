<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-panel" :class="{ 'mobile-full': isMobile }">
      <header class="modal-header">
        <h3 class="modal-title">{{ headerTitle }}</h3>
        <button class="icon-button" @click="handleClose" aria-label="닫기">×</button>
      </header>

      <section v-if="mode === 'view' && epic" class="modal-body">
        <div class="epic-detail">
          <h4 class="detail-title">{{ epic.title }}</h4>
          <p class="detail-desc" v-if="epic.description">{{ epic.description }}</p>
          <div class="detail-meta">
            <span class="badge">상태: {{ statusText }}</span>
            <span class="meta">깊이: {{ epic.depth }}</span>
            <span class="meta" v-if="epic.position">위치: {{ epic.position }}</span>
            <span class="meta">하위: {{ epic.subs?.length || 0 }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-primary" @click="switchToEdit">수정하기</button>
          <button 
            class="btn-danger" 
            @click="showDeleteConfirm"
            :title="hasSubEpics ? '하위 epic이 있어도 함께 삭제됩니다' : ''"
          >
            삭제하기
          </button>
          <button class="btn-secondary" @click="handleClose">닫기</button>
        </div>

        <!-- 연결된 습관 현황 섹션 -->
        <div v-if="latestHabit" class="habit-section">
          <div class="habit-section-header">
            <h4>연결된 최신 습관</h4>
            <button 
              class="btn-habit-dashboard"
              @click="showHabitDashboard = true"
            >
              📊 상세 현황 보기
            </button>
          </div>
          <div class="habit-preview">
            <div class="habit-info">
              <h5>{{ latestHabit.title }}</h5>
              <p v-if="latestHabit.description">{{ latestHabit.description }}</p>
            </div>
            <div class="habit-quick-stats">
              <div class="quick-stat">
                <span class="quick-stat-value">{{ latestHabit.current_combo }}</span>
                <span class="quick-stat-label">현재 연속</span>
              </div>
              <div class="quick-stat">
                <span class="quick-stat-value">{{ latestHabit.best_combo }}</span>
                <span class="quick-stat-label">최고 연속</span>
              </div>
              <div class="quick-stat">
                <span class="quick-stat-value">{{ latestHabit.total_completions }}</span>
                <span class="quick-stat-label">총 실천</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 삭제 확인 다이얼로그 -->
      <div v-if="showDeleteDialog" class="delete-confirm-overlay">
        <div class="delete-confirm-panel">
          <h4>Epic 삭제 확인</h4>
          <p>정말로 "{{ epic?.title }}"을(를) 삭제하시겠습니까?</p>
          <p v-if="hasSubEpics" class="warning-text">
            ⚠️ 이 epic에는 {{ epic?.subs?.length || 0 }}개의 하위 epic이 있습니다. 
            삭제하면 모든 하위 epic도 함께 삭제됩니다.
          </p>
          <p class="warning-text">이 작업은 되돌릴 수 없습니다.</p>
          <div class="delete-confirm-actions">
            <button class="btn-danger" @click="confirmDelete" :disabled="isDeleting">
              {{ isDeleting ? '삭제 중...' : '삭제' }}
            </button>
            <button class="btn-secondary" @click="cancelDelete" :disabled="isDeleting">취소</button>
          </div>
        </div>
      </div>

      <section v-else-if="mode === 'create'" class="modal-body">
        <EpicForm
          :mode="'create'"
          :initialEpic="undefined"
          :defaultCoreEpicId="defaultCoreEpicId"
          :selected-position="selectedPosition"
          :grid-index="gridIndex"
          @epic-saved="handleEpicSaved"
          @epic-created="handleEpicCreated"
        />
      </section>

      <section v-else-if="mode === 'edit' && epic" class="modal-body">
        <EpicForm
          :mode="'edit'"
          :initialEpic="epic"
          :defaultCoreEpicId="defaultCoreEpicId"
          :selected-position="selectedPosition"
          :grid-index="gridIndex"
          @epic-saved="handleEpicSaved"
          @epic-created="handleEpicCreated"
        />
      </section>

      <!-- HabitDashboard 모달 -->
      <HabitDashboard
        v-if="showHabitDashboard && latestHabit"
        :habitId="latestHabit.id"
        @close="showHabitDashboard = false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import EpicForm from './EpicForm.vue';
import HabitDashboard from './HabitDashboard.vue';
import epicService from '../services/epicService';
import habitService, { type Habit } from '../services/habitService';
import type { Epic } from '../services/epicService';

interface Props {
  mode?: 'view' | 'create' | 'edit';
  epic: Epic | null;
  isCreate?: boolean;
  selectedPosition?: { row: number; col: number } | null;
  defaultCoreEpicId?: number | null;
  gridIndex?: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  close: [];
  saved: [];
  'start-edit': [];
  'epic-created': [];
  'epic-updated': [];
  'epic-deleted': [];
}>();

const isMobile = ref(false);
const isEditMode = ref(false);
const showDeleteDialog = ref(false);
const isDeleting = ref(false);

// Habit 관련 상태
const latestHabit = ref<Habit | null>(null);
const showHabitDashboard = ref(false);

const checkIsMobile = () => {
  isMobile.value = window.matchMedia('(max-width: 640px)').matches;
};

// 최신 습관 로드
const loadLatestHabit = async () => {
  if (!props.epic?.id) {
    latestHabit.value = null;
    return;
  }

  try {
    const habits = await habitService.getHabits(props.epic.id);
    if (habits.length > 0) {
      // 가장 최근에 생성된 습관 또는 가장 최근에 업데이트된 습관 선택
      const sortedHabits = habits.sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at);
        const dateB = new Date(b.updated_at || b.created_at);
        return dateB.getTime() - dateA.getTime();
      });
      latestHabit.value = sortedHabits[0];
    } else {
      latestHabit.value = null;
    }
  } catch (error) {
    console.error('Error loading latest habit:', error);
    latestHabit.value = null;
  }
};

// Epic이 변경될 때마다 습관 다시 로드
watch(() => props.epic?.id, (newEpicId) => {
  if (newEpicId) {
    loadLatestHabit();
  } else {
    latestHabit.value = null;
  }
}, { immediate: true });

onMounted(() => {
  checkIsMobile();
  window.addEventListener('resize', checkIsMobile);
  document.body.style.overflow = 'hidden';
});

onUnmounted(() => {
  window.removeEventListener('resize', checkIsMobile);
  document.body.style.overflow = '';
});

const mode = computed<'view' | 'create' | 'edit'>(() => {
  if (props.isCreate) return 'create';
  if (isEditMode.value) return 'edit';
  if (props.epic) return 'view';
  return 'view';
});

const headerTitle = computed(() => {
  if (mode.value === 'create') return '새 Epic 생성';
  if (mode.value === 'edit') return 'Epic 수정';
  return 'Epic 상세';
});

const statusText = computed(() => {
  if (!props.epic) return '';
  const statusMap: Record<string, string> = {
    todo: '할 일',
    running: '진행 중',
    done: '완료',
    blocked: '차단됨',
  };
  return statusMap[props.epic.status] || props.epic.status;
});

// 하위 epic이 있는지 안전하게 확인
const hasSubEpics = computed(() => {
  if (!props.epic || !props.epic.subs) return false;
  return Array.isArray(props.epic.subs) && props.epic.subs.length > 0;
});

const handleSaved = () => emit('saved');
const handleEpicSaved = () => {
  isEditMode.value = false;
  emit('epic-updated');
};
const handleEpicCreated = () => {
  isEditMode.value = false;
  emit('epic-created');
};
const switchToEdit = () => {
  // edit 모드로 전환
  isEditMode.value = true;
};

// 삭제 관련 메서드들
const showDeleteConfirm = () => {
  showDeleteDialog.value = true;
};

const cancelDelete = () => {
  showDeleteDialog.value = false;
};

const confirmDelete = async () => {
  if (!props.epic || isDeleting.value) return;
  
  try {
    isDeleting.value = true;
    await epicService.deleteEpic(props.epic.id);
    showDeleteDialog.value = false;
    emit('epic-deleted');
    handleClose();
  } catch (error) {
    console.error('Epic 삭제 중 오류 발생:', error);
    alert('Epic 삭제 중 오류가 발생했습니다.');
  } finally {
    isDeleting.value = false;
  }
};

// 모달 닫기 시 body overflow 복원
const handleClose = () => {
  document.body.style.overflow = '';
  isEditMode.value = false; // edit 모드 초기화
  showDeleteDialog.value = false; // 삭제 다이얼로그도 닫기
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-panel {
  width: 100%;
  max-width: 720px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-panel.mobile-full {
  max-width: none;
  width: 100%;
  height: 100%;
  border-radius: 0;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.icon-button {
  appearance: none;
  border: none;
  background: transparent;
  font-size: 22px;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 16px 20px 20px 20px;
  overflow: auto;
}

.epic-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.detail-desc {
  margin: 0;
  color: #4b5563;
  line-height: 1.5;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #6b7280;
}

.badge {
  background: #eef2ff;
  color: #3730a3;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
}

.meta {
  font-size: 12px;
}

.modal-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.btn-primary,
.btn-secondary,
.btn-danger {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary {
  background: #3b82f6;
  color: #ffffff;
}

.btn-secondary {
  background: #f3f4f6;
  color: #111827;
  border: 1px solid #e5e7eb;
}

.btn-danger {
  background: #ef4444;
  color: #ffffff;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-disabled {
  background: #9ca3af !important;
  color: #6b7280 !important;
  cursor: not-allowed !important;
}

.btn-disabled:hover {
  background: #9ca3af !important;
}

/* 삭제 확인 다이얼로그 스타일 */
.delete-confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 16px;
}

.delete-confirm-panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.delete-confirm-panel h4 {
  margin: 0 0 16px 0;
  color: #dc2626;
  font-size: 18px;
  font-weight: 600;
}

.delete-confirm-panel p {
  margin: 0 0 8px 0;
  color: #374151;
  line-height: 1.5;
}

.warning-text {
  color: #dc2626 !important;
  font-weight: 500;
  font-size: 14px;
}

.delete-confirm-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.delete-confirm-actions .btn-danger {
  flex: 1;
}

.delete-confirm-actions .btn-secondary {
  flex: 1;
}

/* 습관 섹션 스타일 */
.habit-section {
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
  border-radius: 12px;
  border: 1px solid #f59e0b;
}

.habit-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.habit-section-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #92400e;
}

.btn-habit-dashboard {
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-habit-dashboard:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.habit-preview {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.habit-info {
  flex: 1;
}

.habit-info h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
}

.habit-info p {
  margin: 0;
  font-size: 12px;
  color: #a16207;
  line-height: 1.4;
}

.habit-quick-stats {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.quick-stat {
  text-align: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  min-width: 60px;
}

.quick-stat-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #92400e;
  line-height: 1;
}

.quick-stat-label {
  display: block;
  font-size: 10px;
  color: #a16207;
  margin-top: 4px;
}

@media (max-width: 640px) {
  .modal-actions {
    flex-direction: column;
  }
  
  .habit-preview {
    flex-direction: column;
    gap: 12px;
  }
  
  .habit-quick-stats {
    justify-content: center;
    gap: 12px;
  }
  
  .habit-section-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
}
</style>


