export default {
    printShotFeedbackList: printId =>
        `/api/v1/printshotfeedbacks/?print_id=${printId}`,
    printShotFeedback: shotId => `/api/v1/printshotfeedbacks/${shotId}/`,
    print: printId => `/api/v1/prints/${printId}/`,
}
