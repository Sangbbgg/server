import os
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Asset, MaintenanceLog, MaintenanceDetail, LogFile
from app.models.maintenance import CheckType, ResultStatus
from app.services.zip_parser import ZipParser
from app.services.file_processor import FileProcessor
from app.core.config import settings


class UploadService:
    """ZIP 업로드 및 데이터 처리 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.zip_parser = None
        self.file_processor = FileProcessor()
    
    def process_upload(self, zip_path: str, worker: str = None) -> Dict:
        """
        ZIP 파일 업로드 및 처리
        
        Args:
            zip_path: 업로드된 ZIP 파일 경로
            worker: 작업자명 (선택)
        
        Returns:
            Dict: 처리 결과 통계
        """
        self.zip_parser = ZipParser(zip_path)
        parsed_files = self.zip_parser.parse()
        
        # 임시 추출 디렉토리
        extract_dir = os.path.join(settings.UPLOAD_DIR, f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(extract_dir, exist_ok=True)
        
        stats = {
            'total_files': len(parsed_files),
            'processed': 0,
            'errors': 0,
            'assets_found': 0,
            'assets_created': 0,
            'logs_created': 0
        }
        
        try:
            # 파일별 처리
            for file_info in parsed_files:
                try:
                    self._process_file(file_info, extract_dir, worker)
                    stats['processed'] += 1
                except Exception as e:
                    print(f"Error processing file {file_info['file_path']}: {e}")
                    stats['errors'] += 1
        
        finally:
            # 임시 디렉토리 정리
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
        
        return stats
    
    def _process_file(self, file_info: Dict, extract_dir: str, worker: str = None):
        """개별 파일 처리"""
        # Step 1: 자산 찾기 또는 생성
        asset = self.db.query(Asset).filter(Asset.name == file_info['asset_name']).first()
        
        if not asset:
            # 자산이 없으면 생성 (기본값)
            from app.models.asset import AssetStatus
            asset = Asset(
                name=file_info['asset_name'],
                status=AssetStatus.OPERATIONAL
            )
            self.db.add(asset)
            self.db.flush()
        
        # Step 2: 날짜 파싱
        date_str = file_info['date']
        check_date = datetime.strptime(f"20{date_str}", "%Y%m%d").date()
        
        # Step 3: 점검 유형 결정
        if file_info['work_type'] == 'disk,task':
            check_type = CheckType.DISK
        elif file_info['work_type'] == 'log,process':
            check_type = CheckType.PROCESS if file_info['extension'] == 'txt' else CheckType.LOG
        else:
            check_type = CheckType.OTHER
        
        # Step 4: MaintenanceLog 생성 또는 찾기
        log = self.db.query(MaintenanceLog).filter(
            MaintenanceLog.asset_id == asset.id,
            MaintenanceLog.check_date == check_date,
            MaintenanceLog.check_type == check_type
        ).first()
        
        if not log:
            log = MaintenanceLog(
                asset_id=asset.id,
                check_date=check_date,
                check_type=check_type,
                worker=worker,
                result_status=ResultStatus.PASS
            )
            self.db.add(log)
            self.db.flush()
        
        # Step 5: 파일 추출 및 처리
        extracted_path = self.zip_parser.extract_file(file_info['file_path'], extract_dir)
        
        # 파일 타입별 처리
        if file_info['extension'] == 'txt':
            if file_info['work_type'] == 'disk,task':
                details = self.file_processor.process_txt_performance(extracted_path)
            else:
                details = self.file_processor.process_txt_process(extracted_path)
        elif file_info['extension'] == 'evtx':
            details = self.file_processor.process_evtx(extracted_path)
            
            # Level 1 이벤트가 있으면 Fail 처리
            if details and details[0].get('raw_data'):
                event_stats = details[0]['raw_data']
                if event_stats.get('level_1') and sum(event_stats['level_1'].values()) > 0:
                    log.result_status = ResultStatus.FAIL
            
            # EVTX 파일은 아카이브로 이동
            archive_path = self._archive_file(extracted_path, file_info)
            log_file = LogFile(
                log_id=log.id,
                file_path=archive_path,
                file_type='evtx'
            )
            self.db.add(log_file)
        else:
            details = []
        
        # Step 6: MaintenanceDetail 저장
        for detail_data in details:
            detail = MaintenanceDetail(
                log_id=log.id,
                item_name=detail_data['item_name'],
                value=detail_data.get('value'),
                raw_data=detail_data.get('raw_data')
            )
            self.db.add(detail)
        
        self.db.commit()
    
    def _archive_file(self, file_path: str, file_info: Dict) -> str:
        """파일을 아카이브 디렉토리로 이동"""
        os.makedirs(settings.ARCHIVE_DIR, exist_ok=True)
        
        # 아카이브 경로: archive/asset_name/date_filename
        archive_subdir = os.path.join(settings.ARCHIVE_DIR, file_info['asset_name'])
        os.makedirs(archive_subdir, exist_ok=True)
        
        archive_filename = f"{file_info['date']}_{file_info['filename']}"
        archive_path = os.path.join(archive_subdir, archive_filename)
        
        shutil.move(file_path, archive_path)
        return archive_path

