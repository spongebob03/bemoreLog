<template>
  <div class="three-by-three-grid" :class="gridType">
    <div 
      v-for="index in 9" 
      :key="index"
      class="grid-cell"
      :class="getCellClass(index)"
      @click="handleCellClick(index)"
    >
      <div class="cell-content">
        <EpicCard 
          v-if="getEpicAtPosition(index)"
          :epic="getEpicAtPosition(index)"
          :position="getRelativePosition(index).toString()"
          @click="handleEpicClick(getEpicAtPosition(index))"
        />
        <div v-else class="position-label">
          [{{getRelativePosition(index)}}]
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import EpicCard from './EpicCard.vue';
import type { Epic } from '../services/epicService';

interface Props {
  gridIndex: number; // 0-8 (9개 3x3 그리드 중 몇 번째인지)
  epics: Epic[];
  onCellClick: (relativePosition: string, epic: Epic | null) => void;
}

const props = defineProps<Props>();

// 3x3 그리드의 타입 결정
const gridType = computed(() => {
  if (props.gridIndex === 4) return 'center-grid'; // 중앙 그리드 (0-8에서 4번째)
  return 'surrounding-grid'; // 주변 그리드
});

// 시계방향 위치 번호 생성 (1~8, 중앙 0)
const getRelativePosition = (index: number): number => {
  // 3x3 그리드에서 시계방향으로 번호 매기기
  // 1 2 3
  // 8 0 4
  // 7 6 5
  const positionMap = {
    1: 1, 2: 2, 3: 3,
    4: 8, 5: 0, 6: 4, 
    7: 7, 8: 6, 9: 5
  };
  return positionMap[index as keyof typeof positionMap] || 0;
};

// 특정 위치의 Epic 가져오기 (상대 위치 기반)
const getEpicAtPosition = (index: number): Epic | null => {
  const relativePos = getRelativePosition(index);
  
  // 해당 3x3 그리드에 속하는 epic들 중에서 상대 위치가 일치하는 것 찾기
  return props.epics.find(epic => {
    if (epic.position !== undefined && epic.position !== null) {
      // 중앙 그리드(Grid 4)인 경우
      if (props.gridIndex === 4) {
        if (epic.depth === 0) {
          // depth=0 epic은 중앙(position=0)에만 배치
          return relativePos === 0;
        } else if (epic.depth === 1) {
          // depth=1 epic은 position에 따라 해당 위치에 배치
          return epic.position === relativePos;
        }
      } else {
        // 주변 그리드인 경우
        if (epic.depth === 1) {
          // depth=1 epic은 항상 그리드의 중앙(position=0)에 배치
          return relativePos === 0;
        }
        // 다른 depth의 epic은 position이 현재 셀의 상대 위치와 일치하는지 확인
        return epic.position === relativePos;
      }
    }
    return false;
  }) || null;
};

// 셀 클래스 결정
const getCellClass = (index: number) => {
  const classes = ['grid-cell-base'];
  
  if (props.gridIndex === 4) {
    // 중앙 3x3 그리드
    if (index === 5) {
      classes.push('center-core-cell'); // 중앙 (1,1)
    } else if (index === 1 || index === 3 || index === 7 || index === 9) {
      classes.push('center-corner-cell'); // 모서리
    } else {
      classes.push('center-edge-cell'); // 변
    }
  } else {
    // 주변 3x3 그리드
    if (index === 5) {
      classes.push('region-core-cell'); // 각 3x3의 중앙 (1,1)
    } else if (index === 1 || index === 3 || index === 7 || index === 9) {
      classes.push('region-corner-cell'); // 모서리
    } else {
      classes.push('region-edge-cell'); // 변
    }
  }
  
  return classes;
};

// 셀 클릭 핸들러
const handleCellClick = (index: number) => {
  const relativePos = getRelativePosition(index);
  const epic = getEpicAtPosition(index);
  console.log(`Grid ${props.gridIndex}, Cell ${index} -> [${relativePos}], Epic:`, epic?.title || 'None');
  props.onCellClick(relativePos.toString(), epic);
};

// Epic 클릭 핸들러
const handleEpicClick = (epic: Epic | null) => {
  if (epic) {
    console.log('Epic clicked:', epic.title);
  }
};
</script>

<style scoped>
.three-by-three-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 2px;
  background-color: #f3f4f6;
  padding: 8px;
  border-radius: 8px;
  min-height: 240px;
}

.center-grid {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border: 2px solid #f59e0b;
}

.surrounding-grid {
  background: #ffffff;
  border: 1px solid #d1d5db;
}

.grid-cell {
  aspect-ratio: 1;
  min-height: 70px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 11px;
  color: #6b7280;
}

.grid-cell-base {
  background-color: white;
  border: 1px solid #e5e7eb;
}

.grid-cell:hover {
  background-color: #f9fafb;
  transform: scale(1.02);
}

.center-core-cell {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 2px solid #f59e0b;
  font-weight: bold;
}

.center-corner-cell {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border: 1px solid #fbbf24;
}

.center-edge-cell {
  background: linear-gradient(135deg, #fefce8, #fef3c7);
  border: 1px solid #fbbf24;
}

.region-core-cell {
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border: 1px solid #0ea5e9;
  font-weight: bold;
}

.region-corner-cell {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
}

.region-edge-cell {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
}

.cell-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.position-label {
  font-size: 10px;
  color: #9ca3af;
  text-align: center;
}
</style>
