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

    <!-- 생성 FAB -->
    <button class="fab" @click="openCreateModal" aria-label="새 Epic 생성">＋</button>

    <!-- 모달 -->
    <EpicModal 
      v-if="isModalOpen"
      :mode="modalMode"
      :epic="currentEpic"
      @close="closeModal"
      @saved="handleSaved"
      @start-edit="switchToEdit"
      :default-core-epic-id="modalMode === 'create' ? centerCoreEpicId : null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import EpicCard from './EpicCard.vue';
import EpicModal from './EpicModal.vue';
import epicService, { type Epic } from '../services/epicService';

const epics = ref<Epic[]>([]);
const loading = ref(false);
const isModalOpen = ref(false);
const modalMode = ref<'view' | 'create' | 'edit'>('view');
const currentEpic = ref<Epic | null>(null);
const centerCoreEpicId = ref<number | null>(null);

// Epic 데이터 로드
const loadEpics = async () => {
  try {
    loading.value = true;
    const loadedEpics = await epicService.getEpics();
    epics.value = loadedEpics;
    console.log('Loaded epics:', loadedEpics);
    console.log('Core epics:', loadedEpics.filter(epic => epic.depth === 0));

    // 현재 화면의 중앙 Core Epic ID 계산: 임시로 depth 0 중 첫 번째 사용
    const core = loadedEpics.find(e => e.depth === 0) || null;
    centerCoreEpicId.value = core ? core.id : null;
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
  
  // 3x3 그리드에서 위치 계산 (중앙 제외)
  const position = row * 3 + col;
  if (position === 4) return null; // 중앙 제외
  
  // subs 배열에서 해당 위치의 epic 찾기
  const subIndex = position > 4 ? position - 1 : position; // 중앙을 제외한 인덱스
  if (subIndex < centerEpic.subs.length) {
    const epic = centerEpic.subs[subIndex];
    console.log(`Position (${row},${col}):`, epic);
    return epic;
  }
  
  console.log(`Position (${row},${col}): No epic found, subIndex: ${subIndex}, total subs: ${centerEpic.subs.length}`);
  return null;
};

const getCenterEpic = (): Epic | null => getEpicAtPosition(1, 1);

// Epic 선택: 뷰 모달 열기
const selectEpic = (epic: Epic | null) => {
  currentEpic.value = epic;
  if (epic) {
    modalMode.value = 'view';
  } else {
    // 빈셀 클릭 시 현재 중앙 epic을 core로 설정
    centerCoreEpicId.value = getCenterEpic()?.id ?? null;
    modalMode.value = 'create';
  }
  isModalOpen.value = true;
};

// 생성 모달 열기
const openCreateModal = () => {
  currentEpic.value = null;
  // FAB로 생성 시에도 현재 중앙 epic을 core로 설정
  centerCoreEpicId.value = getCenterEpic()?.id ?? null;
  modalMode.value = 'create';
  isModalOpen.value = true;
};

// 모달 닫기
const closeModal = () => {
  isModalOpen.value = false;
};

// 저장 후 처리
const handleSaved = async () => {
  try {
    await loadEpics();
    // 데이터 로드 완료 후 모달 닫기
    setTimeout(() => {
      isModalOpen.value = false;
    }, 100);
  } catch (error) {
    console.error('Failed to reload epics:', error);
  }
};

// 보기에서 수정으로 전환
const switchToEdit = () => {
  modalMode.value = 'edit';
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

.fab {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 56px;
  height: 56px;
  border-radius: 9999px;
  background: #3b82f6;
  color: #fff;
  font-size: 28px;
  border: none;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
  cursor: pointer;
}

.fab:hover {
  background: #2563eb;
}
</style>
