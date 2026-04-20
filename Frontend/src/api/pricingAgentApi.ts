import api from './authApi';

export const pricingAgentApi = {
  
  suggest: (startDate: string, endDate: string) =>
    api.post('/agents/dynamic-pricing/suggest', null, { params: { start_date: startDate, end_date: endDate }, timeout: 60000 }).then((r) => r.data),

  
  apply: (suggestions: Array<any>) => api.post('/agents/dynamic-pricing/apply', { suggestions }).then((r) => r.data),
};
