import moment from 'moment'
import get from 'lodash/get'
import filesize from 'filesize'
import semverGte from 'semver/functions/gte'
import { humanizedDuration } from '@src/lib/formatters'
import { gcodeMetadata } from '@src/components/g-codes/gcode-metadata'
import {
  setPrinterTransientState,
  getPrinterCalculatedState,
} from '@src/lib/printer-transient-state'

export const toMomentOrNull = (datetimeStr) => {
  if (!datetimeStr) {
    return null
  }
  return moment(datetimeStr)
}

export const PrintStatus = {
  Printing: { key: 'printing', title: 'Printing...', isActive: true },
  Paused: { key: 'paused', title: 'Paused', isActive: true },
  Finished: { key: 'finished', title: 'Finished', isActive: false },
  Cancelled: { key: 'cancelled', title: 'Cancelled', isActive: false },
}

// ––––––––––––––––––––––

export const normalizedPrint = (print) => {
  print.started_at = toMomentOrNull(print.started_at)
  print.uploaded_at = toMomentOrNull(print.uploaded_at)
  print.finished_at = toMomentOrNull(print.finished_at)
  print.cancelled_at = toMomentOrNull(print.cancelled_at)
  print.ended_at = toMomentOrNull(print.ended_at)
  if (print.ended_at) {
    const duration = moment.duration(print.ended_at.diff(print.started_at))
    print.duration = humanizedDuration(duration.asSeconds())
  }
  print.has_alerts = Boolean(print.alerted_at)
  print.printShotFeedbackEligible =
    print.printshotfeedback_set && print.printshotfeedback_set.length > 0
  print.status = print.ended_at
    ? print.cancelled_at
      ? PrintStatus.Cancelled
      : PrintStatus.Finished
    : print.paused_at
    ? PrintStatus.Paused
    : PrintStatus.Printing
  if (print.printer) {
    print.printer = normalizedPrinter(print.printer)
  }
  if (print.g_code_file) {
    print.g_code_file = normalizedGcode(print.g_code_file)
  }
  return print
}

export const normalizedGcode = (gcode) => {
  if (!gcode) {
    return
  }

  gcode.created_at = toMomentOrNull(gcode.created_at)
  gcode.updated_at = toMomentOrNull(gcode.updated_at)
  gcode.deleted = toMomentOrNull(gcode.deleted)
  gcode.filesize = filesize(gcode.num_bytes)

  if (gcode.print_set) {
    gcode.print_set.map((p) => normalizedPrint(p))
    gcode.print_set.sort((a, b) => {
      if (!a.ended_at && !b.ended_at) {
        // if both in progress, sort by started_at
        if (a.started_at > b.started_at) {
          return -1
        } else if (a.started_at < b.started_at) {
          return 1
        } else {
          return 0
        }
      } else if (!a.ended_at) {
        return -1
      } else if (!b.ended_at) {
        return 1
      } else {
        if (a.ended_at > b.ended_at) {
          return -1
        } else if (a.ended_at < b.ended_at) {
          return 1
        } else {
          return 0
        }
      }
    })
    gcode.last_print = gcode.print_set[0]

    gcode.failedPrints = gcode.print_set.filter((p) => p.cancelled_at).length
    gcode.successPrints = gcode.print_set.filter((p) => p.finished_at).length
    gcode.totalPrints = gcode.print_set.length
  }

  // Normalize metadata
  gcode.metadata = {}

  if (gcode.metadata_json) {
    // obico file with metadata
    gcode.metadata = JSON.parse(gcode.metadata_json)
  } else if (gcode.analysis) {
    // octoprint file
    gcode.metadata.object_height = gcode.analysis.dimensions?.height
    gcode.metadata.estimated_time = gcode.analysis.estimatedPrintTime

    let filament_total
    if (gcode.analysis.filament) {
      const tools = Object.keys(gcode.analysis.filament)
      if (tools.length) {
        filament_total = 0
        tools.forEach((key) => {
          filament_total += gcode.analysis.filament[key].length
        })
      }
    }
    gcode.metadata.filament_total = filament_total
  } else {
    // either obico file without metadata or klipper file
    gcodeMetadata.forEach((v) => {
      if (gcode[v.name]) {
        gcode.metadata[v.name] = gcode[v.name]
      }
    })
  }

  // leave only non-null metadata
  Object.keys(gcode.metadata).forEach((key) => {
    if (gcode.metadata[key] === null || gcode.metadata[key] === undefined) {
      delete gcode.metadata[key]
    }
  })

  // Normalize thumbnail
  gcode.getBigThumbnailUrl = () => {
    return gcode.thumbnail1_url || gcode.thumbnail2_url || gcode.thumbnail3_url
  }
  gcode.getSmallThumbnailUrl = () => {
    return gcode.thumbnail3_url || gcode.thumbnail2_url || gcode.thumbnail1_url
  }

  return gcode
}

export const normalizedGcodeFolder = (folder) => {
  folder.created_at = toMomentOrNull(folder.created_at)
  folder.updated_at = toMomentOrNull(folder.updated_at)
  folder.numItems = folder.g_code_file_count + folder.g_code_folder_count
  return folder
}

export const normalizedPrinter = (newData, oldData) => {
  const printerMixin = {
    createdAt: function () {
      return toMomentOrNull(this.created_at)
    },
    progressCompletion: function () {
      return get(this, 'status.progress.completion', 0)
    },
    isOffline: function () {
      return get(this, 'status', null) === null
    },
    isPaused: function () {
      return get(this, 'status.state.flags.paused', false)
    },
    isDisconnected: function () {
      return get(this, 'status.state.flags.closedOrError', true)
    },
    isActive: function () {
      const flags = get(this, 'status.state.flags')
      // https://discord.com/channels/704958479194128507/705047010641838211/1013193281280159875
      return (
        Boolean(flags && flags.operational && (!flags.ready || flags.paused)) ||
        this.inTransientState()
      )
    },
    inTransientState: function () {
      const calculatedState = this.calculatedState()
      // Backward compatibility with OctoPrint-Obico 2.3.7 - 2.3.9
      if (calculatedState === 'Downloading G-Code') {
        return true
      }

      return calculatedState && calculatedState.endsWith('ing') && calculatedState !== 'Printing'
    },
    calculatedState: function () {
      return getPrinterCalculatedState(this, this.status?.state?.text)
    },
    calculatedStateColor: function () {
      const calcState = this.calculatedState()
      const colorMapping = {
        secondary: ['Offline', undefined, null],
        success: ['Operational'],
        neutral: ['Printing', 'G-Code Downloading', 'Downloading G-Code', 'Starting'],
        warning: ['Paused', 'Pausing', 'Resuming'],
        danger: ['Cancelling'],
      }

      for (const [color, states] of Object.entries(colorMapping)) {
        if (states.includes(calcState)) {
          return color
        }
      }
      return 'neutral' // fallback
    },
    setTransientState: function (stateText) {
      setPrinterTransientState(this, stateText)
      if (this.status) this.status = { ...this.status } // clone status to trigger immidiate UI update
    },
    inUserInteractionRequired: function () {
      return get(this, 'status.user_interaction_required', false)
    },
    hasError: function () {
      return (
        get(this, 'status.state.flags.error') ||
        get(this, 'status.state.text', '').toLowerCase().includes('error')
      )
    },
    isAgentMoonraker: function () {
      return get(this, 'agent_name', '') === 'moonraker_obico'
    },
    agentDisplayName: function () {
      return this.isAgentMoonraker() ? 'Klipper' : 'OctoPrint'
    },
    isAgentVersionGte: function (minOctoPrintAgentVersion, minMoonrakerAgentVersion) {
      return (
        (get(this, 'settings.agent_name', '') === 'octoprint_obico' &&
          semverGte(get(this, 'settings.agent_version', '0.0.0'), minOctoPrintAgentVersion)) ||
        (get(this, 'settings.agent_name', '') === 'moonraker_obico' &&
          semverGte(get(this, 'settings.agent_version', '0.0.0'), minMoonrakerAgentVersion))
      )
    },
    alertUnacknowledged: function () {
      return (
        get(this, 'current_print.alerted_at') &&
        moment(get(this, 'current_print.alerted_at')).isAfter(
          moment(get(this, 'current_print.alert_acknowledged_at') || 0)
        )
      )
    },
    // Printing availability
    isPrintable: function () {
      return !this.isOffline() && !this.isDisconnected() && !this.isActive() && !this.archived_at
    },
    printabilityText: function () {
      return this.isPrintable() ? 'Ready' : 'Unavailable'
    },
  }
  if (oldData) {
    if (
      get(oldData, 'status._ts', -1) > get(newData, 'status._ts', get(oldData, 'status._ts', 0))
    ) {
      delete newData.status
    }
    return {
      ...oldData,
      ...newData,
      ...printerMixin,
    }
  } else {
    return {
      ...newData,
      ...printerMixin,
    }
  }
}

export const normalizedPrinterEvent = (printerEvent) => {
  printerEvent.created_at = toMomentOrNull(printerEvent.created_at)
  return printerEvent
}
