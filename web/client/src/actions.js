import _ from 'lodash';

export const PRINTER_FETCH_REQUEST = "PRINTER_FETCH_REQUEST";
export const PRINTER_FETCH_SUCCESS = "PRINTER_FETCH_SUCCESS";
export const PRINTER_LIST_FETCH_REQUEST = "PRINTER_LIST_FETCH_REQUEST";
export const PRINTER_LIST_FETCH_SUCCESS = "PRINTER_LIST_FETCH_SUCCESS";

// Helper

const getJSON = (url, params) => {
    return fetch(url, { data: params }).then(result => result.json());
};

const postJSON = (url, data) => {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(result => result.json());
};

const patchJSON = (url, data) => {
    return fetch(url, {
        method: 'PATCH',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(result => result.json());
};


// Printers REST APIs

export const printerListFetchSuccess = printers => ({
    type: PRINTER_LIST_FETCH_SUCCESS,
    printers
});

export const printerListFetchRequest = () => ({
    type: PRINTER_LIST_FETCH_REQUEST,
});

export const fetchPrinters = () => {
    return dispatch => {
        dispatch(printerListFetchRequest());
        getJSON('/api/printers')
            .then(printers => {
                dispatch(printerListFetchSuccess(printers));
            });
    };
};

export const printerFetchSuccess = printer => ({
    type: PRINTER_FETCH_SUCCESS,
    printer
});

export const printerFetchRequest = () => ({
    type: PRINTER_FETCH_REQUEST,
});

export const fetchPrinter = (printerId) => {
    return dispatch => {
        dispatch(printerFetchRequest());
        getJSON(`/api/printers/${printerId}`)
            .then(printer => {
                dispatch(printerFetchSuccess(printer));
            });
    };
};

export const updatePrinter = (data) => {
    return dispatch => {
        const printerId = _.get(data, 'printer.id');
        let apiCall;
        if (printerId) {
            apiCall = patchJSON(`/printers/${printerId}`, data);
        } else {
            apiCall = postJSON('/printers', data);
        }
        apiCall()
            .then(() => {
                dispatch(fetchPrinters());
            });
    };
};