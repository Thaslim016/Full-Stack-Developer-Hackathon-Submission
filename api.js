const API = "/api";

export async function request(path, options = {}) {
  const token = localStorage.getItem("darukaa_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
export async function login(email, password) {
  const data = await request("/auth/login", {method:"POST",body:JSON.stringify({email,password})});
  localStorage.setItem("darukaa_token", data.access_token); return data;
}
export async function register(name,email,password) { return request("/auth/register",{method:"POST",body:JSON.stringify({name,email,password})}); }
export async function createSite(projectId,name,geometry,extra={}) { return request(`/projects/${projectId}/sites`,{method:"POST",body:JSON.stringify({name,geometry,...extra})}); }
