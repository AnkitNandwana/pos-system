import { useState, useEffect } from 'react';

export const usePluginStatus = (pluginName) => {
  const [isEnabled, setIsEnabled] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkPluginStatus = async () => {
      try {
        const response = await fetch(`/api/plugins/status/${pluginName}/`);
        const data = await response.json();
        setIsEnabled(data.enabled);
      } catch (error) {
        console.error(`Failed to check ${pluginName} plugin status:`, error);
        setIsEnabled(false);
      } finally {
        setLoading(false);
      }
    };

    checkPluginStatus();
  }, [pluginName]);

  return { isEnabled, loading };
};