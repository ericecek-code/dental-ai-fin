import { useMutation } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE = window.location.origin;

export interface AnalyzePayload {
  file: File;
  conf?: number;
}

export interface GeminiPayload {
  file: File;
}

export interface ComparePayload {
  file: File;
  conf?: number;
}

export const useAnalyze = () =>
  useMutation({
    mutationFn: async ({ file, conf = 0.01 }: AnalyzePayload) => {
      const form = new FormData();
      form.append('file', file);
      const { data } = await axios.post(
        `${API_BASE}/analyze/?conf=${conf}`,
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      );
      return data;
    },
  });

export const useGeminiAnalyze = () =>
  useMutation({
    mutationFn: async ({ file }: GeminiPayload) => {
      const form = new FormData();
      form.append('file', file);
      const { data } = await axios.post(
        `${API_BASE}/vision/analyze`,
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      );
      return data;
    },
  });

export const useCompareAnalyze = () =>
  useMutation({
    mutationFn: async ({ file, conf = 0.05 }: ComparePayload) => {
      const form = new FormData();
      form.append('file', file);
      const { data } = await axios.post(
        `${API_BASE}/analyze/compare?conf=${conf}`,
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      );
      return data;
    },
  });

export const useJobResults = (jobId: string | null) => {
  const fetchResults = async () => {
    const { data } = await axios.get(`${API_BASE}/results/${jobId}`);
    return data;
  };
  return { fetchResults };
};
