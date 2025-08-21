#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
기존 position 컬럼의 데이터 형식을 (x, y) 형태로 업데이트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.db.session import SQLALCHEMY_DATABASE_URL

def update_position_format():
    """기존 position 컬럼의 데이터 형식을 (x, y) 형태로 업데이트"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # depth 0: 중앙 (4, 4)
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
            print("✅ 기존 epic들의 position 형식이 (x, y) 형태로 업데이트되었습니다.")
            
        except Exception as e:
            print(f"❌ 마이그레이션 중 오류 발생: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("🚀 position 형식 업데이트 마이그레이션을 시작합니다...")
    update_position_format()
    print("🎉 마이그레이션이 완료되었습니다.")
