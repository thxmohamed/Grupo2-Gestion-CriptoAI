import axios from "axios";

const BackendServer = import.meta.env.BACKEND_SERVER;
const BackendPort = import.meta.env.BACKEND_PORT;

console.log(BackendServer)
console.log(BackendPort)

export default axios.create({
    baseURL: `http://${BackendServer}:${BackendPort}`,
    headers: {
        'Content-Type': 'application/json'
    }
});