<template>
  <div class="grape-view">
    <div class="grape-header">
      <h3>{{ totalCommits }}번 실천 • {{ completedClusters }}개 포도송이 완성!</h3>
      <div class="grape-stats">
        <div class="current-progress">
          현재 포도송이: {{ currentClusterProgress }}/30 ({{ Math.round((currentClusterProgress / 30) * 100) }}%)
        </div>
      </div>
    </div>

    <div class="grape-container">
      <!-- 누적 기반 포도송이들 -->
      <div class="grape-grid">
        <div 
          v-for="(cluster, clusterIndex) in grapeClusterData" 
          :key="`cluster-${clusterIndex}`"
          class="grape-cluster-card"
          :class="{ 'completed': cluster.isCompleted }"
        >
          <div class="cluster-header">
            <h4>{{ clusterIndex + 1 }}번째 포도송이</h4>
            <span class="cluster-stats">
              {{ cluster.filledCount }}/30
              <span v-if="cluster.isCompleted" class="completed-badge">✨ 완성!</span>
            </span>
          </div>
          
          <!-- 포도송이 클러스터 (코드 기반 - 큰 사이즈) -->
          <div class="grape-cluster-large">
            <!-- 포도 줄기 -->
            <div class="grape-stem-large"></div>
            
            <!-- 포도 알갱이들 (30개 고정) -->
            <div class="grapes-large">
              <div 
                v-for="rowIndex in 8" 
                :key="`row-${rowIndex}`"
                class="grape-row-large"
                :class="`row-${rowIndex - 1}`"
              >
                <div
                  v-for="grapeIndex in getGrapesInRow(rowIndex - 1)"
                  :key="`grape-${grapeIndex}`"
                  class="grape-large"
                  :class="[
                    cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)]?.filled ? 'filled' : 'empty',
                    { 'latest': cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)]?.isLatest }
                  ]"
                  :title="getGrapeTooltip(cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)], clusterIndex)"
                  @click="handleGrapeClick(cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)])"
                >
                  <div class="grape-inner-large">
                    <div v-if="cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)]?.filled" class="grape-shine-large"></div>
                    <span v-if="cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)]?.number" class="grape-number-large">
                      {{ cluster.grapes[getGrapeGlobalIndex(rowIndex - 1, grapeIndex - 1)].number }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 클러스터 진척도 -->
          <div class="cluster-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${(cluster.filledCount / 30) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 선택된 날짜 상세 정보 -->
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
import { ref, computed } from 'vue';
import type { HabitCommit } from '../services/habitService';

interface Props {
  habitId: number;
  commits: HabitCommit[];
}

interface GrapeData {
  number: number;
  filled: boolean;
  isLatest: boolean;
  commit?: HabitCommit;
  date?: string;
}

interface ClusterData {
  grapes: GrapeData[];
  filledCount: number;
  isCompleted: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'date-click': [date: string];
}>();

const selectedDayInfo = ref<any>(null);

// 포도송이 클러스터 데이터 생성 (시간순 정렬된 커밋 사용)
const grapeClusterData = computed((): ClusterData[] => {
  const totalCommits = sortedCommits.value.length;
  const clustersNeeded = Math.max(1, Math.ceil(totalCommits / 30)); // 최소 1개 클러스터
  
  const clusters: ClusterData[] = [];
  
  for (let clusterIndex = 0; clusterIndex < clustersNeeded; clusterIndex++) {
    const grapes: GrapeData[] = [];
    const startCommitIndex = clusterIndex * 30;
    const endCommitIndex = Math.min(startCommitIndex + 30, totalCommits);
    
    // 30개 포도알 생성
    for (let grapeIndex = 0; grapeIndex < 30; grapeIndex++) {
      const commitIndex = startCommitIndex + grapeIndex;
      const isFilled = commitIndex < totalCommits;
      const isLatest = commitIndex === totalCommits - 1; // 가장 최근 실천
      
      grapes.push({
        number: commitIndex + 1, // 전체 누적 번호
        filled: isFilled,
        isLatest,
        commit: isFilled ? sortedCommits.value[commitIndex] : undefined,
        date: isFilled ? sortedCommits.value[commitIndex].created_at : undefined
      });
    }
    
    const filledCount = endCommitIndex - startCommitIndex;
    const isCompleted = filledCount >= 30;
    
    clusters.push({
      grapes,
      filledCount,
      isCompleted
    });
  }
  
  return clusters;
});

// 각 행에 표시할 포도 개수 (역삼각형 포도송이 모양)
const getGrapesInRow = (rowIndex: number): number => {
  const naturalCounts = [4, 5, 6, 5, 4, 3, 2, 1]; // 총 30개, 역삼각형 형태
  return naturalCounts[rowIndex] || 0;
};

// 글로벌 인덱스 계산 (행과 열 → 전체 인덱스)
const getGrapeGlobalIndex = (rowIndex: number, colIndex: number): number => {
  const rowCounts = [4, 5, 6, 5, 4, 3, 2, 1];
  let index = 0;
  
  // 이전 행들의 포도 개수 합산
  for (let i = 0; i < rowIndex; i++) {
    index += rowCounts[i];
  }
  
  return index + colIndex;
};

// 정렬된 커밋 리스트 (포도뷰와 잔디뷰 동일한 데이터 보장)
const sortedCommits = computed(() => {
  console.log('Grape View - Total commits:', props.commits.length);
  const sorted = [...props.commits].sort((a, b) => 
    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );
  console.log('Grape View - Sorted commits:', sorted);
  return sorted;
});

// 총 실천 횟수 (정렬된 커밋 기준)
const totalCommits = computed(() => {
  return sortedCommits.value.length;
});

// 완성된 포도송이 개수
const completedClusters = computed(() => {
  return grapeClusterData.value.filter(cluster => cluster.isCompleted).length;
});

// 현재 포도송이 진척도
const currentClusterProgress = computed(() => {
  const currentCluster = grapeClusterData.value[grapeClusterData.value.length - 1];
  return currentCluster ? currentCluster.filledCount : 0;
});

// 포도 툴팁 텍스트
const getGrapeTooltip = (grape: GrapeData | undefined, clusterIndex: number): string => {
  if (!grape) return '';
  
  if (!grape.filled) {
    return `${grape.number}번째 실천을 기다리는 중...`;
  }
  
  const date = grape.date ? formatDate(grape.date) : '';
  return `${grape.number}번째 실천 (${date})${grape.isLatest ? ' - 최신!' : ''}`;
};

// 포도 클릭 핸들러
const handleGrapeClick = (grape: GrapeData | undefined) => {
  if (!grape || !grape.filled || !grape.commit) return;
  
  selectedDayInfo.value = {
    date: grape.date,
    commitCount: 1,
    commits: [grape.commit]
  };
  
  if (grape.date) {
    emit('date-click', grape.date.split('T')[0]);
  }
};

// 날짜 포맷팅
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return `${date.getMonth() + 1}월 ${date.getDate()}일`;
};
</script>

<style scoped>
.grape-view {
  background: 
    radial-gradient(circle at 20% 20%, rgba(168, 85, 247, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(147, 51, 234, 0.03) 0%, transparent 50%),
    linear-gradient(135deg, #ffffff 0%, #fefbff 100%);
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  position: relative;
}

.grape-view::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(147, 51, 234, 0.02) 1px, transparent 1px),
    radial-gradient(circle at 75% 75%, rgba(168, 85, 247, 0.02) 1px, transparent 1px);
  background-size: 40px 40px, 60px 60px;
  pointer-events: none;
  opacity: 0.5;
  z-index: 0;
}

.grape-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
  position: relative;
  z-index: 1;
}

.grape-header h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: #92400e;
  font-weight: 600;
}

.grape-stats {
  display: flex;
  gap: 16px;
  align-items: center;
}

.current-progress {
  font-size: 0.875rem;
  color: #a16207;
  font-weight: 500;
  background: rgba(251, 191, 36, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
}

.grape-container {
  padding: 20px;
  position: relative;
  z-index: 1;
}

.grape-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.grape-cluster-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: linear-gradient(145deg, #ffffff 0%, #fef7ff 50%, #faf5ff 100%);
  border-radius: 20px;
  border: 2px solid transparent;
  background-clip: padding-box;
  box-shadow: 
    0 8px 32px rgba(147, 51, 234, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.grape-cluster-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(145deg, rgba(147, 51, 234, 0.1), rgba(168, 85, 247, 0.05));
  border-radius: 20px;
  padding: 2px;
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  pointer-events: none;
}

.grape-cluster-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 16px 48px rgba(147, 51, 234, 0.15),
    0 8px 16px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.grape-cluster-card.completed {
  background: linear-gradient(145deg, #f0fdf4 0%, #dcfce7 50%, #bbf7d0 100%);
  box-shadow: 
    0 8px 32px rgba(34, 197, 94, 0.2),
    0 2px 8px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  animation: completedGlow 3s ease-in-out infinite alternate;
}

.grape-cluster-card.completed::before {
  background: linear-gradient(145deg, rgba(34, 197, 94, 0.2), rgba(74, 222, 128, 0.1));
}

@keyframes completedGlow {
  0% {
    box-shadow: 
      0 8px 32px rgba(34, 197, 94, 0.2),
      0 2px 8px rgba(0, 0, 0, 0.05),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
  }
  100% {
    box-shadow: 
      0 12px 40px rgba(34, 197, 94, 0.3),
      0 4px 12px rgba(0, 0, 0, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 1);
  }
}

.cluster-header {
  text-align: center;
  margin-bottom: 12px;
}

.cluster-header h4 {
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  color: #92400e;
  font-weight: 600;
}

.grape-cluster-card.completed .cluster-header h4 {
  color: #166534;
}

.cluster-stats {
  font-size: 0.75rem;
  color: #a16207;
  display: flex;
  align-items: center;
  gap: 8px;
}

.grape-cluster-card.completed .cluster-stats {
  color: #166534;
}

.completed-badge {
  font-size: 0.6875rem;
  background: linear-gradient(135deg, #4ade80, #22c55e);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.grape-cluster {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 12px;
}

.grape-stem {
  width: 6px;
  height: 20px;
  background: linear-gradient(to bottom, #22c55e 0%, #16a34a 50%, #15803d 100%);
  border-radius: 3px;
  margin: 0 auto 12px auto;
  position: relative;
  box-shadow: 
    inset -1px 0 2px rgba(0, 0, 0, 0.2),
    inset 1px 0 1px rgba(255, 255, 255, 0.3);
}

.grape-stem::before {
  content: '';
  position: absolute;
  top: -3px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 8px;
  background: radial-gradient(circle, #16a34a 30%, #22c55e 100%);
  border-radius: 50%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.grape-stem::after {
  content: '';
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%) rotate(-30deg);
  width: 12px;
  height: 2px;
  background: linear-gradient(90deg, #16a34a, #22c55e);
  border-radius: 1px;
  transform-origin: left center;
}

.grapes {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: center;
}

.grape-row {
  display: flex;
  gap: 3px;
  justify-content: center;
}

.grape {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: none;
  transform-origin: center;
}

.grape.empty {
  background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
  border: 2px dashed #cbd5e1;
  opacity: 0.6;
  animation: breathe 4s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { 
    opacity: 0.6; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.8; 
    transform: scale(1.02);
  }
}

.grape.filled {
  background: 
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%),
    linear-gradient(135deg, #a855f7 0%, #9333ea 40%, #7c3aed 100%);
  box-shadow: 
    0 4px 8px rgba(147, 51, 234, 0.3),
    0 2px 4px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  animation: grapeGlow 2s ease-in-out infinite alternate;
}

@keyframes grapeGlow {
  0% {
    box-shadow: 
      0 4px 8px rgba(147, 51, 234, 0.3),
      0 2px 4px rgba(0, 0, 0, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
  100% {
    box-shadow: 
      0 6px 12px rgba(147, 51, 234, 0.4),
      0 3px 6px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.4);
  }
}

.grape.latest {
  background: 
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%),
    linear-gradient(135deg, #fbbf24 0%, #f59e0b 40%, #d97706 100%);
  box-shadow: 
    0 0 0 3px rgba(245, 158, 11, 0.4),
    0 6px 16px rgba(245, 158, 11, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
  animation: latestPulse 2s ease-in-out infinite;
  transform: scale(1.1);
}

@keyframes latestPulse {
  0%, 100% {
    box-shadow: 
      0 0 0 3px rgba(245, 158, 11, 0.4),
      0 6px 16px rgba(245, 158, 11, 0.4),
      0 2px 4px rgba(0, 0, 0, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.5);
  }
  50% {
    box-shadow: 
      0 0 0 6px rgba(245, 158, 11, 0.2),
      0 8px 20px rgba(245, 158, 11, 0.5),
      0 4px 8px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.6);
  }
}

.grape:hover {
  transform: scale(1.4);
  z-index: 20;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.grape.latest:hover {
  transform: scale(1.5);
}

.grape-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
}

.grape-shine {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
}

.grape-number {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 7px;
  color: white;
  font-weight: 700;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
  text-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.8),
    0 0 4px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  letter-spacing: -0.5px;
}

.grape.empty .grape-number {
  color: #64748b;
  font-weight: 600;
  text-shadow: none;
  opacity: 0.7;
}

.grape.latest .grape-number {
  color: #1f2937;
  text-shadow: 
    0 1px 2px rgba(255, 255, 255, 0.8),
    0 0 4px rgba(255, 255, 255, 0.4);
  font-weight: 800;
}

.cluster-progress {
  width: 100%;
  text-align: center;
  margin-top: 12px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: linear-gradient(90deg, #f1f5f9, #e2e8f0);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 4px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.progress-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.4));
  border-radius: 6px 6px 0 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a855f7 0%, #9333ea 50%, #7c3aed 100%);
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 
    0 2px 4px rgba(147, 51, 234, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.progress-fill::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.2));
  border-radius: 6px 6px 0 0;
}

.grape-cluster-card.completed .progress-fill {
  background: linear-gradient(90deg, #4ade80 0%, #22c55e 50%, #16a34a 100%);
  box-shadow: 
    0 2px 4px rgba(34, 197, 94, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  animation: completedProgress 2s ease-in-out infinite alternate;
}

@keyframes completedProgress {
  0% {
    box-shadow: 
      0 2px 4px rgba(34, 197, 94, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.4);
  }
  100% {
    box-shadow: 
      0 4px 8px rgba(34, 197, 94, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.5);
  }
}

.day-detail {
  margin-top: 20px;
  padding: 16px 20px;
  background: #fefce8;
  border-top: 1px solid #fde047;
}

.day-detail h4 {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  color: #92400e;
}

.day-detail p {
  margin: 0 0 12px 0;
  font-size: 0.75rem;
  color: #a16207;
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
  border: 1px solid #fde047;
}

.commit-effort {
  font-size: 0.75rem;
  font-weight: 500;
  color: #7c3aed;
  background: #f3e8ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.commit-desc {
  font-size: 0.75rem;
  color: #374151;
  flex: 1;
}

/* 큰 사이즈 코드 기반 포도송이 스타일 */
.grape-cluster-large {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
}

.grape-stem-large {
  width: 12px;
  height: 40px;
  background: linear-gradient(to bottom, #22c55e 0%, #16a34a 50%, #15803d 100%);
  border-radius: 6px;
  margin: 0 auto 20px auto;
  position: relative;
  box-shadow: 
    inset -2px 0 4px rgba(0, 0, 0, 0.2),
    inset 2px 0 2px rgba(255, 255, 255, 0.3);
}

.grape-stem-large::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 16px;
  background: radial-gradient(circle, #16a34a 30%, #22c55e 100%);
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.grape-stem-large::after {
  content: '';
  position: absolute;
  top: -16px;
  left: 50%;
  transform: translateX(-50%) rotate(-30deg);
  width: 24px;
  height: 4px;
  background: linear-gradient(90deg, #16a34a, #22c55e);
  border-radius: 2px;
  transform-origin: left center;
}

.grapes-large {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.grape-row-large {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.grape-large {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: none;
  transform-origin: center;
}

.grape-large.empty {
  background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
  border: 3px dashed #cbd5e1;
  opacity: 0.6;
  animation: breatheLarge 4s ease-in-out infinite;
}

@keyframes breatheLarge {
  0%, 100% { 
    opacity: 0.6; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.8; 
    transform: scale(1.03);
  }
}

.grape-large.filled {
  background: 
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%),
    linear-gradient(135deg, #a855f7 0%, #9333ea 40%, #7c3aed 100%);
  box-shadow: 
    0 8px 16px rgba(147, 51, 234, 0.3),
    0 4px 8px rgba(0, 0, 0, 0.1),
    inset 0 2px 4px rgba(255, 255, 255, 0.3);
  animation: grapeGlowLarge 2s ease-in-out infinite alternate;
}

@keyframes grapeGlowLarge {
  0% {
    box-shadow: 
      0 8px 16px rgba(147, 51, 234, 0.3),
      0 4px 8px rgba(0, 0, 0, 0.1),
      inset 0 2px 4px rgba(255, 255, 255, 0.3);
  }
  100% {
    box-shadow: 
      0 12px 24px rgba(147, 51, 234, 0.4),
      0 6px 12px rgba(0, 0, 0, 0.15),
      inset 0 2px 4px rgba(255, 255, 255, 0.4);
  }
}

.grape-large.latest {
  background: 
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%),
    linear-gradient(135deg, #fbbf24 0%, #f59e0b 40%, #d97706 100%);
  box-shadow: 
    0 0 0 4px rgba(245, 158, 11, 0.4),
    0 12px 24px rgba(245, 158, 11, 0.4),
    0 6px 12px rgba(0, 0, 0, 0.1),
    inset 0 2px 4px rgba(255, 255, 255, 0.5);
  animation: latestPulseLarge 2s ease-in-out infinite;
  transform: scale(1.1);
}

@keyframes latestPulseLarge {
  0%, 100% {
    box-shadow: 
      0 0 0 4px rgba(245, 158, 11, 0.4),
      0 12px 24px rgba(245, 158, 11, 0.4),
      0 6px 12px rgba(0, 0, 0, 0.1),
      inset 0 2px 4px rgba(255, 255, 255, 0.5);
  }
  50% {
    box-shadow: 
      0 0 0 8px rgba(245, 158, 11, 0.2),
      0 16px 32px rgba(245, 158, 11, 0.5),
      0 8px 16px rgba(0, 0, 0, 0.15),
      inset 0 2px 4px rgba(255, 255, 255, 0.6);
  }
}

.grape-large:hover {
  transform: scale(1.3);
  z-index: 20;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.grape-large.latest:hover {
  transform: scale(1.4);
}

.grape-inner-large {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
}

.grape-shine-large {
  position: absolute;
  top: 15%;
  left: 25%;
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
}

.grape-number-large {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  color: white;
  font-weight: 800;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.8),
    0 0 8px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  letter-spacing: -0.5px;
}

.grape-large.empty .grape-number-large {
  color: #64748b;
  font-weight: 700;
  text-shadow: none;
  opacity: 0.7;
}

.grape-large.latest .grape-number-large {
  color: #1f2937;
  text-shadow: 
    0 2px 4px rgba(255, 255, 255, 0.8),
    0 0 8px rgba(255, 255, 255, 0.4);
  font-weight: 900;
}

/* 반응형 */
@media (max-width: 768px) {
  .grape-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .grape-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .grape-cluster-card {
    padding: 12px;
  }
  
  /* 큰 포도송이 반응형 */
  .grape-cluster-large {
    padding: 15px;
  }
  
  .grape-stem-large {
    width: 10px;
    height: 32px;
  }
  
  .grape-stem-large::before {
    width: 12px;
    height: 12px;
    top: -5px;
  }
  
  .grape-stem-large::after {
    width: 20px;
    height: 3px;
    top: -12px;
  }
  
  .grapes-large {
    gap: 4px;
  }
  
  .grape-row-large {
    gap: 6px;
  }
  
  .grape-large {
    width: 36px;
    height: 36px;
  }
  
  .grape-number-large {
    font-size: 11px;
  }
  
  .grape-shine-large {
    width: 8px;
    height: 8px;
  }
}
</style>
