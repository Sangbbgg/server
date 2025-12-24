import zipfile
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import re


class ZipParser:
    """ZIP 파일 구조 파싱 클래스"""
    
    def __init__(self, zip_path: str):
        self.zip_path = zip_path
        self.work_type_pattern = re.compile(r'^(disk,task|log,process)$')
        self.date_pattern = re.compile(r'^(\d{6})_')
    
    def parse(self) -> List[Dict]:
        """
        ZIP 파일을 파싱하여 구조화된 데이터 반환
        
        Returns:
            List[Dict]: 파싱된 파일 정보 리스트
            [
                {
                    'work_type': 'disk,task' | 'log,process',
                    'system_group': '1단계_ECMS',
                    'asset_name': '1BL_ECMS_EWS1',
                    'date': '251209',
                    'filename': 'cpu.txt',
                    'file_path': 'disk,task/1단계_ECMS/1BL_ECMS_EWS1/251209_cpu.txt',
                    'extension': 'txt'
                },
                ...
            ]
        """
        results = []
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for file_info in zip_ref.namelist():
                # 디렉토리는 제외
                if file_info.endswith('/'):
                    continue
                
                parsed = self._parse_file_path(file_info)
                if parsed:
                    results.append(parsed)
        
        return results
    
    def _parse_file_path(self, file_path: str) -> Optional[Dict]:
        """개별 파일 경로 파싱"""
        parts = file_path.split('/')
        
        if len(parts) < 4:
            return None
        
        # Step 1: 작업 유형 식별
        work_type = parts[0]
        if not self.work_type_pattern.match(work_type):
            return None
        
        # Step 2: 설비군 및 자산명 추출
        system_group = parts[1]
        asset_name = parts[2]
        
        # Step 3: 파일명에서 날짜 추출
        filename = parts[-1]
        date_match = self.date_pattern.match(filename)
        if not date_match:
            return None
        
        date_str = date_match.group(1)
        actual_filename = filename[len(date_str) + 1:]  # 날짜_ 제거
        extension = Path(filename).suffix[1:] if Path(filename).suffix else ''
        
        return {
            'work_type': work_type,
            'system_group': system_group,
            'asset_name': asset_name,
            'date': date_str,
            'filename': actual_filename,
            'file_path': file_path,
            'extension': extension.lower()
        }
    
    def extract_file(self, file_path: str, extract_to: str) -> str:
        """ZIP에서 특정 파일 추출"""
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extract(file_path, extract_to)
            return os.path.join(extract_to, file_path)
    
    def extract_all(self, extract_to: str) -> str:
        """ZIP 전체 추출"""
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return extract_to

