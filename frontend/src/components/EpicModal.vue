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
          <button class="btn-secondary" @click="handleClose">닫기</button>
        </div>
      </section>

      <section v-else-if="mode === 'create'" class="modal-body">
        <EpicForm
          :mode="'create'"
          :initialEpic="undefined"
          :defaultCoreEpicId="defaultCoreEpicId"
          :selected-position="selectedPosition"
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
          @epic-saved="handleEpicSaved"
          @epic-created="handleEpicCreated"
        />
      </section>


    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import EpicForm from './EpicForm.vue';
import type { Epic } from '../services/epicService';

interface Props {
  mode?: 'view' | 'create' | 'edit';
  epic: Epic | null;
  isCreate?: boolean;
  selectedPosition?: { row: number; col: number } | null;
  defaultCoreEpicId?: number | null;
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
const checkIsMobile = () => {
  isMobile.value = window.matchMedia('(max-width: 640px)').matches;
};

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

// 모달 닫기 시 body overflow 복원
const handleClose = () => {
  document.body.style.overflow = '';
  isEditMode.value = false; // edit 모드 초기화
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
.btn-secondary {
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

@media (max-width: 640px) {
  .modal-actions {
    flex-direction: column;
  }
}
</style>


