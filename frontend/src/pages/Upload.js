import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  LinearProgress,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import api from '../services/api';

function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('파일을 선택해주세요.');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || '업로드 실패');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        ZIP 파일 업로드
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Box sx={{ mb: 2 }}>
          <input
            accept=".zip"
            style={{ display: 'none' }}
            id="zip-file-input"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="zip-file-input">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUploadIcon />}
              disabled={uploading}
            >
              파일 선택
            </Button>
          </label>
          {file && (
            <Typography sx={{ mt: 1 }}>선택된 파일: {file.name}</Typography>
          )}
        </Box>

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || uploading}
          sx={{ mt: 2 }}
        >
          업로드
        </Button>

        {uploading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Typography sx={{ mt: 1 }}>업로드 및 처리 중...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="h6">처리 완료</Typography>
            <Typography>총 파일: {result.stats?.total_files || 0}</Typography>
            <Typography>처리 완료: {result.stats?.processed || 0}</Typography>
            <Typography>오류: {result.stats?.errors || 0}</Typography>
          </Alert>
        )}
      </Paper>
    </Box>
  );
}

export default Upload;

