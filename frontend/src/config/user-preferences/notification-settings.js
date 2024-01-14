export default [
  {
    id: 'notify_on_failure_alert',
    title: 'Failure alerts',
    description: 'When possible failures are detected',
  },
  {
    id: 'print_job',
    title: 'Print job events',
    description: 'Upon start/end/cancellation of a print job',
    subcategories: [
      {
        id: 'notify_on_print_done',
        title: 'When print is done',
        enabledByDefault: true,
      },
      {
        id: 'notify_on_print_cancelled',
        title: 'When print is cancelled',
        enabledByDefault: false,
      },
      {
        id: 'notify_on_filament_change',
        title: 'When printer needs attention',
        description: 'Such as filament change or run-out',
        enabledByDefault: true,
      },
      {
        id: 'notify_on_print_start',
        title: 'When print is started',
        enabledByDefault: false,
      },
      {
        id: 'notify_on_print_pause',
        title: 'When print is paused',
        description: 'Note: this event may be triggered by other plugins that pause the print frequently, such as the timelapse plugin',
        enabledByDefault: false,
      },
      {
        id: 'notify_on_print_resume',
        title: 'When print is resumed',
        description: 'Note: this event may be triggered by other plugins that pause the print frequently, such as the timelapse plugin',
        enabledByDefault: false,
      },
    ],
  },
  {
    id: 'notify_on_heater_status',
    title: 'Heater status change',
    description: 'Heater reached target or cooled down',
  },
]
