<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="habit-dashboard" @click.stop>
      <div class="dashboard-header">
        <!-- 닫기 버튼 -->
        <button class="close-btn" @click="$emit('close')">&times;</button>
        
        <div class="habit-info">
          <h2 class="habit-title">{{ habit?.title }}</h2>
          <p class="habit-description">{{ habit?.description }}</p>
          <div class="habit-meta">
            <span class="habit-status" :class="`status-${habit?.status}`">
              {{ getStatusText(habit?.status) }}
            </span>
            <span class="habit-schedule">{{ formatSchedule(habit?.schedule) }}</span>
          </div>
        </div>
        
        <div class="habit-stats">
          <div class="stat-item">
            <span class="stat-value">{{ habit?.current_combo }}</span>
            <span class="stat-label">현재 연속</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ habit?.best_combo }}</span>
            <span class="stat-label">최고 연속</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ habit?.total_completions }}</span>
            <span class="stat-label">총 실천</span>
          </div>
        </div>
      </div>

      <div class="dashboard-controls">
        <div class="view-switcher">
          <button 
            class="switch-btn"
            :class="{ active: viewMode === 'github' }"
            @click="viewMode = 'github'"
          >
            🟩 잔디 뷰
          </button>
                  <button 
          class="switch-btn"
          :class="{ active: viewMode === 'grape' }"
          @click="viewMode = 'grape'"
        >
          🍇 포도송이 뷰
        </button>
        </div>
        
        <button class="add-commit-btn" @click="showCommitForm = true">
          ➕ 실천 기록
        </button>
      </div>

      <!-- 깃허브 잔디 스타일 뷰 -->
      <HabitGithubGrassView 
        v-if="viewMode === 'github'"
        :habit-id="habitId"
        :commits="commits"
        @date-click="handleDateClick"
      />

      <!-- 포도송이 스타일 뷰 -->
      <HabitGrapeView 
        v-if="viewMode === 'grape'"
        :habit-id="habitId"
        :commits="commits"
        @date-click="handleDateClick"
      />

      <!-- 실천 기록 추가 모달 -->
      <HabitCommitModal
        v-if="showCommitForm"
        :habit-id="habitId"
        :habit-title="habit?.title || ''"
        :selected-date="selectedDate"
        @close="closeCommitForm"
        @saved="handleCommitSaved"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import habitService, { type Habit, type HabitCommit } from '../services/habitService';
import HabitGithubGrassView from './HabitGithubGrassView.vue';
import HabitGrapeView from './HabitGrapeView.vue';
import HabitCommitModal from './HabitCommitModal.vue';

interface Props {
  habitId: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
}>();

const habit = ref<Habit | null>(null);
const commits = ref<HabitCommit[]>([]);
const loading = ref(false);
const viewMode = ref<'github' | 'grape'>('github');
const showCommitForm = ref(false);
const selectedDate = ref<string | null>(null);

// 상태 텍스트 변환
const getStatusText = (status?: string): string => {
  const statusMap: Record<string, string> = {
    'active': '활성',
    'paused': '일시정지',
    'completed': '완료',
    'archived': '보관됨'
  };
  return statusMap[status || ''] || status || '';
};

// 스케줄 텍스트 포맷팅
const formatSchedule = (schedule?: string): string => {
  if (!schedule) return '스케줄 없음';
  
  const scheduleMap: Record<string, string> = {
    '0 9 * * *': '매일 오전 9시',
    '0 9,18 * * *': '매일 오전 9시, 오후 6시',
    '0 9 * * 1-5': '평일 오전 9시',
    '0 9 * * 0,6': '주말 오전 9시',
    '0 */2 * * *': '2시간마다'
  };
  
  return scheduleMap[schedule] || schedule;
};

// 데이터 로드
const loadHabitData = async () => {
  try {
    loading.value = true;
    
    // 습관 정보와 커밋 데이터를 병렬로 로드
    const [habitData, commitData] = await Promise.all([
      habitService.getHabit(props.habitId),
      habitService.getHabitCommits(props.habitId, 365) // 1년치 데이터
    ]);
    
    habit.value = habitData;
    commits.value = commitData;
    
    console.log('Loaded habit:', habitData);
    console.log('Loaded commits:', commitData);
    
  } catch (error) {
    console.error('Error loading habit data:', error);
    alert('습관 데이터를 불러오는데 실패했습니다.');
  } finally {
    loading.value = false;
  }
};

// 날짜 클릭 핸들러
const handleDateClick = (date: string) => {
  console.log('Date clicked:', date);
  selectedDate.value = date;
  showCommitForm.value = true;
};

// 커밋 폼 닫기
const closeCommitForm = () => {
  showCommitForm.value = false;
  selectedDate.value = null;
};

// 커밋 저장 완료
const handleCommitSaved = async () => {
  console.log('Commit saved, reloading data...');
  const previousCommitCount = commits.value.length;
  
  // 약간의 지연 후 데이터 새로고침 (데이터베이스 반영 대기)
  await new Promise(resolve => setTimeout(resolve, 100));
  await loadHabitData(); // 데이터 새로고침
  
  const newCommitCount = commits.value.length;
  console.log(`Commits count changed: ${previousCommitCount} -> ${newCommitCount}`);
  console.log('New commits data:', commits.value);
  closeCommitForm();
};

// 컴포넌트 마운트
onMounted(() => {
  loadHabitData();
});
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
  overflow-y: auto;
  padding: 10px;
}

.habit-dashboard {
  background: white;
  border-radius: 16px;
  max-width: 1200px;
  width: 95%;
  max-height: 95vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  position: relative;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 60px 24px 24px; /* 우측에 닫기 버튼 공간 확보 */
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 16px 16px 0 0;
  border-bottom: 1px solid #e2e8f0;
  position: relative;
  gap: 20px; /* 요소 간 간격 추가 */
}

.habit-info {
  flex: 1;
}

.habit-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.habit-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.habit-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.habit-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-paused {
  background: #fef3c7;
  color: #92400e;
}

.status-completed {
  background: #dbeafe;
  color: #1e40af;
}

.status-archived {
  background: #f3f4f6;
  color: #374151;
}

.habit-schedule {
  font-size: 0.75rem;
  color: #6b7280;
  background: #f9fafb;
  padding: 4px 8px;
  border-radius: 4px;
}

.habit-stats {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-shrink: 0; /* 축소되지 않도록 */
  min-width: 240px; /* 최소 폭 보장 */
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 4px;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e5e7eb;
  font-size: 1.25rem;
  cursor: pointer;
  color: #6b7280;
  padding: 6px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.close-btn:hover {
  color: #1f2937;
  background: white;
  border-color: #d1d5db;
  transform: scale(1.05);
}

.dashboard-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 24px;
}

.view-switcher {
  display: flex;
  gap: 8px;
}

.switch-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.switch-btn:hover:not(:disabled) {
  border-color: #3b82f6;
  background: #f8fafc;
}

.switch-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.switch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-commit-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.add-commit-btn:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* HabitGithubGrassView에 패딩 추가 */
:deep(.github-grass-view) {
  margin: 0 24px 24px 24px;
  border-radius: 8px;
}

/* HabitGrapeView에 패딩 추가 */
:deep(.grape-view) {
  margin: 0 24px 24px 24px;
  border-radius: 8px;
}

/* 반응형 */
@media (max-width: 768px) {
  .modal-backdrop {
    padding: 10px;
    align-items: flex-start;
    padding-top: 20px;
  }
  
  .habit-dashboard {
    max-height: calc(100vh - 40px);
    border-radius: 12px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    padding: 20px 50px 20px 20px; /* 모바일에서도 닫기 버튼 공간 확보 */
  }
  
  .habit-stats {
    justify-content: center;
    width: 100%;
  }
  
  .dashboard-controls {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
    padding: 0 20px;
  }
  
  .view-switcher {
    justify-content: center;
  }
  
  :deep(.github-grass-view),
  :deep(.grape-view) {
    margin: 0 20px 20px 20px;
  }
  
  .close-btn {
    top: 15px;
    right: 15px;
  }
}
</style>
