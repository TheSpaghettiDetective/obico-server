export default [
  {
    id: 'notify_on_failure_alert',
    title: 'Failure alerts',
    description: 'When possible failures are detected',
  },
  {
    id: 'printer_status_change',
    title: 'Printer status change',
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
        title: 'When filament runs out or needs a change',
        enabledByDefault: true,
      },
      {
        id: 'notify_on_other_print_events',
        title: 'When other event happens',
        description: 'Print start, pause, resume, etc. (TBD. Help wanted!)',
        enabledByDefault: false,
      },
    ]
  },
  {
    id: 'notify_on_heater_status',
    title: 'Heater status change',
    description: 'Reached target or cooled down (TBD. Help wanted!)',
  },
]
