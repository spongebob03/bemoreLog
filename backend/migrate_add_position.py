#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
epics 테이블에 position 컬럼 추가
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.db.session import SQLALCHEMY_DATABASE_URL

def migrate_add_position():
    """epics 테이블에 position 컬럼 추가"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # position 컬럼 추가
            conn.execute(text("ALTER TABLE epics ADD COLUMN position VARCHAR"))
            conn.commit()
            print("✅ position 컬럼이 성공적으로 추가되었습니다.")
            
            # 기존 epic들의 position 설정 (depth에 따라)
            # depth 0: 중앙 [4,4]
            conn.execute(text("UPDATE epics SET position = '(4, 4)' WHERE depth = 0"))
            
            # depth 1: 주변 8개 위치
            conn.execute(text("""
                UPDATE epics 
                SET position = CASE 
                    WHEN id % 8 = 0 THEN '(1, 1)'
                    WHEN id % 8 = 1 THEN '(1, 4)'
                    WHEN id % 8 = 2 THEN '(1, 7)'
                    WHEN id % 8 = 3 THEN '(4, 1)'
                    WHEN id % 8 = 4 THEN '(4, 7)'
                    WHEN id % 8 = 5 THEN '(7, 1)'
                    WHEN id % 8 = 6 THEN '(7, 4)'
                    WHEN id % 8 = 7 THEN '(7, 7)'
                END
                WHERE depth = 1
            """))
            
            conn.commit()
            print("✅ 기존 epic들의 position이 설정되었습니다.")
            
        except Exception as e:
            print(f"❌ 마이그레이션 중 오류 발생: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("🚀 position 컬럼 추가 마이그레이션을 시작합니다...")
    migrate_add_position()
    print("🎉 마이그레이션이 완료되었습니다.")
