import { useEffect, useRef, useCallback } from 'react';

interface SessionMessage {
  type: 'session_terminated';
  message: string;
  reason: string;
  timestamp: string;
}

interface UseSessionMonitorProps {
  terminalId: string | null;
  onSessionTerminated: () => void;
  enabled?: boolean;
}

export const useSessionMonitor = ({ 
  terminalId, 
  onSessionTerminated, 
  enabled = true 
}: UseSessionMonitorProps) => {
  const wsRef = useRef<WebSocket | null>(null);
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

      const wsUrl = `ws://localhost:8000/ws/session/${terminalId}/`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Session WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data: SessionMessage = JSON.parse(event.data);
          if (data.type === 'session_terminated') {
            console.log('Session terminated:', data.message);
            onSessionTerminated();
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('Session WebSocket disconnected:', event.code);
        wsRef.current = null;
        // Only reconnect if not a normal closure and still enabled
        if (event.code !== 1000 && enabled && terminalId) {
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('Session WebSocket error:', error);
      };
    };

    connectWebSocket();

    return disconnect;
  }, [terminalId, enabled, onSessionTerminated, disconnect]);

  return { disconnect };
};