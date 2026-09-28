/**
 * BhuSanket API Client — centralized HTTP client for the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface FetchOptions extends RequestInit {
  token?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { token, ...fetchOptions } = options;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    const authToken = token || this.token;
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // ─── Auth ────────────────────────────────────────────────────────
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) throw new Error('Invalid credentials');
    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  // ─── Dashboard ────────────────────────────────────────────────────
  async getCommandCenter() {
    return this.request('/dashboard/command-center');
  }

  // ─── Projects ────────────────────────────────────────────────────
  async getProjects(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request(`/projects${query}`);
  }

  async getProject(id: string) {
    return this.request(`/projects/${id}`);
  }

  async getProjectStages(id: string) {
    return this.request(`/projects/${id}/stages`);
  }

  async getProjectRisk(id: string) {
    return this.request(`/projects/${id}/risk`);
  }

  async getProjectTimeline(id: string) {
    return this.request(`/projects/${id}/timeline`);
  }

  async getProjectClocks(id: string) {
    return this.request(`/projects/${id}/clocks`);
  }

  async getBlockingParcels(id: string) {
    return this.request(`/projects/${id}/blocking-parcels`);
  }

  async getProjectExplanation(id: string) {
    return this.request(`/projects/${id}/explanation`);
  }

  async runWhatIf(id: string, actions: any[]) {
    return this.request(`/projects/${id}/whatif`, {
      method: 'POST',
      body: JSON.stringify({ actions }),
    });
  }

  async getDataQuality(id: string) {
    return this.request(`/projects/${id}/data-quality`);
  }

  // ─── Alerts ────────────────────────────────────────────────────
  async getAlerts(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request(`/alerts${query}`);
  }

  async acknowledgeAlert(id: string, by: string) {
    return this.request(`/alerts/${id}/ack`, {
      method: 'POST',
      body: JSON.stringify({ acknowledged_by: by }),
    });
  }

  // ─── Interventions ────────────────────────────────────────────────
  async getAllowedActions() {
    return this.request('/interventions/actions');
  }

  async createIntervention(data: any) {
    return this.request('/interventions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getInterventions(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request(`/interventions${query}`);
  }

  // ─── GIS ────────────────────────────────────────────────────────
  async getGeoProjects(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request(`/geo/projects${query}`);
  }

  async getGeoParcels(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request(`/geo/parcels${query}`);
  }

  // ─── Governance ────────────────────────────────────────────────────
  async getModels() {
    return this.request('/governance/models');
  }

  async getAuditLog(params?: Record<string, string>) {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return this.request(`/governance/audit${query}`);
  }

  async getDataSources() {
    return this.request('/governance/data-sources');
  }

  // ─── Events ────────────────────────────────────────────────────
  async ingestEvent(data: any) {
    return this.request('/events', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiClient(API_BASE);
export default api;
