<template>
  <div 
    class="epic-card"
    :class="{
      'empty': !epic,
      'depth-0': epic && epic.depth === 0,
      'depth-1': epic && epic.depth === 1,
      'depth-2': epic && epic.depth === 2,
      'clickable': epic,
      'is-compact': isCompact
    }"
    @click="$emit('click')"
  >
    <div v-if="epic" class="epic-content">
      <h3 class="epic-title">{{ epic.title }}</h3>
      <p v-if="epic.description" class="epic-description">
        {{ truncateDescription(epic.description, getMaxLength()) }}
      </p>
      

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
  isCompact?: boolean;
}

const props = defineProps<Props>();
defineEmits<{
  click: [];
}>();

// 설명 텍스트 자르기
const truncateDescription = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// compact 모드에서 사용할 최대 길이
const getMaxLength = (): number => {
  return props.isCompact ? 30 : 50;
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

/* Depth 0: 진한 에메랄드 초록색 (더 강조된 색) */
.epic-card.depth-0 {
  border-color: #059669;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.epic-card.depth-0:hover {
  border-color: #047857;
  box-shadow: 0 4px 12px rgba(4, 120, 87, 0.15);
}

.epic-card.depth-0 .epic-title {
  color: white;
}

.epic-card.depth-0 .epic-description {
  color: #d1fae5;
}

/* Depth 1: 밝은 초록색 */
.epic-card.depth-1 {
  border-color: #10b981;
  background: linear-gradient(135deg, #6ee7b7 0%, #34d399 100%);
}

.epic-card.depth-1:hover {
  border-color: #059669;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.15);
}

/* Depth 2: 연두색 */
.epic-card.depth-2 {
  border-color: #65a30d;
  background: linear-gradient(135deg, #ecfccb 0%, #d9f99d 100%);
}

.epic-card.depth-2:hover {
  border-color: #4d7c0f;
  box-shadow: 0 4px 12px rgba(77, 124, 15, 0.15);
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

.epic-card:has(.is-compact) .epic-title,
.epic-card.is-compact .epic-title {
  font-size: 12px;
  margin: 0 0 6px 0;
}

.epic-description {
  font-size: 11px;
  color: #6b7280;
  margin: 0 0 8px 0;
  line-height: 1.3;
  flex-grow: 1;
}

.epic-card:has(.is-compact) .epic-description,
.epic-card.is-compact .epic-description {
  font-size: 10px;
  margin: 0 0 6px 0;
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

.epic-card:has(.is-compact) .epic-status,
.epic-card.is-compact .epic-status {
  font-size: 9px;
  padding: 1px 4px;
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

.epic-card:has(.is-compact) .epic-subs-count,
.epic-card.is-compact .epic-subs-count {
  font-size: 8px;
  padding: 1px 3px;
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
