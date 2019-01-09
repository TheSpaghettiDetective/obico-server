import * as actions from "./actions";

const printers = (state = [], action) => {
    switch (action.type) {
        case actions.PRINTER_LIST_FETCH_SUCCESS:
            return action.printers;
        default:
            return state;
    }
}

export default {
    printers,
};