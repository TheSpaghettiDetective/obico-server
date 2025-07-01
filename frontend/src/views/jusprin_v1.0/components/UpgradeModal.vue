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
        <img src="/static/img/jusprin-credit.png" alt="JusPrin Credit Icon" class="d-inline-block align-middle mr-2" style="width: 2em; height: 2em;" />
        <h4 class="modal-section-title mb-4 d-inline-block align-middle">{{ $t("AI Credits") }}</h4>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: `${progressPercentage}%` }"></div>
        </div>
        <div class="progress-info">
          <span class="usage-text">{{ $t("You've used {used} AI Credits of {total} this month", { used: creditsUsed, total: credits.total }) }}</span>
          <span class="reset-date">{{ $t("Reset on {resetDate}", { resetDate: "July 1st" }) }}</span>
        </div>
      </div>

      <div class="text-muted small">
       {{ $t("\"AI credit\" is the currency for using JusPrin AI. Every time you can ask JusPrin to determine the best way to slice the model, you will use 1 AI credit.") }}
       <br>
       {{ $t("We set a limit on the number of AI Credits per month for free users because OpenAI charges us for each API call.") }}
      </div>

      <muted-alert class="mt-2 feature-notice">
        {{ $t("AI Credits limit is reset at the beginning of each month.") }}
      </muted-alert>

      <div class="body-section">
        <h4 class="modal-section-title">{{ $t("Get More AI Credits") }}</h4>
        <div class="section-description">{{ $t("If you are running short on AI Credits, there are two ways to get more.") }}</div>
        <div class="upgrade-option">
          <div class="upgrade-details">
            <div class="upgrade-title">
              {{ $t("Upgrade to Unlimited Plan") }}
            </div>
            <div class="text-muted small">{{ $t("Note: If your account is an Obico Pro account, you can a 30% discount on the upgrade.") }}</div>
          </div>
          <button class="btn btn-primary upgrade-button" @click="handleUpgrade">{{ $t("Upgrade") }}</button>
        </div>
        <div class="mt-4">
          <i18next :translation="$t('Alternatively, you can {hostYourOwnLink} and get unlimited AI Credits using your own OpenAI API key.')">
            <template #hostYourOwnLink>
              <a href="https://github.com/TheSpaghettiDetective/JusPrin" target="_blank">{{ $t("host your own JusPrin server") }}</a>
            </template>
          </i18next>
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
      color: var(--color-text-primary);
      padding: 0.25rem 0.75rem;
      border-radius: var(--border-radius-lg);
      border: 1px solid var(--color-divider);
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }
  }

  .body-section {
    margin-bottom: 1rem;

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

    .modal-section-title {
      color: var(--color-text-primary);
      font-size: 1.5rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      margin-top: 2rem;
      text-decoration: none;
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

      @media (max-width: 400px) {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
        padding: 0.875rem;
      }

      .upgrade-details {
        flex: 1;
        min-width: 0; // Allow text to wrap if needed

        // Prevent excessive shrinking on medium screens
        @media (min-width: 401px) {
          min-width: 200px;
        }

        .upgrade-title {
          color: var(--color-text-primary);
          font-size: 1.2rem;
          font-weight: 500;
          margin-bottom: 0.25rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;

          .discount {
            background-color: var(--color-primary);
            color: var(--color-on-primary);
            padding: 0.125rem 0.5rem;
            border-radius: var(--border-radius-lg);
            font-size: 0.75rem;
            font-weight: 600;
          }
        }
      }

      .upgrade-button {
        padding: 0.75rem 2rem;
        font-size: 0.875rem;
        font-weight: 600;
        white-space: nowrap;
        flex-shrink: 0; // Prevent button from shrinking

        @media (max-width: 400px) {
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