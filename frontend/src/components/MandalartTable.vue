<template>
  <div class="mandalart-container">
    <h2 class="text-2xl font-bold text-center mb-6">만다라트 목표 관리</h2>
    
    <!-- 3x3 만다라트 테이블 -->
    <div class="mandalart-grid">
      <!-- 첫 번째 행 -->
      <div class="mandalart-cell" v-for="i in 3" :key="`row1-${i}`">
        <EpicCard 
          :epic="getEpicAtPosition(0, i-1)" 
          :position="`0,${i-1}`"
          @click="selectEpic(getEpicAtPosition(0, i-1))"
        />
      </div>
      
      <!-- 두 번째 행 -->
      <div class="mandalart-cell" v-for="i in 3" :key="`row2-${i}`">
        <EpicCard 
          :epic="getEpicAtPosition(1, i-1)" 
          :position="`1,${i-1}`"
          @click="selectEpic(getEpicAtPosition(1, i-1))"
        />
      </div>
      
      <!-- 세 번째 행 -->
      <div class="mandalart-cell" v-for="i in 3" :key="`row3-${i}`">
        <EpicCard 
          :epic="getEpicAtPosition(2, i-1)" 
          :position="`2,${i-1}`"
          @click="selectEpic(getEpicAtPosition(2, i-1))"
        />
      </div>
    </div>

    <!-- Epic 생성 폼 -->
    <div class="mt-8 p-4 bg-gray-50 rounded-lg">
      <h3 class="text-lg font-semibold mb-4">새 Epic 생성</h3>
      <EpicForm @epic-created="loadEpics" />
    </div>

    <!-- 선택된 Epic 상세 정보 -->
    <div v-if="selectedEpic" class="mt-6 p-4 bg-blue-50 rounded-lg">
      <h3 class="text-lg font-semibold mb-2">선택된 Epic 상세</h3>
      <div class="text-sm">
        <p><strong>제목:</strong> {{ selectedEpic.title }}</p>
        <p><strong>설명:</strong> {{ selectedEpic.description }}</p>
        <p><strong>상태:</strong> {{ selectedEpic.status }}</p>
        <p><strong>깊이:</strong> {{ selectedEpic.depth }}</p>
        <p><strong>하위 Epic 수:</strong> {{ selectedEpic.subs?.length || 0 }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import EpicCard from './EpicCard.vue';
import EpicForm from './EpicForm.vue';
import epicService, { type Epic } from '../services/epicService';

const epics = ref<Epic[]>([]);
const selectedEpic = ref<Epic | null>(null);
const loading = ref(false);

// Epic 데이터 로드
const loadEpics = async () => {
  try {
    loading.value = true;
    epics.value = await epicService.getEpics();
  } catch (error) {
    console.error('Failed to load epics:', error);
  } finally {
    loading.value = false;
  }
};

// 특정 위치의 Epic 가져오기
const getEpicAtPosition = (row: number, col: number): Epic | null => {
  // depth 0인 core epic들을 먼저 찾기
  const coreEpics = epics.value.filter(epic => epic.depth === 0);
  
  if (coreEpics.length === 0) return null;
  
  // 중앙 (1,1)에는 첫 번째 core epic
  if (row === 1 && col === 1) {
    return coreEpics[0] || null;
  }
  
  // 다른 위치에는 해당 core epic의 subs 중에서 찾기
  const centerEpic = coreEpics[0];
  if (!centerEpic || !centerEpic.subs) return null;
  
  // 3x3 그리드에서 위치 계산
  const position = row * 3 + col;
  if (position < centerEpic.subs.length) {
    return centerEpic.subs[position];
  }
  
  return null;
};

// Epic 선택
const selectEpic = (epic: Epic | null) => {
  selectedEpic.value = epic;
};

// 컴포넌트 마운트 시 Epic 데이터 로드
onMounted(() => {
  loadEpics();
});
</script>

<style scoped>
.mandalart-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.mandalart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 16px;
  margin: 0 auto;
  max-width: 600px;
}

.mandalart-cell {
  aspect-ratio: 1;
  min-height: 120px;
}
</style>
