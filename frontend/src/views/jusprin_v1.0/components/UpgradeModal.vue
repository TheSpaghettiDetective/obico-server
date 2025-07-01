<template>
  <div v-if="show" class="upgrade-modal-backdrop" @click="closeModal">
    <div class="upgrade-modal surface" @click.stop>
      <button class="close-button icon-btn" @click="closeModal">
        <i class="mdi mdi-close"></i>
      </button>

      <h2 class="modal-title">{{ $t("Your JusPrin Account") }}</h2>

      <div class="user-info">
        <div class="user-details">
          <h3 class="user-name">{{ userInfo.name }}</h3>
          <div class="user-email">{{ userInfo.email }}</div>
        </div>
        <span class="plan-badge">{{ $t("FREE Plan") }}</span>
      </div>

      <div class="body-section">
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: `${progressPercentage}%` }"></div>
        </div>
        <div class="progress-info">
          <span class="usage-text">{{ $t("You've used {used} AI Asks of {total} this month", { used: creditsUsed, total: credits.total }) }}</span>
          <span class="reset-date">{{ $t("Reset on {resetDate}", { resetDate: "July 1st" }) }}</span>
        </div>
      </div>

      <muted-alert class="feature-notice">
        {{ $t("AI Asks are the number of times you can ask JusPrin to determine the best way to slice the model. We set a limit on the number of AI Asks per month for free users because OpenAI charges us for each API call. The limit is reset at the beginning of each month.") }}
      </muted-alert>

      <div class="body-section">
        <h4 class="section-title">{{ $t("Get More AI Asks") }}</h4>
        <div class="section-description">{{ $t("If you are running short on AI asks, there are two ways to get more.") }}</div>
        <div class="upgrade-option">
          <div class="upgrade-details">
            <div class="upgrade-title">
              {{ $t("Upgrade to Pro") }}
              <span class="discount">{{ $t("-{percent}%", { percent: 25 }) }}</span>
            </div>
            <div class="upgrade-description">{{ $t("Unlock features and earn {credits} credits", { credits: 1200 }) }}</div>
          </div>
          <button class="btn btn-primary upgrade-button" @click="handleUpgrade">{{ $t("Upgrade") }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MutedAlert from '@src/components/MutedAlert.vue'

export default {
  name: 'UpgradeModal',
  components: {
    MutedAlert,
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    userInfo: {
      type: Object,
      default: () => ({
        name: 'Kenneth Jiang',
        email: 'kenneth.jiang@gmail.com'
      })
    },
    credits: {
      type: Object,
      default: () => ({
        available: 90,
        total: 90,
        purchased: 0
      })
    }
  },
  computed: {
    creditsUsed() {
      return this.credits.total - this.credits.available
    },
    progressPercentage() {
      return ((this.credits.total - this.credits.available) / this.credits.total) * 100
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
    },
    handleUpgrade() {
      this.$emit('upgrade')
    }
  }
}
</script>

<style lang="scss" scoped>
@import '../../../styles/theme';
@import '../../../styles/mixin';

// Upgrade Modal Styles
.upgrade-modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--color-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.upgrade-modal {
  background-color: var(--color-surface-secondary);
  border-radius: var(--border-radius-lg);
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: var(--shadow-top-nav);

  @include respond-below(md) {
    padding: 1.5rem;
    margin: 0 1rem;
    width: calc(100% - 2rem);
  }

  .close-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;

    &:hover, &:focus {
      background-color: var(--color-hover) !important;
      color: var(--color-text-primary) !important;
    }
  }

  .modal-title {
    color: var(--color-text-primary);
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 1.5rem 0;
    text-align: center;

    @include respond-below(md) {
      font-size: 1.25rem;
      margin-bottom: 1rem;
    }
  }

  .user-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

    @media (max-width: 400px) {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .user-details {
      .user-name {
        color: var(--color-text-primary);
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;

        @include respond-below(md) {
          font-size: 1.125rem;
        }
      }

      .user-email {
        color: var(--color-text-secondary);
        font-size: 0.875rem;
        text-decoration: underline;
      }
    }

    .plan-badge {
      background-color: var(--color-primary);
      color: var(--color-on-primary);
      padding: 0.25rem 0.75rem;
      border-radius: var(--border-radius-lg);
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }
  }

  .body-section {
    margin-bottom: 2rem;

    @include respond-below(md) {
      margin-bottom: 1.5rem;
    }

    .ai-asks-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;

      .ai-asks-icon {
        background-color: var(--color-primary);
        color: var(--color-on-primary);
        border-radius: 50%;
        width: 1.5rem;
        height: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.875rem;
      }

      .ai-asks-title {
        color: var(--color-text-primary);
        font-size: 1.125rem;
        font-weight: 600;
      }
    }

    .progress-bar-container {
      width: 100%;
      height: 8px;
      background-color: var(--color-surface-primary);
      border-radius: var(--border-radius-xs);
      overflow: hidden;
      border: 1px solid var(--color-divider-muted);

      .progress-bar {
        height: 100%;
        background-color: var(--color-primary);
        border-radius: var(--border-radius-xs);
        transition: width 0.3s ease;
      }
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 0.5rem;
      gap: 1rem;

      @media (max-width: 400px) {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
      }

      .usage-text {
        color: var(--color-text-primary);
        font-size: 0.875rem;
        font-weight: 500;
        flex: 1;
        min-width: 0;
      }

      .reset-date {
        color: var(--color-text-secondary);
        font-size: 0.75rem;
        font-weight: 400;
        flex-shrink: 0;
        white-space: nowrap;
      }
    }

    .section-title {
      color: var(--color-text-primary);
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      margin-top: 2rem;
    }

    .section-description {
      color: var(--color-text-secondary);
      font-size: 0.875rem;
      margin-bottom: 1rem;
    }

    .upgrade-option {
      border: 1px solid var(--color-divider);
      border-radius: var(--border-radius-md);
      padding: 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;

      @include respond-below(md) {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
        padding: 0.875rem;
      }

      .upgrade-details {
        flex: 1;

        .upgrade-title {
          color: var(--color-text-primary);
          font-size: 1rem;
          font-weight: 500;
          margin-bottom: 0.25rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;

          @include respond-below(md) {
            flex-wrap: wrap;
          }

          .discount {
            background-color: var(--color-primary);
            color: var(--color-on-primary);
            padding: 0.125rem 0.5rem;
            border-radius: var(--border-radius-lg);
            font-size: 0.75rem;
            font-weight: 600;
          }
        }

        .upgrade-description {
          color: var(--color-text-secondary);
          font-size: 0.875rem;
        }
      }

      .upgrade-button {
        padding: 0.75rem 2rem;
        font-size: 0.875rem;
        font-weight: 600;
        white-space: nowrap;

        @include respond-below(md) {
          width: 100%;
          white-space: normal;
        }

        &:hover {
          background-color: var(--color-primary-hover);
        }
      }
    }
  }
}
</style>