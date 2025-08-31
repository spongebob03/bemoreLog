import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Habit {
  id: number;
  epic_id: number | null;
  title: string;
  description: string | null;
  schedule: string | null; // cron 표현식
  target_count: number;
  status: 'active' | 'paused' | 'completed' | 'archived';
  current_combo: number;
  best_combo: number;
  total_completions: number;
  created_at: string;
  updated_at: string | null;
}

export interface HabitCreate {
  title: string;
  description?: string | null;
  schedule?: string | null; // cron 표현식
  target_count?: number;
  epic_id?: number | null;
}

export interface HabitUpdate {
  title?: string;
  description?: string | null;
  schedule?: string | null;
  target_count?: number;
  status?: 'active' | 'paused' | 'completed' | 'archived';
  epic_id?: number | null;
}

export interface HabitCommit {
  id: number;
  habit_id: number;
  description: string | null;
  effort: number; // 1-5 사이의 값
  created_at: string;
  updated_at: string | null;
}

export interface HabitCommitCreate {
  habit_id: number;
  description?: string | null;
  effort: number; // 1-5 사이의 값
}

class HabitService {
  async getHabits(epicId?: number, status?: string): Promise<Habit[]> {
    try {
      const params = new URLSearchParams();
      if (epicId) params.append('epic_id', epicId.toString());
      if (status) params.append('status', status);
      
      const response = await axios.get(`${API_BASE_URL}/api/habit?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching habits:', error);
      throw error;
    }
  }

  async getHabit(id: number): Promise<Habit> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/habit/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching habit ${id}:`, error);
      throw error;
    }
  }

  async createHabit(habit: HabitCreate): Promise<Habit> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/habit/`, habit);
      return response.data;
    } catch (error) {
      console.error('Error creating habit:', error);
      throw error;
    }
  }

  async updateHabit(id: number, habit: HabitUpdate): Promise<Habit> {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/habit/${id}`, habit);
      return response.data;
    } catch (error) {
      console.error(`Error updating habit ${id}:`, error);
      throw error;
    }
  }

  async deleteHabit(id: number): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/api/habit/${id}`);
    } catch (error) {
      console.error(`Error deleting habit ${id}:`, error);
      throw error;
    }
  }

  async updateHabitStatus(id: number, status: string): Promise<Habit> {
    try {
      const response = await axios.patch(`${API_BASE_URL}/api/habit/${id}/status?status=${status}`);
      return response.data;
    } catch (error) {
      console.error(`Error updating habit status ${id}:`, error);
      throw error;
    }
  }

  async createHabitCommit(habitId: number, commit: Omit<HabitCommitCreate, 'habit_id'>): Promise<HabitCommit> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/habit/${habitId}/commit`, {
        ...commit,
        habit_id: habitId
      });
      return response.data;
    } catch (error) {
      console.error(`Error creating habit commit for habit ${habitId}:`, error);
      throw error;
    }
  }

  async getHabitCommits(habitId: number, limit: number = 50): Promise<HabitCommit[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/habit/${habitId}/commits?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching habit commits for habit ${habitId}:`, error);
      throw error;
    }
  }

  // Epic과 연결된 Habit 생성을 위한 편의 메서드
  async createHabitForEpic(epicId: number, title: string, description?: string): Promise<Habit> {
    return this.createHabit({
      title,
      description,
      epic_id: epicId,
      target_count: 1,
      schedule: "0 9 * * *" // 기본값: 매일 오전 9시
    });
  }
}

export default new HabitService();
