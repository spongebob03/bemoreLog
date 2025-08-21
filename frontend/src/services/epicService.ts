import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Epic {
  id: number;
  title: string;
  description: string;
  status: string;
  depth: number;
  position?: number;  // 3x3 그리드 내 시계방향 위치 (0: 중앙, 1-8: 주변)
  core_epic_id: number | null;
  created_at: string;
  updated_at: string | null;
  subs: Epic[];
}

export interface EpicCreate {
  title: string;
  description: string;
  status: string;
  position?: number;
  core_epic_id?: number | null;
}

export interface EpicUpdate {
  title?: string;
  description?: string;
  status?: string;
  depth?: number;
  position?: number;
  core_epic_id?: number | null;
}

class EpicService {
  async getEpics(): Promise<Epic[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/epic`);
      return response.data;
    } catch (error) {
      console.error('Error fetching epics:', error);
      throw error;
    }
  }

  async getEpic(id: number): Promise<Epic> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/epic/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching epic ${id}:`, error);
      throw error;
    }
  }

  async createEpic(epic: EpicCreate): Promise<Epic> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/epic`, epic);
      return response.data;
    } catch (error) {
      console.error('Error creating epic:', error);
      throw error;
    }
  }

  async updateEpic(id: number, epic: EpicUpdate): Promise<Epic> {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/epic/${id}`, epic);
      return response.data;
    } catch (error) {
      console.error(`Error updating epic ${id}:`, error);
      throw error;
    }
  }

  async deleteEpic(id: number): Promise<Epic> {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/epic/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting epic ${id}:`, error);
      throw error;
    }
  }

  async deleteAllEpics(): Promise<{ message: string }> {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/epic`);
      return response.data;
    } catch (error) {
      console.error('Error deleting all epics:', error);
      throw error;
    }
  }
}

export default new EpicService();
