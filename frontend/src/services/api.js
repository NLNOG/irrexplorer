import axios from "axios";
import config from "../config.json";

let source = axios.CancelToken.source();

axios.defaults.headers = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Expires': '0',
};

axios.interceptors.response.use(null, error => {
    const expectedError =
        error.message === 'cancel' ||
        (error.response &&
            error.response.status >= 400 &&
            error.response.status < 500);
    if (!expectedError) {
        console.log('Unexpected HTTP error', error);
    }
    return Promise.reject(error);
})


export async function cleanQuery(query) {
    try {
        const response = await axios.get(`${config.apiUrl}/clean_query/${query}`);
        return response.data;
    } catch (exc) {
        return {error: exc.response.data};
    }
}

async function performRequest(url) {
    try {
        const response = await axios.get(url, {cancelToken: source.token});
        return response.data;
    } catch (exc) {
        return null;
    }

}

export async function getPrefixesForPrefix(prefix) {
    return await performRequest(`${config.apiUrl}/prefixes/prefix/${prefix}`);
}

export async function getPrefixesForASN(asn) {
    return await performRequest(`${config.apiUrl}/prefixes/asn/${asn}`);
}

export async function getSetMemberOf(target) {
    return await performRequest(`${config.apiUrl}/sets/member-of/${target}`);
}

export async function getSetExpansion(target) {
    return await performRequest(`${config.apiUrl}/sets/expand/${target}`);
}

export async function cancelAllRequests() {
    await source.cancel('cancel');
    source = axios.CancelToken.source();
}

const api = {
    getPrefixesForPrefix,
    getPrefixesForASN,
    cleanQuery,
    getSetMemberOf,
    getSetExpansion,
    cancelAllRequests,
}
export default api;
