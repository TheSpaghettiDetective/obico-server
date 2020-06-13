export default {
    printShotFeedbackList: printId =>
        `/api/v1/printshotfeedbacks/?print_id=${printId}`,
    printShotFeedback: (shotId, printId) => `/api/v1/printshotfeedbacks/${shotId}/?print_id=${printId}`,
    print: printId => `/api/v1/prints/${printId}/`,
}
