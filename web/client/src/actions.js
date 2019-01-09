export const PRINTER_LIST_FETCH_REQUEST = "PRINTER_LIST_FETCH_REQUEST";
export const PRINTER_LIST_FETCH_SUCCESS = "PRINTER_LIST_FETCH_SUCCESS";

// Printers REST APIs

export const printersListFetchSuccess = printers => ({
    type: PRINTER_LIST_FETCH_SUCCESS,
    printers
});

export const printerListFetchRequest = () => ({
    type: PRINTER_LIST_FETCH_REQUEST,
});

export const fetchPrinters = () => {
    return dispatch => {
        dispatch(printerListFetchRequest());
        fetch('/api/printers')
            .then(response => response.json())
            .then(printers => {
                dispatch(printersListFetchSuccess(printers));
            });
    };
};
