import { toMomentOrNull } from '@src/lib/normalizers'
import filesize from 'filesize'
import _ from 'lodash'

export const listFiles = (printerComm, options) => {
  const { query, path, onRequestEnd, isAgentMoonraker = false } = options

  if (isAgentMoonraker) {
    printerComm.passThruToPrinter(
      {
        target: 'moonraker_api',
        func: 'server/files/directory',
        kwargs: {
          path,
          extended: true,
        },
      },
      (err, ret) => {
        if (err) {
          onRequestEnd()
        } else if (ret) {
          // subdirs should be ignored when user is searching
          const dirsInServerFormat = query
            ? []
            : _.map(
                _.filter(
                  _.get(ret, 'dirs', []),
                  (d) => !d.dirname.startsWith('.') && !d.dirname.startsWith('Obico_Upload')
                ),
                (d) => {
                  return {
                    name: d.dirname,
                    path: `${path}/${d.dirname}`,
                    children: [], // To signify this is a folder, not a file
                  }
                }
              )

          const filesInServerFormat = _.map(
            _.filter(
              _.get(ret, 'files', []),
              (f) =>
                !f.filename.startsWith('.') &&
                (!query || f.filename.toLowerCase().includes(query.toLowerCase()))
            ),
            (f) => {
              return {
                ...f,
                num_bytes: f.size,
                created_at: new Date(f.modified * 1000),
                path: `${path}/${f.filename}`,
              }
            }
          )

          dirsInServerFormat.concat(filesInServerFormat)

          onRequestEnd({ folders: dirsInServerFormat, files: filesInServerFormat })
        }
      }
    )
  } else {
    printerComm.passThruToPrinter(
      {
        func: 'list_files',
        target: '_file_manager',
        kwargs: query
          ? {
              filter: String(query),
              recursive: true,
            }
          : {
              path,
              recursive: false,
              level: 1,
            },
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

          const items = query ? listRecoursively(ret.local) : Object.values(ret.local)
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
