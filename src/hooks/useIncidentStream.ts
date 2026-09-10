import { useEffect, useRef } from 'react';
import { apiBaseUrl } from '../services/api';

export interface IncidentSseEvent {
  id: string;
  type: string;
  timestamp: string;
  incident_id: string;
  run_id?: string;
  status?: string;
  payload: Record<string, any>;
}

export function useIncidentStream(
  incidentId: string | undefined,
  onEvent: (event: IncidentSseEvent) => void,
) {
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    if (!incidentId) return;

    let eventSource: EventSource | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    let isCancelled = false;

    function connect() {
      if (isCancelled) return;
      const url = `${apiBaseUrl()}/api/v1/incidents/${incidentId}/events/stream`;
      eventSource = new EventSource(url);

      eventSource.onmessage = (e) => {
        try {
          const data: IncidentSseEvent = JSON.parse(e.data);
          onEventRef.current(data);
        } catch {
          // Ignore parse error
        }
      };

      eventSource.onerror = () => {
        if (eventSource) {
          eventSource.close();
          eventSource = null;
        }
        // Attempt reconnect after 3 seconds
        if (!isCancelled) {
          reconnectTimeout = setTimeout(connect, 3000);
        }
      };
    }

    connect();

    return () => {
      isCancelled = true;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (eventSource) eventSource.close();
    };
  }, [incidentId]);
}
