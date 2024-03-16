import { toMomentOrNull } from '@src/lib/normalizers'
import filesize from 'filesize'
import _ from 'lodash'

export class PassThruTimeOutError extends Error {}

export function passThruPromise(printerComm, payload, timeout = 10) {
  return new Promise((resolve, reject) => {
    printerComm.passThruToPrinter(
      payload,
      (err, ret) => {
        if (err || ret?.error) {
          reject(err || ret?.error)
        } else {
          resolve(ret)
        }
      },
      timeout,
      () => {
        reject(new PassThruTimeOutError())
      }
    )
  })
}

export function shutdownWebcamStreamer(printerComm) {
  return passThruPromise(printerComm, {
    func: 'shutdown',
    target: 'webcam_streamer',
  })
}

export function fetchAgentWebcams(printerComm, printer) {
  return passThruPromise(printerComm, {
    func: 'list_system_webcams',
    target: 'webcam_streamer',
  })
}

export function startWebcamStreamer(printerComm, webcamName, streamingParams) {
  const payload = {
    func: 'start',
    target: 'webcam_streamer',
    args: [[{ name: webcamName, streaming_params: streamingParams }]],
  }

  return passThruPromise(printerComm, payload, 60)
}

export function fetchAgentCpuUsage(printerComm, isAgentMoonraker) {
  if (isAgentMoonraker) {
    return passThruPromise(printerComm, {
      target: 'moonraker_api',
      func: 'machine/proc_stats',
    }).then((procStats) => {
      return procStats?.system_cpu_usage
    })
  }
}

export function listPrinterLocalGCodesOctoPrint(printerComm, path, searchKeyword) {
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

  let kwargs
  if (searchKeyword) {
    // In OctoPrint we can do global search for better user experience. Hence path is ignored
    kwargs = { filter: String(searchKeyword), recursive: true }
  } else {
    kwargs = { path: path, recursive: false, level: 1 } // Return 1 level children so that we can do item count
  }

  return passThruPromise(printerComm, {
    func: 'list_files',
    target: '_file_manager',
    kwargs,
  }).then((ret) => {
    let folders = []
    let files = []

    if (!ret?.local || !Object.keys(ret.local).length) {
      return
    }

    // ObicoUpload is used to cache Obico Cloud files and should be hidden from the users
    delete ret.local.ObicoUpload

    const items = searchKeyword ? listRecoursively(ret.local) : Object.values(ret.local)
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
          ...item,
          id: item.path,
          filename: item.name,
          num_bytes: item.size,
          filesize: filesize(item.size),
          created_at: toMomentOrNull(new Date(item.date * 1000)),
          getBigThumbnailUrl: () => null,
          getSmallThumbnailUrl: () => null,
        })
      }
    }
    return { folders, files }
  })
}

export function listPrinterLocalGCodesMoonraker(printerComm, path, searchKeyword) {
  const pathPrefix = path == null ? '' : `${path}/`
  return passThruPromise(printerComm, {
    target: 'moonraker_api',
    func: 'server/files/directory',
    kwargs: {
      path: `gcodes/${path ? path : ''}`,
      extended: true,
    },
  }).then((ret) => {
    // subdirs should be ignored when user is searching
    const dirsInServerFormat = searchKeyword
      ? []
      : _.map(
          _.filter(
            _.get(ret, 'dirs', []),
            (d) => !d.dirname.startsWith('.') && !d.dirname.startsWith('Obico_Upload')
          ),
          (d) => {
            const path = `${pathPrefix}${d.dirname}`
            return {
              name: d.dirname,
              id: path,
              path,
              children: [], // To signify this is a folder, not a file
            }
          }
        )

    const filesInServerFormat = _.map(
      _.filter(
        _.get(ret, 'files', []),
        (f) =>
          !f.filename.startsWith('.') &&
          (!searchKeyword || f.filename.toLowerCase().includes(searchKeyword.toLowerCase()))
      ),
      (f) => {
        return {
          ...f,
          num_bytes: f.size,
          filesize: filesize(f.size),
          created_at: toMomentOrNull(new Date(f.modified * 1000)),
          path: `${pathPrefix}${f.filename}`,
          getBigThumbnailUrl: () => null,
          getSmallThumbnailUrl: () => null,
        }
      }
    )
    return { folders: dirsInServerFormat, files: filesInServerFormat }
  })
}

export function printPrinterLocalGCodeOctoPrint(printerComm, gcode) {
  const path = gcode.path
  return passThruPromise(printerComm, {
    func: 'select_file',
    target: '_printer',
    args: [`${path}`, null],
    kwargs: { printAfterSelect: 'true' },
  })
}

export function printPrinterLocalGCodeMoonraker(printerComm, gcode) {
  const path = gcode.path
  return passThruPromise(printerComm, {
    target: 'moonraker_api',
    func: 'printer/print/start',
    kwargs: {
      verb: 'post',
      filename: path,
    },
  })
}

export function repeatPrinterLocalGCode(printerComm, gcode) {
  return passThruPromise(printerComm, {
    target: 'file_operations',
    func: 'start_printer_local_print',
    args: [gcode],
  })
}


export function getMoonrakerWebcams(printerComm) {
  return new Promise((resolve, reject) => {
    printerComm.passThruToPrinter(
      {
        func: `server/webcams/list`,
        target: 'moonraker_api',
      },
      (err, ret) => {
        if (err || ret?.error) {
          reject(err || ret?.error)
        } else {
          resolve(ret?.webcams)
        }
      }
    )
  })
}

export function requestSnapshot(printerComm, url) {
  return new Promise((resolve, reject) => {
    printerComm.passThruToPrinter(
      {
        func: `web_snapshot_request`,
        target: 'jpeg_poster',
        args: [url],
      },
      (err, ret) => {
        if (err || ret?.error) {
          reject(err || ret?.error)
        } else {
          resolve(ret.pic)
        }
      }
    )
  })
}
