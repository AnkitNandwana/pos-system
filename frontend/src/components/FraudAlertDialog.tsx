import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  Chip
} from '@mui/material';
import { Warning, Error, Info, ReportProblem } from '@mui/icons-material';

interface FraudAlert {
  alert_id: string;
  rule_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  details: any;
  timestamp: string;
}

interface FraudAlertDialogProps {
  open: boolean;
  alert: FraudAlert | null;
  onAcknowledge: () => void;
}

const FraudAlertDialog: React.FC<FraudAlertDialogProps> = ({
  open,
  alert,
  onAcknowledge
}) => {
  if (!alert) return null;

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <Error className="text-red-600" />;
      case 'HIGH': return <Warning className="text-orange-600" />;
      case 'MEDIUM': return <ReportProblem className="text-yellow-600" />;
      case 'LOW': return <Info className="text-blue-600" />;
      default: return <Info className="text-blue-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'error';
      case 'HIGH': return 'warning';
      case 'MEDIUM': return 'warning';
      case 'LOW': return 'info';
      default: return 'info';
    }
  };

  const formatRuleName = (ruleId: string) => {
    return ruleId.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatDetails = (details: any) => {
    const items = [];
    if (details.threshold !== undefined) {
      items.push(`Threshold: ${details.threshold}`);
    }
    if (details.actual_value !== undefined) {
      items.push(`Actual: ${details.actual_value}`);
    }
    if (details.time_window !== undefined) {
      items.push(`Time Window: ${details.time_window}s`);
    }
    if (details.terminals) {
      items.push(`Terminals: ${details.terminals.join(', ')}`);
    }
    return items;
  };

  return (
    <Dialog 
      open={open} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: {
          border: `2px solid ${getSeverityColor(alert.severity) === 'error' ? '#f44336' : '#ff9800'}`,
        }
      }}
    >
      <DialogTitle className="bg-red-50 border-b">
        <Box className="flex items-center space-x-2">
          {getSeverityIcon(alert.severity)}
          <Typography variant="h6" className="font-bold text-red-800">
            FRAUD ALERT DETECTED
          </Typography>
          <Chip 
            label={alert.severity} 
            color={getSeverityColor(alert.severity) as any}
            size="small"
          />
        </Box>
      </DialogTitle>
      
      <DialogContent className="py-6">
        <Alert severity={getSeverityColor(alert.severity) as any} className="mb-4">
          <Typography variant="h6" className="font-semibold mb-2">
            {formatRuleName(alert.rule_id)}
          </Typography>
          <Typography variant="body2">
            Suspicious activity has been detected and requires your immediate attention.
          </Typography>
        </Alert>

        <Box className="space-y-3">
          <div>
            <Typography variant="subtitle2" className="font-semibold text-gray-700">
              Alert Details:
            </Typography>
            <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
              {formatDetails(alert.details).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <Typography variant="subtitle2" className="font-semibold text-gray-700">
              Alert ID:
            </Typography>
            <Typography variant="body2" className="text-gray-600 font-mono">
              {alert.alert_id}
            </Typography>
          </div>

          <div>
            <Typography variant="subtitle2" className="font-semibold text-gray-700">
              Timestamp:
            </Typography>
            <Typography variant="body2" className="text-gray-600">
              {new Date(alert.timestamp).toLocaleString()}
            </Typography>
          </div>
        </Box>
      </DialogContent>
      
      <DialogActions className="bg-gray-50 px-6 py-4">
        <Button
          onClick={onAcknowledge}
          variant="contained"
          color="primary"
          size="large"
          className="px-8 font-semibold"
        >
          Acknowledge Alert
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FraudAlertDialog;