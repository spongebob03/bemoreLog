<template>
  <div class="mandalart-container">
    <div class="header">
      <h1>Mandalart Epic Manager</h1>
      <p>9x9 그리드로 epic을 관리하세요</p>
    </div>

    <div class="mandalart-grid">
      <!-- 9개의 3x3 그리드를 3x3 레이아웃으로 배치 -->
      <ThreeByThreeGrid
        v-for="gridIndex in 9"
        :key="gridIndex"
        :grid-index="gridIndex - 1"
        :epics="gridEpics[gridIndex - 1]"
        :on-cell-click="(relativePosition, epic) => handleCellClick(relativePosition, epic, gridIndex - 1)"
      />
    </div>

    <!-- Epic Modal -->
    <EpicModal 
      v-if="selectedEpic !== null || showCreateModal"
      :epic="selectedEpic"
      :is-create="showCreateModal"
      :selected-position="selectedPosition"
      :grid-index="selectedGridIndex"
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
  <button class="clear-all-btn" @click="handleClearAllEpics">
      모든 Epic 삭제
  </button>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import epicService, { type Epic } from '../services/epicService';
import EpicModal from './EpicModal.vue';
import ThreeByThreeGrid from './ThreeByThreeGrid.vue';

const epics = ref<Epic[]>([]);
const loading = ref(false);
const selectedEpic = ref<Epic | null>(null);
const showCreateModal = ref(false);
const selectedPosition = ref<{row: number, col: number} | null>(null);
const selectedGridIndex = ref<number | undefined>(undefined);

// 3x3 그리드별로 epic을 분류하는 computed 속성
const gridEpics = computed(() => {
  const grids: Epic[][] = Array(9).fill(null).map(() => []);
  
  // 중복 제거를 위해 Map 사용
  const uniqueEpics = new Map<number, Epic>();
  epics.value.forEach(epic => {
    if (!uniqueEpics.has(epic.id)) {
      uniqueEpics.set(epic.id, epic);
    }
  });
  
  // 중복 제거된 epic들을 그리드에 배치
  uniqueEpics.forEach(epic => {
    if (epic.position !== undefined && epic.position !== null) {
      let gridIndex = 0;
      
      console.log(`Processing epic: "${epic.title}" (depth: ${epic.depth}, position: ${epic.position})`);
      
      if (epic.depth === 0) {
        // depth=0 (core epic)은 중앙 3x3 그리드 (index 4)
        gridIndex = 4;
        console.log(`  → Core epic → Grid ${gridIndex}`);
        grids[gridIndex].push(epic);
      } else if (epic.depth === 1) {
        // depth=1 epic은 position에 따라 해당 3x3 그리드의 중앙에 위치
        // 시계방향 위치를 3x3 그리드 인덱스로 매핑
        switch (epic.position) {
          case 1: gridIndex = 0; break; // 좌상단 3x3
          case 2: gridIndex = 1; break; // 상단 3x3
          case 3: gridIndex = 2; break; // 우상단 3x3
          case 4: gridIndex = 5; break; // 우측 3x3
          case 5: gridIndex = 8; break; // 우하단 3x3
          case 6: gridIndex = 7; break; // 하단 3x3
          case 7: gridIndex = 6; break; // 좌하단 3x3
          case 8: gridIndex = 3; break; // 좌측 3x3
          default: gridIndex = 4; // 기본값은 중앙
        }
        
        // depth=1 epic을 해당 주변 그리드에 추가
        grids[gridIndex].push(epic);
        
        // depth=1 epic을 중앙 그리드(Grid 4)에도 추가 (하위 epic으로 표시)
        grids[4].push(epic);
        
        console.log(`Depth=1 epic "${epic.title}" (position: ${epic.position}) → Grid ${gridIndex} at center + Grid 4 as sub`);
      } else if (epic.depth === 2) {
        // depth=2 epic은 부모 epic의 위치에 따라 해당 3x3 그리드에 배치
        if (epic.core_epic_id) {
          const parentEpic = epics.value.find(e => e.id === epic.core_epic_id);
          if (parentEpic && parentEpic.position !== undefined) {
            // 부모 epic의 position에 따라 grid 결정
            switch (parentEpic.position) {
              case 1: gridIndex = 0; break;
              case 2: gridIndex = 1; break;
              case 3: gridIndex = 2; break;
              case 4: gridIndex = 5; break;
              case 5: gridIndex = 8; break;
              case 6: gridIndex = 7; break;
              case 7: gridIndex = 6; break;
              case 8: gridIndex = 3; break;
              default: gridIndex = 4;
            }
            
            // depth=2 epic을 해당 그리드에 추가
            grids[gridIndex].push(epic);
            
            console.log(`Depth=2 epic "${epic.title}" (parent position: ${parentEpic.position}) → Grid ${gridIndex}`);
          }
        }
      }
    }
  });
  
  // 각 그리드의 epic 분포를 상세히 로그로 출력
  console.log('=== Grid Epics Distribution ===');
  grids.forEach((grid, i) => {
    if (grid.length > 0) {
      console.log(`Grid ${i}: ${grid.map(e => `${e.title}(depth:${e.depth}, pos:${e.position})`).join(', ')}`);
    }
  });
  console.log('===============================');
  
  return grids;
});

// Epic 데이터 로드
const loadEpics = async () => {
  try {
    loading.value = true;
    const loadedEpics = await epicService.getEpics();
    epics.value = loadedEpics;
    console.log('Loaded epics:', loadedEpics);
    
    // 각 epic의 position 정보를 상세히 로그로 출력
    loadedEpics.forEach(epic => {
      if (epic.position) {
        console.log(`Epic: ${epic.title} (depth: ${epic.depth}) at position: ${epic.position}`);
      }
    });
  } catch (error) {
    console.error('Failed to load epics:', error);
  } finally {
    loading.value = false;
  }
};

// 셀 클릭 핸들러
const handleCellClick = (relativePosition: string, epic: Epic | null, gridIndex?: number) => {
  console.log(`Cell clicked at relative position [${relativePosition}], epic:`, epic, `gridIndex:`, gridIndex);
  
  if (epic) {
    // 기존 epic 클릭 - 수정 모드
    selectedEpic.value = epic;
    showCreateModal.value = false;
  } else {
    // 빈 셀 클릭 - 생성 모드
    selectedEpic.value = null;
    showCreateModal.value = true;
    
    // gridIndex 정보가 있으면 더 정확한 위치 계산
    if (gridIndex !== undefined) {
      // 전체 9x9 그리드에서의 절대 위치 계산
      const gridRow = Math.floor(gridIndex / 3);
      const gridCol = gridIndex % 3;
      
      // 시계방향 위치 번호를 그리드 내 상대 위치로 변환
      const positionNumber = parseInt(relativePosition);
      let relativeRow = 0, relativeCol = 0;
      
      // 시계방향 번호를 상대 x,y 좌표로 변환
      switch (positionNumber) {
        case 1: relativeRow = 0; relativeCol = 0; break; // 좌상단
        case 2: relativeRow = 0; relativeCol = 1; break; // 상단
        case 3: relativeRow = 0; relativeCol = 2; break; // 우상단
        case 4: relativeRow = 1; relativeCol = 2; break; // 우측
        case 5: relativeRow = 2; relativeCol = 2; break; // 우하단
        case 6: relativeRow = 2; relativeCol = 1; break; // 하단
        case 7: relativeRow = 2; relativeCol = 0; break; // 좌하단
        case 8: relativeRow = 1; relativeCol = 0; break; // 좌측
        case 0: relativeRow = 1; relativeCol = 1; break; // 중앙
        default: relativeRow = 0; relativeCol = 0;
      }
      
      // 전체 9x9 그리드에서의 절대 위치
      const absoluteRow = gridRow * 3 + relativeRow;
      const absoluteCol = gridCol * 3 + relativeCol;
      
      console.log(`Grid ${gridIndex} (${gridRow}, ${gridCol}) -> Relative [${relativeRow}, ${relativeCol}] -> Absolute [${absoluteRow}, ${absoluteCol}]`);
      
      // 3x3 그리드 내 상대 위치로 전달 (EpicForm에서 사용)
      selectedPosition.value = { row: relativeRow, col: relativeCol };
      selectedGridIndex.value = gridIndex;
    } else {
      // 기존 방식 (하위 호환성)
      const positionNumber = parseInt(relativePosition);
      let row = 0, col = 0;
      
      switch (positionNumber) {
        case 1: row = 0; col = 0; break;
        case 2: row = 0; col = 1; break;
        case 3: row = 0; col = 2; break;
        case 4: row = 1; col = 2; break;
        case 5: row = 2; col = 2; break;
        case 6: row = 2; col = 1; break;
        case 7: row = 2; col = 0; break;
        case 8: row = 1; col = 0; break;
        case 0: row = 1; col = 1; break;
        default: row = 0; col = 0;
      }
      
      selectedPosition.value = { row, col };
    }
  }
};

// 모달 닫기
const closeModal = () => {
  selectedEpic.value = null;
  showCreateModal.value = false;
  selectedPosition.value = null;
  selectedGridIndex.value = undefined;
};

// Epic 생성 완료
const handleEpicCreated = async () => {
  console.log('Epic created');
  await loadEpics(); // epic 목록 새로고침
  closeModal();
};

// Epic 수정 완료
const handleEpicUpdated = async () => {
  console.log('Epic updated');
  await loadEpics(); // epic 목록 새로고침
  closeModal();
};

// Epic 삭제 완료
const handleEpicDeleted = async () => {
  console.log('Epic deleted');
  await loadEpics(); // epic 목록 새로고침
  closeModal();
};

// 모든 Epic 삭제
const handleClearAllEpics = async () => {
  if (confirm('정말로 모든 Epic을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
    try {
      await epicService.deleteAllEpics();
      console.log('All epics deleted successfully');
      await loadEpics(); // epic 목록 새로고침
      alert('모든 Epic이 삭제되었습니다.');
    } catch (error) {
      console.error('Failed to delete all epics:', error);
      alert('Epic 삭제에 실패했습니다.');
    }
  }
};

// 컴포넌트 마운트 시 Epic 데이터 로드
onMounted(() => {
  loadEpics();
});
</script>

<style scoped>
.mandalart-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
  text-align: center;
}

.header h1 {
  color: #1f2937;
  margin-bottom: 8px;
}

.header p {
  color: #6b7280;
  font-size: 16px;
}

.header-actions {
  margin-top: 16px;
}

.clear-all-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.clear-all-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.mandalart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 16px;
  margin: 0 auto;
  max-width: 1200px;
  background-color: #f8fafc;
  padding: 20px;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
}

.fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  z-index: 1000;
}

.fab:hover {
  background: #059669;
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.fab-icon {
  color: white;
  font-size: 24px;
  font-weight: bold;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .mandalart-grid {
    gap: 12px;
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .mandalart-grid {
    gap: 8px;
    padding: 12px;
  }
  
  .mandalart-container {
    padding: 16px;
  }
}
</style>