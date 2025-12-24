import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
} from '@mui/material';
import api from '../services/api';

function Assets() {
  const [assets, setAssets] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAssets();
  }, [search]);

  const fetchAssets = async () => {
    try {
      const params = search ? { search } : {};
      const response = await api.get('/assets/', { params });
      setAssets(response.data);
    } catch (error) {
      console.error('Error fetching assets:', error);
    }
  };

  const handleRowClick = (assetId) => {
    navigate(`/assets/${assetId}`);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        자산 관리
      </Typography>

      <TextField
        fullWidth
        label="검색 (자산명, IP, 위치)"
        variant="outlined"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        sx={{ mt: 2, mb: 2 }}
      />

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>자산명</TableCell>
              <TableCell>자산번호</TableCell>
              <TableCell>상태</TableCell>
              <TableCell>제조사</TableCell>
              <TableCell>모델</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {assets
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((asset) => (
                <TableRow
                  key={asset.id}
                  hover
                  onClick={() => handleRowClick(asset.id)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{asset.id}</TableCell>
                  <TableCell>{asset.name}</TableCell>
                  <TableCell>{asset.asset_tag || '-'}</TableCell>
                  <TableCell>{asset.status}</TableCell>
                  <TableCell>{asset.manufacturer || '-'}</TableCell>
                  <TableCell>{asset.model || '-'}</TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={assets.length}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>
    </Box>
  );
}

export default Assets;

