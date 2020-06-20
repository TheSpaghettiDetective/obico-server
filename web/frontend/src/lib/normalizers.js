import moment from 'moment';
import filter from 'lodash/filter';

export const toMomentOrNull = datetimeStr => {
    if (!datetimeStr) {
        return null;
    }
    return moment(datetimeStr);
}

export const normalizedPrint = print => {
    print.ended_at = toMomentOrNull(print.cancelled_at || print.finished_at);
    print.started_at = toMomentOrNull(print.started_at);
    print.uploaded_at = toMomentOrNull(print.uploaded_at);
    print.is_cancelled = print.cancelled_at !== null;
    print.is_finished = print.finished_at !== null;
    print.is_uploaded = print.uploaded_at !== null;
    print.has_detective_view = print.prediction_json_url !== null && print.tagged_video_url !== null;
    print.focused_review_pending = print.printshotfeedback_set.length > 0 && filter(print.printshotfeedback_set, shot => shot.answered_at).length >= print.printshotfeedback_set.length;
    return print;
}
