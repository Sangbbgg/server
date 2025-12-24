import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json
import re


class FileProcessor:
    """파일 타입별 처리 클래스"""
    
    @staticmethod
    def process_txt_performance(file_path: str) -> List[Dict]:
        """
        Case 1: 성능 데이터 (.txt in disk,task)
        Key: Value 형태 파싱
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    
                    # Key: Value 추출
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        results.append({
                            'item_name': key,
                            'value': value,
                            'raw_data': None
                        })
        except Exception as e:
            print(f"Error processing performance file {file_path}: {e}")
        
        return results
    
    @staticmethod
    def process_txt_process(file_path: str) -> List[Dict]:
        """
        Case 2: 프로세스 현황 데이터 (.txt in log,process)
        전체 텍스트를 raw_data에 저장
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return [{
                'item_name': 'Process List',
                'value': str(len(content.splitlines())),  # 라인 수
                'raw_data': content
            }]
        except Exception as e:
            print(f"Error processing process file {file_path}: {e}")
            return []
    
    @staticmethod
    def process_evtx(file_path: str) -> List[Dict]:
        """
        Case 3: EVTX 로그 파일 처리
        python-evtx를 사용하여 파싱
        """
        try:
            from Evtx.Evtx import Evtx
            from Evtx.Views import evtx_file_xml_view
            
            event_stats = {
                'level_1': {},  # Critical
                'level_2': {},  # Error
                'level_3': {}   # Warning
            }
            
            total_count = 0
            
            with Evtx(file_path) as evtx:
                for record_xml, record in evtx_file_xml_view(evtx.get_file_header()):
                    # XML 파싱하여 Level과 EventID 추출
                    level, event_id = FileProcessor._parse_evtx_record(record_xml)
                    
                    if level in [1, 2, 3]:
                        level_key = f'level_{level}'
                        event_key = f'EventID_{event_id}'
                        
                        if event_key not in event_stats[level_key]:
                            event_stats[level_key][event_key] = 0
                        event_stats[level_key][event_key] += 1
                        total_count += 1
            
            # 파일 타입 추출 (sys, app, sec 등)
            file_type = Path(file_path).stem.lower()
            if 'sys' in file_type:
                file_type = 'sys'
            elif 'app' in file_type:
                file_type = 'app'
            elif 'sec' in file_type:
                file_type = 'sec'
            else:
                file_type = 'unknown'
            
            return [{
                'item_name': f'{file_type} Event Stats',
                'value': str(total_count),
                'raw_data': event_stats
            }]
        except ImportError:
            print("python-evtx library not available. Install it for EVTX parsing.")
            return []
        except Exception as e:
            print(f"Error processing EVTX file {file_path}: {e}")
            return []
    
    @staticmethod
    def _parse_evtx_record(record_xml: str) -> tuple:
        """EVTX 레코드 XML에서 Level과 EventID 추출"""
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(record_xml)
            ns = {'evt': 'http://schemas.microsoft.com/win/2004/08/events/event'}
            
            # System 섹션에서 Level과 EventID 추출
            system = root.find('.//evt:System', ns)
            if system is not None:
                level_elem = system.find('evt:Level', ns)
                event_id_elem = system.find('evt:EventID', ns)
                
                level = int(level_elem.text) if level_elem is not None and level_elem.text else 0
                event_id = int(event_id_elem.text) if event_id_elem is not None and event_id_elem.text else 0
                
                return level, event_id
        except Exception as e:
            print(f"Error parsing EVTX record: {e}")
        
        return 0, 0

