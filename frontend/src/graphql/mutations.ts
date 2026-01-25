import { gql } from '@apollo/client';

export const LOGIN_MUTATION = gql`
  mutation Login($username: String!, $password: String!) {
    login(username: $username, password: $password) {
      token
      employee {
        id
        username
        firstName
        lastName
        role
      }
      terminal {
        terminalId
        loginTime
        isActive
      }
    }
  }
`;

export const LOGOUT_MUTATION = gql`
  mutation Logout($terminalId: String!) {
    logout(terminalId: $terminalId) {
      success
      message
    }
  }
`;

export const START_BASKET_MUTATION = gql`
  mutation StartBasket($employeeId: Int!, $terminalId: String!) {
    startBasket(employeeId: $employeeId, terminalId: $terminalId) {
      basketId
      status
      employee {
        id
        username
      }
    }
  }
`;

export const UPDATE_PLUGIN_MUTATION = gql`
  mutation UpdatePlugin($id: ID!, $enabled: Boolean, $config: String, $supportedEvents: [String!]) {
    updatePlugin(id: $id, enabled: $enabled, config: $config, supportedEvents: $supportedEvents) {
      id
      name
      enabled
      description
      config
      supportedEvents
    }
  }
`;