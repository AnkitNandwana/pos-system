import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_PLUGINS } from '../graphql/queries';
import { UPDATE_PLUGIN_MUTATION } from '../graphql/mutations';
import { Plugin } from '../types';
import { Settings, ToggleOn, ToggleOff, Edit, Save, Cancel } from '@mui/icons-material';

const AVAILABLE_EVENTS = ['EMPLOYEE_LOGIN', 'EMPLOYEE_LOGOUT', 'SESSION_TERMINATED'];

interface PluginsQueryData {
  plugins: Plugin[];
}

const PluginsPage: React.FC = () => {
  const [editingPlugin, setEditingPlugin] = useState<string | null>(null);
  const [editConfig, setEditConfig] = useState('');
  const [editEvents, setEditEvents] = useState<string[]>([]);

  const { data, loading, refetch } = useQuery<PluginsQueryData>(GET_PLUGINS);
  const [updatePlugin] = useMutation(UPDATE_PLUGIN_MUTATION, {
    onCompleted: () => refetch()
  });

  const handleTogglePlugin = async (plugin: Plugin) => {
    await updatePlugin({
      variables: {
        id: plugin.id,
        enabled: !plugin.enabled
      }
    });
  };

  const handleEditStart = (plugin: Plugin) => {
    setEditingPlugin(plugin.id);
    setEditConfig(plugin.config || '{}');
    setEditEvents(plugin.supportedEvents || []);
  };

  const handleEditSave = async (pluginId: string) => {
    await updatePlugin({
      variables: {
        id: pluginId,
        config: editConfig,
        supportedEvents: editEvents
      }
    });
    setEditingPlugin(null);
  };

  const handleEditCancel = () => {
    setEditingPlugin(null);
    setEditConfig('');
    setEditEvents([]);
  };

  const handleEventToggle = (event: string) => {
    setEditEvents(prev => 
      prev.includes(event) 
        ? prev.filter(e => e !== event)
        : [...prev, event]
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading plugins...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Settings className="text-3xl text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-800">Plugin Management</h1>
          </div>
          <p className="text-gray-600">Configure and manage system plugins</p>
        </div>

        <div className="grid gap-6">
          {data?.plugins?.map((plugin: Plugin) => (
            <div key={plugin.id} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-800">{plugin.name}</h3>
                    <button
                      onClick={() => handleTogglePlugin(plugin)}
                      className="flex items-center space-x-1 text-sm"
                    >
                      {plugin.enabled ? (
                        <ToggleOn className="text-green-500 text-2xl" />
                      ) : (
                        <ToggleOff className="text-gray-400 text-2xl" />
                      )}
                      <span className={plugin.enabled ? 'text-green-600' : 'text-gray-500'}>
                        {plugin.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </button>
                  </div>
                  <p className="text-gray-600 mb-4">{plugin.description}</p>
                </div>
                
                <button
                  onClick={() => handleEditStart(plugin)}
                  className="flex items-center space-x-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition"
                >
                  <Edit className="text-sm" />
                  <span>Edit</span>
                </button>
              </div>

              {editingPlugin === plugin.id ? (
                <div className="space-y-4 border-t pt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Configuration (JSON)</label>
                    <textarea
                      value={editConfig}
                      onChange={(e) => setEditConfig(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={4}
                      placeholder="{}"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Supported Events</label>
                    <div className="flex flex-wrap gap-2">
                      {AVAILABLE_EVENTS.map(event => (
                        <button
                          key={event}
                          onClick={() => handleEventToggle(event)}
                          className={`px-3 py-1 rounded-full text-sm transition ${
                            editEvents.includes(event)
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          {event}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEditSave(plugin.id)}
                      className="flex items-center space-x-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                    >
                      <Save className="text-sm" />
                      <span>Save</span>
                    </button>
                    <button
                      onClick={handleEditCancel}
                      className="flex items-center space-x-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                    >
                      <Cancel className="text-sm" />
                      <span>Cancel</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 border-t pt-4">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Configuration:</span>
                    <pre className="mt-1 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                      {plugin.config || '{}'}
                    </pre>
                  </div>
                  
                  <div>
                    <span className="text-sm font-medium text-gray-700">Supported Events:</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {plugin.supportedEvents?.map(event => (
                        <span key={event} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {event}
                        </span>
                      )) || <span className="text-gray-500 text-sm">None</span>}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PluginsPage;