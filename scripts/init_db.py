import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.db import create_tables

if __name__ == '__main__':
    create_tables()
    print('DB 테이블 생성 완료')
