import { toMomentOrNull } from '@src/lib/normalizers'
import filesize from 'filesize'
import semverGte from 'semver/functions/gte'
import get from 'lodash/get'

export const listFiles = (printerComm, options) => {
  const { query, path, onRequestEnd } = options

  let kwargs
  if (query) {
    kwargs = {
      filter: String(query),
      recursive: true,
    }
  } else {
    kwargs = {
      path,
      recursive: false,
      level: 1,
    }
  }

  printerComm.passThruToPrinter({
    func: 'list_files',
    target: '_file_manager',
    kwargs,
  },
  (err, ret) => {
    if (err) {
      onRequestEnd()
    } else if (ret) {
      let folders = []
      let files = []

      if (!ret?.local || !Object.keys(ret.local).length) {
        onRequestEnd()
        return
      }

      // ObicoUpload is used to cache Obico Cloud files and should be hidden from the users
      delete ret.local.ObicoUpload

      const items = Boolean(query) ? listRecoursively(ret.local) : Object.values(ret.local)
      for (const item of items) {
        if (item.type === 'folder') {
          folders.push({
            id: item.path,
            path: item.path,
            name: item.display,
            numItems: Object.keys(item.children).length,
          })
        } else {
          files.push({
            id: item.path,
            path: item.path,
            filename: item.name,
            num_bytes: item.size,
            filesize: filesize(item.size),
            created_at: toMomentOrNull(new Date(item.date * 1000)),
          })
        }
      }

      onRequestEnd({ folders, files })
    } else {
      onRequestEnd()
    }
  }
  )
}

const listRecoursively = (fileObj) => {
  const fileList = []
  for (const item of Object.values(fileObj)) {
    if (item.children) {
      fileList.push(...listRecoursively(item.children))
    } else {
      fileList.push(item)
    }
  }
  return fileList
}

export const getPrinterStorageAvailability = (normalizedPrinter) => {
  const agentName = normalizedPrinter.agentDisplayName()
  const MIN_OCTOPRINT_PLUGIN_VERSION = '2.3.0'
  const MIN_MOONRAKER_PLUGIN_VERSION = '1.2.0'

  if (normalizedPrinter.isOffline()) {
    return {
      key: 'offline',
      text: `${agentName} is offline`,
      rejectMessage: `${agentName} is offline. You can't browse the files on the ${agentName} when it's offline.`,
    }
  }

  if (!normalizedPrinter.isAgentMoonraker() && !semverGte(get(normalizedPrinter, 'settings.agent_version', '0.0.0'), MIN_OCTOPRINT_PLUGIN_VERSION)) {
    return {
      key: 'plugin_outdated',
      text: `Obico plugin outdated`,
      rejectMessage: `Please upgrade your Obico for ${agentName} to ${MIN_OCTOPRINT_PLUGIN_VERSION} or later`
    }
  }

  if (normalizedPrinter.isAgentMoonraker() && !semverGte(get(normalizedPrinter, 'settings.agent_version', '0.0.0'), MIN_MOONRAKER_PLUGIN_VERSION)) {
    return {
      key: 'plugin_outdated',
      text: `Obico plugin outdated`,
      rejectMessage: `Please upgrade your Obico for ${agentName} to ${MIN_MOONRAKER_PLUGIN_VERSION} or later`
    }
  }

  return {
    key: 'online',
    text: `${normalizedPrinter.agentDisplayName()} is online`,
  }
}
