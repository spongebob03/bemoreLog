<template>
  <div class="github-grass-view">
    <div class="grass-header">
      <h3>{{ totalCommits }}번의 실천 in the last year</h3>
      <div class="legend">
        <span class="legend-text">적음</span>
        <div class="legend-colors">
          <div class="legend-color" :style="{ backgroundColor: getLevelColor(0) }"></div>
          <div class="legend-color" :style="{ backgroundColor: getLevelColor(1) }"></div>
          <div class="legend-color" :style="{ backgroundColor: getLevelColor(2) }"></div>
          <div class="legend-color" :style="{ backgroundColor: getLevelColor(3) }"></div>
          <div class="legend-color" :style="{ backgroundColor: getLevelColor(4) }"></div>
        </div>
        <span class="legend-text">많음</span>
      </div>
    </div>

    <div class="grass-container" :style="{ '--weeks-count': weeksCount }">
      <!-- 요일 라벨 -->
      <div class="weekday-labels">
        <div class="weekday-label"></div>
        <div class="weekday-label">월</div>
        <div class="weekday-label"></div>
        <div class="weekday-label">수</div>
        <div class="weekday-label"></div>
        <div class="weekday-label">금</div>
        <div class="weekday-label"></div>
      </div>

      <!-- 월 라벨 -->
      <div class="month-labels">
        <div 
          v-for="month in monthLabels" 
          :key="`month-${month.index}`"
          class="month-label"
          :style="{ gridColumn: `${month.startCol} / ${month.endCol}` }"
        >
          {{ month.name }}
        </div>
      </div>

      <!-- 잔디 그리드 -->
      <div class="grass-grid">
        <div
          v-for="day in days"
          :key="day.date"
          class="grass-cell"
          :class="{ 
            'has-commit': day.commitCount > 0,
            'today': day.isToday 
          }"
          :style="{ backgroundColor: getLevelColor(day.level) }"
          :title="getTooltipText(day)"
          @click="handleDateClick(day.date)"
        >
        </div>
      </div>
    </div>

    <!-- 상세 정보 패널 -->
    <div v-if="selectedDayInfo" class="day-detail">
      <h4>{{ formatDate(selectedDayInfo.date) }}</h4>
      <p>{{ selectedDayInfo.commitCount }}번 실천</p>
      <div v-if="selectedDayInfo.commits.length > 0" class="commit-list">
        <div 
          v-for="commit in selectedDayInfo.commits" 
          :key="commit.id"
          class="commit-item"
        >
          <span class="commit-effort">노력도: {{ commit.effort }}/5</span>
          <span v-if="commit.description" class="commit-desc">{{ commit.description }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import type { HabitCommit } from '../services/habitService';

interface Props {
  habitId: number;
  commits: HabitCommit[];
}

interface DayData {
  date: string;
  commitCount: number;
  level: number;
  isToday: boolean;
  commits: HabitCommit[];
}

interface MonthLabel {
  name: string;
  index: number;
  startCol: number;
  endCol: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'date-click': [date: string];
}>();

const selectedDayInfo = ref<DayData | null>(null);

// 색상 레벨 (0: 없음, 1-4: 강도별)
const getLevelColor = (level: number): string => {
  const colors = [
    '#ebedf0', // 0: 실천 없음
    '#9be9a8', // 1: 1-2번
    '#40c463', // 2: 3-4번  
    '#30a14e', // 3: 5-6번
    '#216e39'  // 4: 7번 이상
  ];
  return colors[level] || colors[0];
};

// 지난 1년간의 날짜 데이터 생성
const days = computed(() => {
  const today = new Date();
  const yearAgo = new Date(today);
  yearAgo.setFullYear(today.getFullYear() - 1);
  
  // 일요일부터 시작하도록 조정
  const startDate = new Date(yearAgo);
  startDate.setDate(startDate.getDate() - startDate.getDay());
  
  const daysData: DayData[] = [];
  const commitsByDate = new Map<string, HabitCommit[]>();
  
  // 커밋을 날짜별로 그룹화
  props.commits.forEach(commit => {
    const date = new Date(commit.created_at).toISOString().split('T')[0];
    if (!commitsByDate.has(date)) {
      commitsByDate.set(date, []);
    }
    commitsByDate.get(date)!.push(commit);
  });

  // 현재 날짜까지 포함하도록 동적 계산
  const daysToShow = Math.max(371, Math.ceil((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1);
  
  for (let i = 0; i < daysToShow; i++) {
    const currentDate = new Date(startDate);
    currentDate.setDate(startDate.getDate() + i);
    
    const dateString = currentDate.toISOString().split('T')[0];
    const dayCommits = commitsByDate.get(dateString) || [];
    const commitCount = dayCommits.length;
    
    // 실천 횟수에 따른 레벨 계산
    let level = 0;
    if (commitCount > 0) {
      if (commitCount <= 2) level = 1;
      else if (commitCount <= 4) level = 2;
      else if (commitCount <= 6) level = 3;
      else level = 4;
    }
    
    daysData.push({
      date: dateString,
      commitCount,
      level,
      isToday: dateString === today.toISOString().split('T')[0],
      commits: dayCommits
    });
  }
  
  return daysData;
});

// 월 라벨 생성
const monthLabels = computed((): MonthLabel[] => {
  const labels: MonthLabel[] = [];
  let currentMonth = -1;
  let startCol = 1;
  
  const monthNames = [
    '1월', '2월', '3월', '4월', '5월', '6월',
    '7월', '8월', '9월', '10월', '11월', '12월'
  ];
  
  days.value.forEach((day, index) => {
    const month = new Date(day.date).getMonth();
    const col = Math.floor(index / 7) + 1;
    
    if (month !== currentMonth) {
      if (currentMonth !== -1) {
        labels.push({
          name: monthNames[currentMonth],
          index: currentMonth,
          startCol,
          endCol: col
        });
      }
      currentMonth = month;
      startCol = col;
    }
  });
  
  // 마지막 월 추가
  if (currentMonth !== -1) {
    labels.push({
      name: monthNames[currentMonth],
      index: currentMonth,
      startCol,
      endCol: 54 // 53주 + 1
    });
  }
  
  return labels;
});

// 총 실천 횟수
const totalCommits = computed(() => {
  return props.commits.length;
});

// 표시할 주 수 계산
const weeksCount = computed(() => {
  const today = new Date();
  const yearAgo = new Date(today);
  yearAgo.setFullYear(today.getFullYear() - 1);
  const startDate = new Date(yearAgo);
  startDate.setDate(startDate.getDate() - startDate.getDay());
  
  const daysToShow = Math.max(371, Math.ceil((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1);
  return Math.ceil(daysToShow / 7);
});

// 날짜 클릭 핸들러
const handleDateClick = (date: string) => {
  const dayData = days.value.find(d => d.date === date);
  if (dayData) {
    selectedDayInfo.value = dayData;
    emit('date-click', date);
  }
};

// 툴팁 텍스트
const getTooltipText = (day: DayData): string => {
  const date = formatDate(day.date);
  if (day.commitCount === 0) {
    return `${date}: 실천 없음`;
  } else {
    return `${date}: ${day.commitCount}번 실천`;
  }
};

// 날짜 포맷팅
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
};
</script>

<style scoped>
.github-grass-view {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.grass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.grass-header h3 {
  margin: 0;
  font-size: 0.875rem;
  color: #1f2937;
  font-weight: 500;
}

.legend {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-text {
  font-size: 0.75rem;
  color: #6b7280;
}

.legend-colors {
  display: flex;
  gap: 2px;
}

.legend-color {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.grass-container {
  padding: 20px;
  position: relative;
}

.weekday-labels {
  display: grid;
  grid-template-rows: repeat(7, 12px);
  gap: 3px;
  position: absolute;
  left: 0;
  top: 50px;
  width: 20px;
}

.weekday-label {
  font-size: 9px;
  color: #6b7280;
  text-align: right;
  line-height: 12px;
}

.month-labels {
  display: grid;
  grid-template-columns: repeat(var(--weeks-count, 53), 15px);
  gap: 3px;
  margin-left: 25px;
  margin-bottom: 8px;
  height: 15px;
}

.month-label {
  font-size: 10px;
  color: #6b7280;
  text-align: left;
}

.grass-grid {
  display: grid;
  grid-template-rows: repeat(7, 15px);
  grid-template-columns: repeat(var(--weeks-count, 53), 15px);
  gap: 3px;
  margin-left: 25px;
  grid-auto-flow: column;
}

.grass-cell {
  width: 15px;
  height: 15px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.1s ease;
  border: 1px solid rgba(27, 31, 35, 0.06);
}

.grass-cell:hover {
  border-color: rgba(27, 31, 35, 0.3);
  transform: scale(1.1);
}

.grass-cell.today {
  border: 2px solid #3b82f6;
}

.day-detail {
  margin-top: 20px;
  padding: 16px 20px;
  background: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.day-detail h4 {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  color: #1f2937;
}

.day-detail p {
  margin: 0 0 12px 0;
  font-size: 0.75rem;
  color: #6b7280;
}

.commit-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.commit-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.commit-effort {
  font-size: 0.75rem;
  font-weight: 500;
  color: #059669;
  background: #d1fae5;
  padding: 2px 6px;
  border-radius: 3px;
}

.commit-desc {
  font-size: 0.75rem;
  color: #374151;
  flex: 1;
}

/* 반응형 */
@media (max-width: 1100px) {
  .grass-container {
    padding: 15px 10px;
    overflow-x: auto;
  }
  
  .grass-grid {
    min-width: 900px;
  }
}

@media (max-width: 768px) {
  .grass-container {
    padding: 10px;
    overflow-x: auto;
  }
  
  .grass-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .grass-grid {
    min-width: 850px;
  }
}
</style>
