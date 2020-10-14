import moment from 'moment'

export const toDuration = (seconds, isPrinting) => {
  if (seconds == null || seconds == 0) {
    return {
      valid: false,
      printing: isPrinting,
    }
  } else {
    var d = moment.duration(seconds, 'seconds')
    var h = Math.floor(d.asHours())
    var m = d.minutes()
    var s = d.seconds()
    return {
      valid: true,
      printing: isPrinting,
      hours: h,
      showHours: (h>0),
      minutes: m,
      showMinutes: (h>0 || m>0),
      seconds: s,
      showSeconds: (h==0 && m==0)
    }
  }
}
