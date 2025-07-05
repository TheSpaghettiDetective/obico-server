<template>
  <div v-if="show" class="upgrade-modal-backdrop" @click="closeModal">
    <div class="upgrade-modal surface" @click.stop>
      <button class="close-button icon-btn" @click="closeModal">
        <i class="mdi mdi-close"></i>
      </button>

      <h2 class="modal-title">{{ $t("Your JusPrin Account") }}</h2>

      <!-- Red banner for zero credits -->
      <div v-if="!loading && !isUnlimitedPlan && remainingCredits <= 0" class="credit-exhausted-banner">
        <i class="mdi mdi-alert-circle"></i>
        <span>{{ $t("You have run out of AI credits!") }}</span>
      </div>

      <div v-if="loading" class="text-center">
        <i class="mdi mdi-loading mdi-spin"></i> {{ $t("Loading...") }}
      </div>

      <div v-else>
        <div class="user-info">
          <div class="user-details">
            <h3 v-if="userInfo.first_name || userInfo.last_name" class="user-name">{{ userDisplayName }}</h3>
            <div class="user-email">{{ userInfo.email }}</div>
          </div>
          <span class="plan-badge" :class="{ 'pro-badge': isUnlimitedPlan }">
            {{ isUnlimitedPlan ? $t('Unlimited') : $t('FREE Plan') }}
          </span>
        </div>

        <template v-if="isUnlimitedPlan">
          <div class="body-section text-center">
            <div class="celebration" style="font-size: 2.5rem; margin: 1.5rem 0;">
              🎉 <i class="mdi mdi-crown" style="color: gold; font-size: 2.5rem;"></i> 🎉
            </div>
            <div class="unlimited-text" style="font-size: 1.2rem; font-weight: bold;">
              {{ $t('Yay! You are on the Unlimited Plan!') }}
            </div>
            <div class="unlimited-text" style="font-size: 1.2rem; font-weight: bold; margin-bottom: 3rem;">
              {{ $t('Enjoy unlimited AI credits!') }}
            </div>
            <a
              href="/ent/jusprin/pricing/?can_go_back_to_chat=1"
              class="btn btn-primary upgrade-button"
            >
              {{ $t('Manage Subscription Plan') }}
            </a>
          </div>
        </template>
        <template v-else>
          <div class="body-section">
            <div class="ai-credits-header">
              <img src="/static/img/jusprin-credit.png" alt="JusPrin Credit Icon" class="credit-icon" />
              <h4 class="modal-section-title">{{ $t("AI Credits") }}</h4>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar" :class="creditStatusClass" :style="{ width: `${progressPercentage}%` }"></div>
            </div>
            <div class="progress-info">
              <span class="usage-text">
                You've used {{ credits.ai_credit_used_current_month }} AI credits of {{ isUnlimitedPlan ? 'unlimited' : credits.ai_credit_free_monthly_quota }} this month
              </span>
              <span class="reset-date">{{ $t("Reset on {resetDate}", { resetDate: nextMonthResetDate }) }}</span>
            </div>
          </div>

          <div class="text-muted small">
           {{ $t("\"AI credit\" is the currency for using JusPrin AI. Every time you ask JusPrin to determine the best way to slice the model, you will use 1 AI credit.") }}
           <br>
           {{ $t("We set a limit on the number of AI credits per month for free users because OpenAI charges us for each API call.") }}
          </div>

          <muted-alert class="mt-2 feature-notice">
            {{ $t("AI credit limit is reset at the beginning of each month.") }}
          </muted-alert>

          <div class="body-section">
            <h4 class="modal-section-title">{{ $t("Get More AI Credits") }}</h4>
            <div class="section-description">{{ $t("If you are running short on AI credits, there are two ways to get more.") }}</div>
            <div class="upgrade-option">
              <div class="upgrade-details">
                <div class="upgrade-title">
                  {{ $t("Upgrade to Unlimited Plan") }}
                  <span v-if="userInfo.has_active_subscription" class="discount">{{ $t("30% OFF") }}</span>
                </div>
                <div class="text-primary small">{{ $t("If your account is an Obico Pro account, you can get a 30% discount on the upgrade. Discount automatically applied at checkout.") }}</div>
              </div>
              <a
                href="/ent/jusprin/pricing/?can_go_back_to_chat=1"
                class="btn btn-primary upgrade-button"
              >
                {{ $t('Upgrade') }}
              </a>
            </div>
            <div class="mt-4">
              <i18next :translation="$t('Alternatively, you can {hostYourOwnLink} and get unlimited AI credits using your own OpenAI API key.')">
                <template #hostYourOwnLink>
                  <a href="https://github.com/TheSpaghettiDetective/obico-server/blob/release/README_jusprin_server.md">{{ $t("host your own JusPrin server") }}</a>
                </template>
              </i18next>
            </div>
          </div>
        </template>

        <div class="body-section" v-else>
          <h4 class="modal-section-title">{{ $t("Your Active Subscription") }}</h4>
          <div class="subscription-info">
            <div class="subscription-details">
              <div class="subscription-plan">
                <i class="mdi mdi-crown"></i>
                {{ $t("You have an active {plan} subscription", { plan: userInfo.subscription_plan || 'Pro' }) }}
              </div>
              <div class="text-muted small">{{ $t("Your subscription gives you access to enhanced features and higher AI credit limits.") }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MutedAlert from '@src/components/MutedAlert.vue'
import api from '../lib/api'
import urls from '@config/server-urls'

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
    oauthAccessToken: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      loading: false,
      userInfo: null,
      credits: null,
      error: null
    }
  },
  computed: {
    progressPercentage() {
      if (!this.credits || this.credits.ai_credit_free_monthly_quota === -1) return 100
      if (this.credits.ai_credit_free_monthly_quota === 0) return 0
      return Math.min(100, (this.credits.ai_credit_used_current_month / this.credits.ai_credit_free_monthly_quota) * 100)
    },
    isUnlimitedPlan() {
      return this.credits?.ai_credit_free_monthly_quota === -1
    },
    remainingCredits() {
      if (!this.credits || this.credits.ai_credit_free_monthly_quota <= 0) {
        return 0
      }
      return Math.max(0, this.credits.ai_credit_free_monthly_quota - (this.credits.ai_credit_used_current_month || 0))
    },
    creditStatusClass() {
      if (!this.credits || this.credits.ai_credit_free_monthly_quota <= 0) {
        return ''
      }
      const remaining = this.remainingCredits
      const total = this.credits.ai_credit_free_monthly_quota
      const ratio = total === 0 ? 0 : remaining / total
      if (remaining === 0) {
        return 'credit-exhausted'
      } else if (ratio < 1/3) {
        return 'credit-warning'
      } else {
        return 'credit-success'
      }
    },
    userDisplayName() {
      if (!this.userInfo) return ''
      return `${this.userInfo.first_name || ''} ${this.userInfo.last_name || ''}`.trim()
    },
    nextMonthResetDate() {
      const now = new Date()
      const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1)
      return nextMonth.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    }
  },
  watch: {
    show(newValue) {
      if (newValue) {
        this.fetchAICreditsData()
      }
    }
  },
  mounted() {
    if (this.show) {
      this.fetchAICreditsData()
    }
  },
  methods: {
    async fetchAICreditsData() {
      if (!this.oauthAccessToken) {
        return
      }
      this.loading = true
      this.error = null
      const response = await api.get(urls.jusprinMe(), this.oauthAccessToken)
      if (response.data) {
        this.userInfo = response.data.user
        this.credits = response.data.ai_credits
      }
      this.loading = false
    },
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>

<style lang="scss" scoped>
@import '../../../../styles/theme';
@import '../../../../styles/mixin';

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
      border-radius: var(--border-radius-sm);
      border: 1px dashed var(--color-divider);
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;

      &.pro-badge {
        color: var(--color-primary);
        border: 1px dashed var(--color-primary);
      }
    }
  }

  .body-section {
    margin-bottom: 1rem;

    @include respond-below(md) {
      margin-bottom: 1.5rem;
    }

    .ai-credits-header {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      margin-bottom: 1rem;

      .credit-icon {
        width: 1.5rem;
        height: 1.5rem;
        flex-shrink: 0;
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

        &.credit-success {
          background-color: var(--color-success);
        }

        &.credit-warning {
          background-color: var(--color-warning);
        }

        &.credit-exhausted {
          background-color: var(--color-danger);
        }
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
        min-width: 0;

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
        flex-shrink: 0;

        @media (max-width: 400px) {
          width: 100%;
          white-space: normal;
        }

        &:hover {
          background-color: var(--color-primary-hover);
        }
      }
    }

    .subscription-info {
      border: 1px solid var(--color-primary);
      border-radius: var(--border-radius-md);
      padding: 1rem;
      background-color: var(--color-surface-primary);

      .subscription-details {
        .subscription-plan {
          color: var(--color-primary);
          font-size: 1.1rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;

          i {
            color: var(--color-primary);
          }
        }
      }
    }
  }

  .credit-exhausted-banner {
    background-color: var(--color-danger);
    color: white;
    padding: 1rem;
    border-radius: var(--border-radius-md);
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 700;
    font-size: 1rem;
    text-align: center;
    justify-content: center;
    border: 2px solid var(--color-danger);
    animation: pulse-danger 2s ease-in-out infinite;

    i {
      font-size: 1.25rem;
      flex-shrink: 0;
    }

    span {
      font-weight: 700;
    }

    @media (max-width: 400px) {
      font-size: 0.875rem;
      padding: 0.875rem;
      margin-bottom: 1rem;
    }
  }

  @keyframes pulse-danger {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(var(--color-danger-rgb, 220, 53, 69), 0.4);
    }
    50% {
      box-shadow: 0 0 0 8px rgba(var(--color-danger-rgb, 220, 53, 69), 0);
    }
  }
}
</style>