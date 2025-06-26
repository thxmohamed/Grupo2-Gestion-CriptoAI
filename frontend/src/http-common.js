import axios from "axios";

const BackendServer = import.meta.env.BACKEND_SERVER || 'localhost';
const BackendPort = import.meta.env.BACKEND_PORT || '8000';

console.log('Backend Server:', BackendServer);
console.log('Backend Port:', BackendPort);

const apiClient = axios.create({
    baseURL: `http://${BackendServer}:${BackendPort}`,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor para logging de requests (opcional)
apiClient.interceptors.request.use(
    (config) => {
        console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
        return config;
    },
    (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
    }
);

// Interceptor para logging de responses (opcional)
apiClient.interceptors.response.use(
    (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
    },
    (error) => {
        console.error('❌ Response Error:', error.response?.status, error.response?.statusText);
        return Promise.reject(error);
    }
);

export default apiClient;