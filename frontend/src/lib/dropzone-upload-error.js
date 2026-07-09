import i18n from '@src/i18n/i18n.js'

const MAX_USER_MESSAGE_LENGTH = 500
const MAX_SENTRY_MESSAGE_LENGTH = 1000

const isObject = (value) => value && typeof value === 'object' && !Array.isArray(value)

const truncate = (value, maxLength = MAX_USER_MESSAGE_LENGTH) => {
  if (typeof value !== 'string') {
    return value
  }

  return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value
}

const normalizeWhitespace = (value) => value.replace(/\s+/g, ' ').trim()

const looksLikeHtml = (value) =>
  typeof value === 'string' &&
  /<!doctype html|<html[\s>]|<head[\s>]|<body[\s>]|<title[\s>]|<\/[a-z][^>]*>/i.test(value)

const decodeHtmlEntities = (value) => {
  if (typeof document !== 'undefined') {
    const textarea = document.createElement('textarea')
    textarea.innerHTML = value
    return textarea.value
  }

  return value
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
}

const stripHtml = (value) => {
  if (typeof value !== 'string') {
    return value
  }

  return normalizeWhitespace(decodeHtmlEntities(value.replace(/<[^>]*>/g, ' ')))
}

const extractHtmlTitle = (value) => {
  if (typeof value !== 'string') {
    return null
  }

  const title = value.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]
  return title ? stripHtml(title) : null
}

const getHeader = (xhr, name) => {
  if (!xhr || typeof xhr.getResponseHeader !== 'function') {
    return null
  }

  try {
    return xhr.getResponseHeader(name)
  } catch (_error) {
    return null
  }
}

const getResponseText = (xhr) => {
  if (!xhr) {
    return null
  }

  if (typeof xhr.responseText === 'string') {
    return xhr.responseText
  }

  if (typeof xhr.response === 'string') {
    return xhr.response
  }

  return null
}

const getStatus = (xhr) => {
  if (!xhr || typeof xhr.status !== 'number') {
    return null
  }

  return xhr.status
}

const parseJson = (value) => {
  if (typeof value !== 'string' || !value.trim()) {
    return null
  }

  try {
    return JSON.parse(value)
  } catch (_error) {
    return null
  }
}

const safeString = (value) => {
  if (typeof value === 'string') {
    return value
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  return null
}

const flattenApiErrors = (value) => {
  const directValue = safeString(value)
  if (directValue) {
    return [directValue]
  }

  if (Array.isArray(value)) {
    return value.flatMap((item) => flattenApiErrors(item))
  }

  if (isObject(value)) {
    if (value.error) {
      return flattenApiErrors(value.error)
    }
    if (value.detail) {
      return flattenApiErrors(value.detail)
    }

    return Object.values(value).flatMap((item) => flattenApiErrors(item))
  }

  return []
}

const sanitizeUserMessage = (value) => {
  if (!value || typeof value !== 'string') {
    return null
  }

  const message = looksLikeHtml(value) ? stripHtml(value) : normalizeWhitespace(value)
  return message ? truncate(message) : null
}

const userMessageFromApiBody = (body) => {
  const errors = flattenApiErrors(body)
    .map((error) => sanitizeUserMessage(error))
    .filter(Boolean)

  return errors.length ? errors.join(' ') : null
}

const defaultUploadErrorMessage = () => i18n.t('Upload failed. Please try again.')

const fallbackMessageForStatus = (status, defaultMessage) => {
  if (status === 0) {
    return i18n.t(
      'Upload failed because the connection was interrupted. Please check your network and try again.'
    )
  }

  if (status === 413) {
    return i18n.t('Upload failed because the file is larger than the upload limit.')
  }

  if (status >= 500) {
    return i18n.t(
      'Upload failed because the server temporarily could not complete the request. Please try again later.'
    )
  }

  return defaultMessage || defaultUploadErrorMessage()
}

export const normalizeDropzoneUploadError = (file, message, xhr, options = {}) => {
  const defaultMessage = options.defaultMessage || defaultUploadErrorMessage()
  const status = getStatus(xhr)
  const responseText = getResponseText(xhr)
  const contentType = getHeader(xhr, 'content-type') || getHeader(xhr, 'Content-Type')
  const jsonBody = parseJson(responseText)
  const htmlResponse =
    looksLikeHtml(responseText) || (contentType && /html/i.test(contentType))

  let userMessage = null
  if (jsonBody) {
    userMessage = userMessageFromApiBody(jsonBody)
  } else if (isObject(message)) {
    userMessage = userMessageFromApiBody(message)
  } else if (!htmlResponse) {
    userMessage = sanitizeUserMessage(safeString(message) || responseText)
  }

  if (!userMessage) {
    userMessage = fallbackMessageForStatus(status, defaultMessage)
  }

  if (!jsonBody && (status === 0 || status === 413 || status >= 500)) {
    userMessage = fallbackMessageForStatus(status, defaultMessage)
  }

  return {
    userMessage,
    status,
    contentType,
    isHtmlResponse: !!htmlResponse,
    responseTitle: extractHtmlTitle(responseText),
    responseSnippet: truncate(stripHtml(responseText || ''), MAX_SENTRY_MESSAGE_LENGTH),
    dropzoneMessage: truncate(
      sanitizeUserMessage(safeString(message)) || '',
      MAX_SENTRY_MESSAGE_LENGTH
    ),
    fileName: file?.name || null,
    fileSize: typeof file?.size === 'number' ? file.size : null,
  }
}

export const getDropzoneUploadErrorMessage = (file, message, xhr, options = {}) =>
  normalizeDropzoneUploadError(file, message, xhr, options).userMessage
