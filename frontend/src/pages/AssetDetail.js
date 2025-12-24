import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import api from '../services/api';

function AssetDetail() {
  const { id } = useParams();
  const [asset, setAsset] = useState(null);
  const [maintenanceLogs, setMaintenanceLogs] = useState([]);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    fetchAsset();
    fetchMaintenanceLogs();
  }, [id]);

  const fetchAsset = async () => {
    try {
      const response = await api.get(`/assets/${id}`);
      setAsset(response.data);
    } catch (error) {
      console.error('Error fetching asset:', error);
    }
  };

  const fetchMaintenanceLogs = async () => {
    try {
      const response = await api.get('/maintenance/logs', {
        params: { asset_id: id },
      });
      setMaintenanceLogs(response.data);
    } catch (error) {
      console.error('Error fetching maintenance logs:', error);
    }
  };

  if (!asset) {
    return <Typography>로딩 중...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {asset.name}
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="제원" />
          <Tab label="점검이력" />
          <Tab label="이벤트로그 분석" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                기본 정보
              </Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>자산번호</TableCell>
                      <TableCell>{asset.asset_tag || '-'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>상태</TableCell>
                      <TableCell>{asset.status}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>제조사</TableCell>
                      <TableCell>{asset.manufacturer || '-'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>모델</TableCell>
                      <TableCell>{asset.model || '-'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>OS 정보</TableCell>
                      <TableCell>{asset.os_info || '-'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                점검 이력
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>점검일</TableCell>
                      <TableCell>점검유형</TableCell>
                      <TableCell>작업자</TableCell>
                      <TableCell>결과</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {maintenanceLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>{log.check_date}</TableCell>
                        <TableCell>{log.check_type}</TableCell>
                        <TableCell>{log.worker || '-'}</TableCell>
                        <TableCell>{log.result_status}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                이벤트 로그 분석
              </Typography>
              <Typography color="textSecondary">
                (구현 예정: MaintenanceDetails의 EventID 카운트 정보 표시)
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
}

export default AssetDetail;

