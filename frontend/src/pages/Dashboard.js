import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import api from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>로딩 중...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        대시보드
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                전체 자산
              </Typography>
              <Typography variant="h4">
                {stats?.total_assets || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                운영 중인 자산
              </Typography>
              <Typography variant="h4">
                {stats?.operational_assets || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                최근 로그 (24시간)
              </Typography>
              <Typography variant="h4">
                {stats?.recent_logs || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {stats?.warning_assets && stats.warning_assets.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="warning" icon={<WarningIcon />}>
              <Typography variant="h6" gutterBottom>
                경고: Level 1 이벤트가 감지된 자산
              </Typography>
              {stats.warning_assets.map((asset) => (
                <Typography key={asset.id}>- {asset.name}</Typography>
              ))}
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default Dashboard;

