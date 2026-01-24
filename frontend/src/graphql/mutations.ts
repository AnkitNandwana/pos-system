import { gql } from '@apollo/client';

// Placeholder for future mutations
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