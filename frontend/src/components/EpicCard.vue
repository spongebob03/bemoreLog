<template>
  <div 
    class="epic-card"
    :class="{
      'empty': !epic,
      'core-epic': epic && epic.depth === 0,
      'sub-epic': epic && epic.depth > 0,
      'clickable': epic
    }"
    @click="$emit('click')"
  >
    <div v-if="epic" class="epic-content">
      <h3 class="epic-title">{{ epic.title }}</h3>
      <p v-if="epic.description" class="epic-description">
        {{ truncateDescription(epic.description) }}
      </p>
      <div class="epic-meta">
        <span class="epic-status" :class="`status-${epic.status}`">
          {{ getStatusText(epic.status) }}
        </span>
        <span v-if="epic.subs && epic.subs.length > 0" class="epic-subs-count">
          {{ epic.subs.length }}개 하위
        </span>
      </div>
    </div>
    
    <div v-else class="empty-content">
      <div class="empty-icon">+</div>
      <p class="empty-text">빈 셀</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type Epic } from '../services/epicService';

interface Props {
  epic: Epic | null;
  position: string;
}

defineProps<Props>();
defineEmits<{
  click: [];
}>();

// 설명 텍스트 자르기
const truncateDescription = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// 상태 텍스트 변환
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'todo': '할 일',
    'running': '진행 중',
    'done': '완료',
    'blocked': '차단됨'
  };
  return statusMap[status] || status;
};
</script>

<style scoped>
.epic-card {
  width: 100%;
  height: 100%;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: white;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.epic-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.epic-card.core-epic {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.epic-card.sub-epic {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

.epic-card.empty {
  border-style: dashed;
  border-color: #d1d5db;
  background: #f9fafb;
  cursor: default;
}

.epic-card.empty:hover {
  border-color: #d1d5db;
  box-shadow: none;
}

.epic-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.epic-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.epic-description {
  font-size: 11px;
  color: #6b7280;
  margin: 0 0 8px 0;
  line-height: 1.3;
  flex-grow: 1;
}

.epic-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.epic-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.status-todo {
  background: #fef3c7;
  color: #92400e;
}

.status-running {
  background: #dbeafe;
  color: #1e40af;
}

.status-done {
  background: #d1fae5;
  color: #065f46;
}

.status-blocked {
  background: #fee2e2;
  color: #991b1b;
}

.epic-subs-count {
  font-size: 9px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 1px 4px;
  border-radius: 3px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
}

.empty-icon {
  font-size: 24px;
  font-weight: 300;
  margin-bottom: 4px;
}

.empty-text {
  font-size: 11px;
  margin: 0;
}
</style>
