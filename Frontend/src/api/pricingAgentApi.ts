import api from './authApi';

export const pricingAgentApi = {
  // Suggest pricing for a date range
  suggest: (startDate: string, endDate: string) =>
    api.post('/agents/dynamic-pricing/suggest', null, { params: { start_date: startDate, end_date: endDate }, timeout: 60000 }).then((r) => r.data),

  // Apply provided suggestions (requires moderator auth)
  // Wrap suggestions in an object to satisfy backend body validation
  apply: (suggestions: Array<any>) => api.post('/agents/dynamic-pricing/apply', { suggestions }).then((r) => r.data),
};
