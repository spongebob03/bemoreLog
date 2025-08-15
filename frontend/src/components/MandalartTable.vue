<template>
  <div class="mandalart-container">
    <div class="header">
      <h2 class="text-2xl font-bold text-center mb-6">만다라트 목표 관리</h2>
      

    </div>
    
    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Epic 로딩 중...</div>
    </div>

    <!-- 9x9 만다라트 테이블 -->
    <div class="mandalart-grid">
      <div 
        class="mandalart-cell" 
        v-for="index in 81" 
        :key="`cell-${index}`"
        :class="getCellClass(Math.floor((index-1)/9), (index-1)%9)"
      >
        <div class="cell-content">
          <EpicCard 
            v-if="getEpicAtPosition(Math.floor((index-1)/9), (index-1)%9)"
            :epic="getEpicAtPosition(Math.floor((index-1)/9), (index-1)%9)"
            :position="`${Math.floor((index-1)/9)},${(index-1)%9}`"
            @click="selectEpic(getEpicAtPosition(Math.floor((index-1)/9), (index-1)%9), Math.floor((index-1)/9), (index-1)%9)"
          />
          <div 
            v-else 
            class="position-label clickable-empty"
            @click="selectEpic(null, Math.floor((index-1)/9), (index-1)%9)"
          >
            [{{Math.floor((index-1)/9)}},{{(index-1)%9}}]
          </div>
        </div>
      </div>
      
      <!-- 3x3 영역 구분선 -->
      <div class="region-divider region-divider-horizontal region-divider-1"></div>
      <div class="region-divider region-divider-horizontal region-divider-2"></div>
      <div class="region-divider region-divider-vertical region-divider-3"></div>
      <div class="region-divider region-divider-vertical region-divider-4"></div>
    </div>

    <!-- Epic Modal -->
    <EpicModal 
      v-if="selectedEpic !== null || showCreateModal"
      :epic="selectedEpic"
      :is-create="showCreateModal"
      :selected-position="selectedPosition"
      @close="closeModal"
      @saved="handleEpicUpdated"
      @epic-created="handleEpicCreated"
      @epic-updated="handleEpicUpdated"
      @epic-deleted="handleEpicDeleted"
    />

    <!-- Floating Action Button -->
    <div class="fab" @click="showCreateModal = true">
      <span class="fab-icon">+</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import epicService, { type Epic } from '../services/epicService';
import EpicCard from './EpicCard.vue';
import EpicModal from './EpicModal.vue';

const epics = ref<Epic[]>([]);
const loading = ref(false);
const selectedEpic = ref<Epic | null>(null);
const showCreateModal = ref(false);
const selectedPosition = ref<{row: number, col: number} | null>(null);

// Epic 데이터 로드
const loadEpics = async () => {
  try {
    loading.value = true;
    const loadedEpics = await epicService.getEpics();
    epics.value = loadedEpics;
    console.log('Loaded epics:', loadedEpics);
  } catch (error) {
    console.error('Failed to load epics:', error);
  } finally {
    loading.value = false;
  }
};

// 특정 위치의 Epic 가져오기 (9x9 그리드)
const getEpicAtPosition = (row: number, col: number): Epic | null => {
  // 중앙 [4,4]에는 depth=0 epic (core epic)
  if (row === 4 && col === 4) {
    const coreEpic = epics.value.find(epic => epic.depth === 0);
    if (coreEpic) {
      console.log(`Position [${row}][${col}] - Core Epic:`, coreEpic.title);
      return coreEpic;
    }
    return null;
  }
  
  // 중앙 3x3 영역 (3,3) ~ (5,5)에도 depth=1 epic들을 배치
  if (row >= 3 && row <= 5 && col >= 3 && col <= 5) {
    // 중앙 (4,4)는 제외
    if (!(row === 4 && col === 4)) {
      // depth=1인 epic들을 찾아서 각 3x3 영역의 위치에 따라 배치
      const depth1Epics = epics.value.filter(epic => epic.depth === 1);
      
      // 중앙 3x3 영역에서의 상대적 위치 계산 (0~7)
      const centerRelativeIndex = (row - 3) * 3 + (col - 3);
      if (centerRelativeIndex === 4) return null; // 중앙 제외
      
      // 주변 8개 위치와 매핑
      const surroundingPositions = [
        [1, 1], [1, 4], [1, 7],
        [4, 1], [4, 7],
        [7, 1], [7, 4], [7, 7]
      ];
      
      // 해당 위치에 맞는 depth=1 epic 찾기
      const adjustedIndex = centerRelativeIndex > 4 ? centerRelativeIndex - 1 : centerRelativeIndex;
      if (adjustedIndex < depth1Epics.length) {
        const epic = depth1Epics[adjustedIndex];
        
        // epic의 position 값을 확인하여 해당 3x3 영역의 위치에 맞게 배치
        if (epic.position) {
          const match = epic.position.match(/(\d+)\s*,\s*(\d+)/);
          if (match) {
            const epicRow = parseInt(match[1]);
            const epicCol = parseInt(match[2]);
            
            // epic이 속한 3x3 영역 계산
            const regionRow = Math.floor(epicRow / 3);
            const regionCol = Math.floor(epicCol / 3);
            
            // epic이 속한 3x3 영역의 중앙 위치 계산
            const regionCenterRow = regionRow * 3 + 1;
            const regionCenterCol = regionCol * 3 + 1;
            
            // epic이 해당 3x3 영역의 중앙에 있는지 확인
            if (epicRow === regionCenterRow && epicCol === regionCenterCol) {
              console.log(`Position [${row}][${col}] - Depth 1 Epic (${epic.title}) from region [${regionRow}][${regionCol}] in center 3x3`);
              return epic;
            }
          }
        }
      }
    }
  }
  
  // 주변 8개 위치에도 depth=1 epic들을 배치
  const surroundingPositions = [
    [1, 1], [1, 4], [1, 7],
    [4, 1], [4, 7],
    [7, 1], [7, 4], [7, 7]
  ];
  
  const isSurrounding = surroundingPositions.some(([r, c]) => r === row && c === col);
  if (isSurrounding) {
    // depth=1인 epic들을 찾아서 각 3x3 영역의 위치에 따라 배치
    const depth1Epics = epics.value.filter(epic => epic.depth === 1);
    
    // 해당 위치에 맞는 depth=1 epic 찾기
    const positionIndex = surroundingPositions.findIndex(([r, c]) => r === row && c === col);
    if (positionIndex < depth1Epics.length) {
      const epic = depth1Epics[positionIndex];
      
      // epic의 position 값을 확인하여 해당 3x3 영역의 위치에 맞게 배치
      if (epic.position) {
        const match = epic.position.match(/(\d+)\s*,\s*(\d+)/);
        if (match) {
          const epicRow = parseInt(match[1]);
          const epicCol = parseInt(match[2]);
          
          // epic이 속한 3x3 영역 계산
          const regionRow = Math.floor(epicRow / 3);
          const regionCol = Math.floor(epicCol / 3);
          
          // epic이 속한 3x3 영역의 중앙 위치 계산
          const regionCenterRow = regionRow * 3 + 1;
          const regionCenterCol = regionCol * 3 + 1;
          
          // epic이 해당 3x3 영역의 중앙에 있는지 확인
          if (epicRow === regionCenterRow && epicCol === regionCenterCol) {
            console.log(`Position [${row}][${col}] - Depth 1 Epic (${epic.title}) from region [${regionRow}][${regionCol}] in surrounding`);
            return epic;
          }
        }
      }
    }
  }
  
  // depth=1 epic에 포함된 subs들도 position 값 참조해서 배치
  const depth1Epics = epics.value.filter(epic => epic.depth === 1);
  for (const depth1Epic of depth1Epics) {
    if (depth1Epic.subs && depth1Epic.subs.length > 0) {
      // depth=1 epic의 subs들 중에서 해당 위치에 맞는 epic 찾기
      for (const subEpic of depth1Epic.subs) {
        if (subEpic.position) {
          const match = subEpic.position.match(/(\d+)\s*,\s*(\d+)/);
          if (match) {
            const subEpicRow = parseInt(match[1]);
            const subEpicCol = parseInt(match[2]);
            
            // 현재 위치와 일치하는지 확인
            if (subEpicRow === row && subEpicCol === col) {
              console.log(`Position [${row}][${col}] - Depth 2 Epic (${subEpic.title}) from parent (${depth1Epic.title})`);
              return subEpic;
            }
          }
        }
      }
    }
  }
  
  return null;
};

// 셀 클래스 결정 (중앙, 모서리, 변 등)
const getCellClass = (row: number, col: number) => {
  const classes = ['mandalart-cell-base'];
  
  // 중앙 3x3 영역 (3,3) ~ (5,5) - 주요 epic 구간
  if (row >= 3 && row <= 5 && col >= 3 && col <= 5) {
    classes.push('center-region');
    
    // 중앙 3x3 내부의 중앙 칸 (4,4) - 핵심
    if (row === 4 && col === 4) {
      classes.push('core-cell');
    }
    // 중앙 3x3 내부의 모서리 칸들
    else if ((row === 3 || row === 5) && (col === 3 || col === 5)) {
      classes.push('center-corner-cell');
    }
    // 중앙 3x3 내부의 변 칸들
    else {
      classes.push('center-edge-cell');
    }
  }
  // 주변 3x3 영역들
  else {
    // 각 3x3 영역의 중앙 칸 - 핵심
    const regionCenterRow = Math.floor(row / 3) * 3 + 1;
    const regionCenterCol = Math.floor(col / 3) * 3 + 1;
    
    if (row === regionCenterRow && col === regionCenterCol) {
      classes.push('region-core-cell');
    }
    // 각 3x3 영역의 모서리 칸들
    else if ((row % 3 === 0 || row % 3 === 2) && (col % 3 === 0 || col % 3 === 2)) {
      classes.push('region-corner-cell');
    }
    // 각 3x3 영역의 변 칸들
    else {
      classes.push('region-edge-cell');
    }
  }
  
  return classes.join(' ');
};

// Epic 선택
const selectEpic = (epic: Epic | null, row: number, col: number) => {
  if (epic) {
    // 기존 epic 클릭 - 상세 보기 모드
    selectedEpic.value = epic;
    showCreateModal.value = false;
  } else {
    // 빈 셀 클릭 - 새 epic 생성 모드
    selectedEpic.value = null;
    showCreateModal.value = true;
  }
  selectedPosition.value = { row, col };
  console.log(`Selected position [${row}][${col}], Epic:`, epic);
};

// 모달 닫기
const closeModal = () => {
  selectedEpic.value = null;
  showCreateModal.value = false;
  selectedPosition.value = null;
};

// Epic 생성 완료
const handleEpicCreated = async (newEpic: Epic) => {
  console.log('Epic created:', newEpic);
  await loadEpics(); // epic 목록 새로고침
  closeModal();
};

// Epic 수정 완료
const handleEpicUpdated = async (updatedEpic: Epic) => {
  console.log('Epic updated:', updatedEpic);
  await loadEpics(); // epic 목록 새로고침
  closeModal();
};

// Epic 삭제 완료
const handleEpicDeleted = async () => {
  console.log('Epic deleted');
  await loadEpics(); // epic 목록 새로고침
  closeModal();
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

.header {
  margin-bottom: 30px;
}

.navigation {
  text-align: center;
  margin-bottom: 20px;
}

.nav-link {
  display: inline-block;
  padding: 10px 20px;
  background: #10b981;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background: #059669;
}

.mandalart-grid {
  display: grid;
  grid-template-columns: repeat(9, 1fr);
  grid-template-rows: repeat(9, 1fr);
  gap: 2px;
  margin: 0 auto;
  max-width: 900px;
  background-color: #e5e7eb;
  padding: 12px;
  border-radius: 12px;
  position: relative;
}

.mandalart-cell {
  aspect-ratio: 1;
  min-height: 80px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mandalart-cell-base {
  background-color: white;
  border: 1px solid #d1d5db;
}

/* 중앙 3x3 영역 - 주요 epic 구간 */
.center-region {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border: 2px solid #fbbf24;
}

.core-cell {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  border: 3px solid #3b82f6;
  color: #1e40af;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.center-corner-cell {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 2px solid #fbbf24;
  color: #92400e;
}

.center-edge-cell {
  background: linear-gradient(135deg, #fef9c3, #fef3c7);
  border: 2px solid #fbbf24;
  color: #92400e;
}

/* 주변 3x3 영역들 */
.region-core-cell {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  border: 2px solid #10b981;
  color: #047857;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
}

.region-corner-cell {
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border: 2px solid #d1d5db;
  color: #6b7280;
}

.region-edge-cell {
  background: linear-gradient(135deg, #f9fafb, #f3f4f6);
  border: 2px solid #d1d5db;
  color: #6b7280;
}

.mandalart-cell:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 5;
}

.cell-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.position-label {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #374151;
  font-size: 10px;
  margin-bottom: 4px;
}

.clickable-empty {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 4px;
  padding: 4px;
}

.clickable-empty:hover {
  background-color: #f3f4f6;
  color: #1f2937;
  transform: scale(1.05);
}

.epic-info {
  text-align: center;
  margin-top: 4px;
}

.epic-title {
  font-size: 11px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
  line-height: 1.2;
  word-break: break-word;
}

.epic-depth {
  font-size: 9px;
  color: #6b7280;
  font-weight: 500;
}

/* 3x3 영역 구분선 */
.region-divider {
  position: absolute;
  background: #d1d5db;
  z-index: 10;
}

.region-divider-horizontal {
  width: 100%;
  height: 4px;
  left: 0;
}

.region-divider-vertical {
  height: 100%;
  width: 4px;
  top: 0;
}

.region-divider-1 {
  top: 33.33%;
}

.region-divider-2 {
  top: 66.66%;
}

.region-divider-3 {
  left: 33.33%;
}

.region-divider-4 {
  left: 66.66%;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-size: 18px;
  color: #3b82f6;
}

/* Floating Action Button */
.fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
  z-index: 1000;
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.fab-icon {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

</style>
