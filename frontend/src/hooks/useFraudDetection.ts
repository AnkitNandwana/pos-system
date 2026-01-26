import { useEffect, useRef, useState, useCallback } from 'react';

interface FraudAlert {
  alert_id: string;
  rule_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  details: any;
  timestamp: string;
}

interface UseFraudDetectionProps {
  terminalId: string | null;
  onFraudAlert: (alert: FraudAlert) => void;
  enabled?: boolean;
}

export const useFraudDetection = ({ 
  terminalId, 
  onFraudAlert, 
  enabled = true 
}: UseFraudDetectionProps) => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close(1000);
    }
    wsRef.current = null;
    setIsConnected(false);
  }, []);

  useEffect(() => {
    if (!terminalId || !enabled) {
      disconnect();
      return;
    }

    // Prevent multiple connections
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    const connectWebSocket = () => {
      if (wsRef.current) {
        wsRef.current.close();
      }

      const wsUrl = `ws://localhost:8000/ws/fraud-alerts/${terminalId}/`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Fraud detection WebSocket connected');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'fraud_alert') {
            console.log('Fraud alert received:', data);
            onFraudAlert({
              alert_id: data.alert_id,
              rule_id: data.rule_id,
              severity: data.severity,
              details: data.details,
              timestamp: data.timestamp
            });
          }
        } catch (error) {
          console.error('Error parsing fraud alert:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('Fraud detection WebSocket disconnected:', event.code);
        setIsConnected(false);
        wsRef.current = null;
        // Only reconnect if not a normal closure and still enabled
        if (event.code !== 1000 && enabled && terminalId) {
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('Fraud detection WebSocket error:', error);
        setIsConnected(false);
      };
    };

    connectWebSocket();

    return disconnect;
  }, [terminalId, enabled, onFraudAlert, disconnect]);

  return { isConnected, disconnect };
};