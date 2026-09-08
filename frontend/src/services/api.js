import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

export const fetchInstances = async () => {
  const res = await axios.get(`${API_BASE}/instances`);
  return res.data;
};

export const fetchDailyBrief = async () => {
  const res = await axios.get(`${API_BASE}/brief`);
  return res.data;
};

export const fetchAuditLogs = async () => {
  const res = await axios.get(`${API_BASE}/audit`);
  return res.data;
};

export const stopInstance = async (instanceId) => {
  const res = await axios.post(`${API_BASE}/instances/stop`, {
    instance_id: instanceId,
    confirmed: true,
  });
  return res.data;
};