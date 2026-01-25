import { gql } from '@apollo/client';

export const GET_PLUGINS = gql`
  query GetPlugins {
    plugins {
      id
      name
      enabled
      description
      config
      supportedEvents
    }
  }
`;