import i18n from '@src/i18n/i18n.js'

export default [
  {
    id: 'notify_on_failure_alert',
    title: `${i18n.t('Failure alerts')}`,
    description: `${i18n.t('When possible failures are detected')}`,
  },
  {
    id: 'print_job',
    title: `${i18n.t('Print job events')}`,
    description: `${i18n.t('Upon start/end/cancellation of a print job')}`,
    subcategories: [
      {
        id: 'notify_on_print_done',
        title: `${i18n.t('When print is done')}`,
        enabledByDefault: true,
      },
      {
        id: 'notify_on_print_cancelled',
        title: `${i18n.t('When print is cancelled')}`,
        enabledByDefault: false,
      },
      {
        id: 'notify_on_filament_change',
        title: `${i18n.t('When printer needs attention')}`,
        description: `${i18n.t('Such as filament change or run-out')}`,
        enabledByDefault: true,
      },
      {
        id: 'notify_on_print_start',
        title: `${i18n.t('When print is started')}`,
        enabledByDefault: false,
      },
      {
        id: 'notify_on_print_pause',
        title: `${i18n.t('When print is paused')}`,
        description: `${i18n.t('Note: this event may be triggered by other plugins that pause the print frequently, such as the timelapse plugin')}`,
        enabledByDefault: false,
      },
      {
        id: 'notify_on_print_resume',
        title: `${i18n.t('When print is resumed')}`,
        description: `${i18n.t('Note: this event may be triggered by other plugins that pause the print frequently, such as the timelapse plugin')}`,
        enabledByDefault: false,
      },
    ],
  },
  {
    id: 'notify_on_heater_status',
    title: `${i18n.t('Heater status change')}`,
    description: `${i18n.t('Heater reached target or cooled down')}`,
  },
]
