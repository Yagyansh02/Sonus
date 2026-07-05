import api from '@/lib/api';
import { API_ENDPOINTS } from '@/constants';
import type { RAGAskRequest, RAGAskResponse } from '@/types';

/**
 * Ask a cultural interpretation question about a song via the RAG pipeline.
 */
export async function askQuestion(request: RAGAskRequest): Promise<RAGAskResponse> {
  const { data } = await api.post<RAGAskResponse>(API_ENDPOINTS.RAG_ASK, request);
  return data;
}
