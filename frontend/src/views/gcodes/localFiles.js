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

export const isPrinterAvailable = (normalizedPrinter) => {
  if (normalizedPrinter.status === null) {
    return false
  }

  if (normalizedPrinter.isAgentMoonraker()) {
    return false
  }

  // Temporary comment this to test earlier dev version of plugin
  if (!semverGte(get(normalizedPrinter, 'settings.agent_version', '0.0.0'), '2.3.0')) {
    return false
  }

  return true
}
