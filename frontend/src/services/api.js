import axios from "axios";
import config from "../config.json";


export async function getPrefixesData(prefix) {
    const response = await axios.get(`${config.apiUrl}/prefix/${prefix}`);
    return response.data;
}

const api = {
    getPrefixesData,
}
export default api;
