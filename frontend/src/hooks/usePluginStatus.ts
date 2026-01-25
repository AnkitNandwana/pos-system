import { useQuery } from '@apollo/client';
import { useMemo } from 'react';
import { GET_PLUGINS } from '../graphql/queries';

export const usePluginStatus = () => {
  const { data, loading, error } = useQuery(GET_PLUGINS);
  
  return useMemo(() => {
    const status: { [key: string]: boolean } = {};
    data?.plugins?.forEach((plugin: any) => {
      status[plugin.name] = plugin.enabled;
    });
    return { pluginStatus: status, loading, error };
  }, [data, loading, error]);
};