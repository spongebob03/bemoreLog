<template>
  <div class="modal-backdrop" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>실천 기록 추가</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="habit-info">
          <h3>{{ habitTitle }}</h3>
          <p v-if="selectedDate" class="selected-date">
            📅 {{ formatDate(selectedDate) }}
          </p>
        </div>

        <form @submit.prevent="saveCommit">
          <div class="form-group">
            <label for="effort">노력도 *</label>
            <div class="effort-selector">
              <div 
                v-for="level in 5"
                :key="level"
                class="effort-level"
                :class="{ 
                  active: form.effort === level,
                  selected: form.effort >= level 
                }"
                @click="form.effort = level"
              >
                <span class="effort-icon">{{ getEffortIcon(level) }}</span>
                <span class="effort-text">{{ getEffortText(level) }}</span>
              </div>
            </div>
            <small class="help-text">
              오늘 이 습관을 실천하는데 얼마나 노력했나요?
            </small>
          </div>
          
          <div class="form-group">
            <label for="description">메모 (선택사항)</label>
            <textarea
              id="description"
              v-model="form.description"
              placeholder="오늘의 실천에 대한 소감이나 메모를 남겨보세요"
              rows="4"
              maxlength="300"
            ></textarea>
            <small class="char-count">{{ form.description.length }}/300</small>
          </div>

          <div class="quick-actions">
            <h4>빠른 입력</h4>
            <div class="quick-buttons">
              <button 
                type="button" 
                class="quick-btn"
                @click="setQuickCommit(1, '조금 했음')"
              >
                😅 조금 했음
              </button>
              <button 
                type="button" 
                class="quick-btn"
                @click="setQuickCommit(3, '보통으로 했음')"
              >
                😊 보통으로 했음
              </button>
              <button 
                type="button" 
                class="quick-btn"
                @click="setQuickCommit(5, '완벽하게 했음!')"
              >
                🔥 완벽하게 했음!
              </button>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              취소
            </button>
            <button 
              type="submit" 
              class="btn btn-primary" 
              :disabled="loading || form.effort === 0"
            >
              {{ loading ? '저장 중...' : '실천 기록 저장' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import habitService from '../services/habitService';

interface Props {
  habitId: number;
  habitTitle: string;
  selectedDate?: string | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  saved: [];
}>();

const loading = ref(false);

const form = reactive({
  effort: 0,
  description: ''
});

const closeModal = () => {
  emit('close');
};

const getEffortIcon = (level: number): string => {
  const icons = ['', '😅', '🙂', '😊', '😄', '🔥'];
  return icons[level] || '';
};

const getEffortText = (level: number): string => {
  const texts = ['', '조금', '어느정도', '보통', '많이', '완벽!'];
  return texts[level] || '';
};

const setQuickCommit = (effort: number, description: string) => {
  form.effort = effort;
  form.description = description;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
};

const saveCommit = async () => {
  if (form.effort === 0) {
    alert('노력도를 선택해주세요.');
    return;
  }

  loading.value = true;

  try {
    const commitData = {
      effort: form.effort,
      description: form.description.trim() || null
    };

    await habitService.createHabitCommit(props.habitId, commitData);
    
    console.log('HabitCommitModal - Commit saved successfully, emitting saved event');
    emit('saved');
  } catch (error) {
    console.error('Error saving habit commit:', error);
    alert('실천 기록 저장에 실패했습니다. 다시 시도해주세요.');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #1f2937;
  background: #f3f4f6;
}

.modal-body {
  padding: 24px;
}

.habit-info {
  margin-bottom: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.habit-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.125rem;
  color: #0c4a6e;
}

.selected-date {
  margin: 0;
  font-size: 0.875rem;
  color: #0369a1;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.effort-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.effort-level {
  flex: 1;
  padding: 12px 8px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.effort-level:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.effort-level.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.effort-level.active {
  border-color: #1d4ed8;
  background: #3b82f6;
  color: white;
}

.effort-icon {
  display: block;
  font-size: 1.5rem;
  margin-bottom: 4px;
}

.effort-text {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
}

.help-text {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  resize: vertical;
  transition: border-color 0.2s;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.char-count {
  display: block;
  text-align: right;
  margin-top: 4px;
  font-size: 0.75rem;
  color: #6b7280;
}

.quick-actions {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.quick-actions h4 {
  margin: 0 0 12px 0;
  font-size: 0.875rem;
  color: #374151;
}

.quick-buttons {
  display: flex;
  gap: 8px;
}

.quick-btn {
  flex: 1;
  padding: 8px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s;
}

.quick-btn:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-secondary {
  background-color: #f9fafb;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background-color: #f3f4f6;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 반응형 */
@media (max-width: 768px) {
  .effort-selector {
    flex-direction: column;
  }
  
  .quick-buttons {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
