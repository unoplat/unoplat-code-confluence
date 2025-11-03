// hooks/useAuthData.ts
import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { getFlagStatus, fetchGitHubUser } from '@/lib/api';
import { useAuthStore } from '@/stores/useAuthStore';

export const useAuthData = () => {
  const { setTokenStatus, setUser } = useAuthStore();

  // 1. token flag
  const tokenQuery = useQuery({
    queryKey: ['flags', 'isTokenSubmitted'],
    queryFn : () => getFlagStatus('isTokenSubmitted'),
    staleTime: 0,
  });

  // 2. user – enable only if token valid
  const userQuery = useQuery({
    queryKey: ['githubUser'],
    queryFn : fetchGitHubUser,
    enabled : !!tokenQuery.data?.status,
  });

  // Write‑through side‑effects (v5: prefer useEffect, not onSuccess) ...
  useEffect(() => {
    if (tokenQuery.data) setTokenStatus(tokenQuery.data);
  }, [tokenQuery.data, setTokenStatus]);            //  [oai_citation_attribution:10‡Stack Overflow](https://stackoverflow.com/questions/68690221/how-to-use-zustand-to-store-the-result-of-a-query?utm_source=chatgpt.com)

  useEffect(() => {
    if (userQuery.data) setUser(userQuery.data);
  }, [userQuery.data, setUser]);

  return { tokenQuery, userQuery };
};