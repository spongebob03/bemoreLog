<template>
  <div class="modal-backdrop" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>습관 트랙킹 생성</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="createHabit">
          <div class="form-group">
            <label for="title">습관 제목 *</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              placeholder="예: 매일 물 8잔 마시기"
              maxlength="100"
            />
          </div>
          
          <div class="form-group">
            <label for="description">설명</label>
            <textarea
              id="description"
              v-model="form.description"
              placeholder="습관에 대한 설명을 입력하세요"
              rows="3"
              maxlength="500"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="schedule">스케줄 (Cron)</label>
              <select id="schedule" v-model="form.schedule">
                <option value="">선택하세요</option>
                <option value="0 9 * * *">매일 오전 9시</option>
                <option value="0 9,18 * * *">매일 오전 9시, 오후 6시</option>
                <option value="0 9 * * 1-5">평일 오전 9시</option>
                <option value="0 9 * * 0,6">주말 오전 9시</option>
                <option value="0 */2 * * *">2시간마다</option>
                <option value="custom">직접 입력</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="target_count">목표 횟수</label>
              <input
                id="target_count"
                v-model.number="form.target_count"
                type="number"
                min="1"
                max="100"
              />
            </div>
          </div>
          
          <div v-if="form.schedule === 'custom'" class="form-group">
            <label for="custom_schedule">커스텀 Cron 표현식</label>
            <input
              id="custom_schedule"
              v-model="form.custom_schedule"
              type="text"
              placeholder="예: 0 9 * * * (매일 오전 9시)"
            />
            <small class="help-text">
              Cron 형식: 분 시 일 월 요일 
              <a href="https://crontab.guru/" target="_blank" rel="noopener">도움말</a>
            </small>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              취소
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '생성 중...' : '습관 생성' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import habitService, { type HabitCreate } from '../services/habitService';

interface Props {
  epicId: number;
  epicTitle: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  created: [habit: any];
}>();

const loading = ref(false);

const form = reactive({
  title: '',
  description: '',
  schedule: '0 9 * * *', // 기본값: 매일 오전 9시
  custom_schedule: '',
  target_count: 1
});

const closeModal = () => {
  emit('close');
};

const createHabit = async () => {
  if (!form.title.trim()) {
    alert('습관 제목을 입력해주세요.');
    return;
  }

  loading.value = true;

  try {
    const scheduleValue = form.schedule === 'custom' ? form.custom_schedule : form.schedule;
    
    const habitData: HabitCreate = {
      title: form.title.trim(),
      description: form.description.trim() || null,
      schedule: scheduleValue || null,
      target_count: form.target_count,
      epic_id: props.epicId
    };

    const newHabit = await habitService.createHabit(habitData);
    
    emit('created', newHabit);
    closeModal();
  } catch (error) {
    console.error('Error creating habit:', error);
    alert('습관 생성에 실패했습니다. 다시 시도해주세요.');
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
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
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
}

.close-btn:hover {
  color: #1f2937;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.help-text {
  display: block;
  margin-top: 4px;
  font-size: 0.75rem;
  color: #6b7280;
}

.help-text a {
  color: #3b82f6;
  text-decoration: none;
}

.help-text a:hover {
  text-decoration: underline;
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
  padding: 8px 16px;
  border-radius: 6px;
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
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
