import axios from "axios";
import config from "../config.json";


axios.defaults.headers = {
  'Cache-Control': 'no-cache',
  'Pragma': 'no-cache',
  'Expires': '0',
};

axios.interceptors.response.use(null, error => {
    const expectedError =
        error.response &&
        error.response.status >= 400 &&
        error.response.status < 500;
    if(!expectedError) {
        console.log('Unexpected HTTP error', error);
    }
    return Promise.reject(error);
})


export async function cleanQuery(query) {
    try {
        const response = await axios.get(`${config.apiUrl}/clean_query/${query}`);
        return response.data;
    } catch(exc) {
        return null;
    }
}

export async function getPrefixesData(prefix) {
    const response = await axios.get(`${config.apiUrl}/prefix/${prefix}`);
    return response.data;
}

const api = {
    getPrefixesData,
    cleanQuery,
}
export default api;
