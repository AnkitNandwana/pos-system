export interface Employee {
  id: number;
  username: string;
  firstName: string;
  lastName: string;
  role: string;
}

export interface Terminal {
  terminalId: string;
  loginTime: string;
  isActive: boolean;
}

export interface Basket {
  basketId: string;
  status: string;
  employee: {
    id: number;
    username: string;
  };
}

export interface Plugin {
  id: string;
  name: string;
  enabled: boolean;
  description: string;
  config: string;
  supportedEvents: string[];
}

export interface LoginResponse {
  token: string;
  employee: Employee;
  terminal: Terminal;
}

export interface LogoutResponse {
  success: boolean;
  message: string;
}