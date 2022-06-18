const ACTIVE_SESSION_LENGTH = 30;
const FROZEN_SESSION_LENGTH = 30;

const STREAM_CYCLE_LENGTH = ACTIVE_SESSION_LENGTH + FROZEN_SESSION_LENGTH;

const STREAM_SESSION = {
  Active: 'Active',
  Frozen: 'Frozen',
  Idle: 'Idle',
};

const STREAM_EVENT = {
  FrozenSessionStarted: 'FrozenSessionStarted',
  CycleFinished: 'CycleFinished',
};

const STORAGE_ITEM_PREFIX = 'tsNextVideoCycle';

class StreamThrottle {
  constructor(printerId, storageProvider, isStorageAsync = false) {
    this.storageItemId = `${STORAGE_ITEM_PREFIX}-${printerId}`;
    this.storageProvider = storageProvider;
    this.isStorageAsync = isStorageAsync;
  }

  restoreRemainingSeconds() {
    if (!this.storageProvider) {
      return STREAM_CYCLE_LENGTH;
    }

    return this._calcRemainingSeconds(this.storageProvider.getItem(this.storageItemId));
  }

  async restoreRemainingSecondsAsync() {
    if (!this.storageProvider) {
      return STREAM_CYCLE_LENGTH;
    }

    const val = await this.storageProvider.getItem(this.storageItemId);
    return this._calcRemainingSeconds(val);
  }

  _calcRemainingSeconds(val) {
    const tsNextVideoCycle = parseFloat(val);
    const now = (new Date().getTime()) / 1000;
    if (!tsNextVideoCycle || now > tsNextVideoCycle) {
      return STREAM_CYCLE_LENGTH;
    } else {
      return Math.round((tsNextVideoCycle - now));
    }
  }

  saveToStorage(remainingSeconds) {
    if (!this.storageProvider) {
      return;
    }
    const now = (new Date().getTime()) / 1000;
    this.storageProvider.setItem(this.storageItemId, String(now + remainingSeconds));
  }

  removeFromStorage() {
    if (!this.storageProvider) {
      return;
    }
    this.storageProvider.removeItem(this.storageItemId);
  }

  static currentSession(remainingSeconds) {
    if (remainingSeconds >= STREAM_CYCLE_LENGTH || remainingSeconds <= 0) {
      return STREAM_SESSION.Idle;
    } else if (remainingSeconds < STREAM_CYCLE_LENGTH && remainingSeconds > FROZEN_SESSION_LENGTH) {
      return STREAM_SESSION.Active;
    } else {
      return STREAM_SESSION.Frozen;
    }
  }

  static calculateSessionsSeconds(remainingSeconds = STREAM_CYCLE_LENGTH) {
    const active = remainingSeconds - FROZEN_SESSION_LENGTH;
    const frozen = remainingSeconds > FROZEN_SESSION_LENGTH ? -1 : remainingSeconds;
    return [active, frozen];
  }

  static whatHappened(remainingSeconds) {
    if (remainingSeconds <= 0) {
      return STREAM_EVENT.CycleFinished;
    } else if (remainingSeconds === FROZEN_SESSION_LENGTH) {
      return STREAM_EVENT.FrozenSessionStarted;
    } else {
      return null;
    }
  }

  static defaultRemainingSeconds() {
    return STREAM_CYCLE_LENGTH;
  }
}

export {
  ACTIVE_SESSION_LENGTH,
  FROZEN_SESSION_LENGTH,
  STREAM_SESSION,
  STREAM_EVENT,
  StreamThrottle,
};
