---
id: move-from-tsd-to-obico-in-octoprint
title: Move from The Spaghetti Detective to Obico in OctoPrint
---

If you are already using the *"Access Anywhere - The Spaghetti Detective"* plugin in OctoPrint, you are in luck. We have made it very easy for you to move to Obico.

## Migrate to *Obico for OctoPrint* plugin in 3 easy steps {#migrate-to-obico-for-octoprint-plugin-in-3-easy-steps}

### Step 1. Uninstall the *Access Anywhere - The Spaghetti Detective"* plugin but keep the data {#step-1-uninstall-the-access-anywhere---the-spaghetti-detective-plugin-but-keep-the-data}

1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. Scroll down the navigation bar on the left side.
1. Click "Plugin Manager" tab.
1. Click the trash can icon (**🗑️**) next to "Access Anywhere - The Spaghetti Detective".
1. Click the "Uninstall" (**NOT "Uninstall & clean up data"**) button.

:::caution
Do NOT click the "Uninstall & clean up data" button. Otherwise it'll take quite a few more steps to migrate to Obico.
:::

![](/img/user-guides/obico-migration/tsd-octoprint-plugin-delete-button.jpg)

![](/img/user-guides/obico-migration/delete-tsd-plugin-keep-data.jpg)


:::info
Alternatively, you can just disable *Access Anywhere - The Spaghetti Detective"* plugin. However, it's highly recommended that you remove the plugin.
:::

### Step 2. Install the *Obico for OctoPrint* plugin {#step-2-install-the-obico-for-octoprint-plugin}

1. Open OctoPrint page in a browser.
1. Open OctoPrint settings page by clicking the wrench icon (**🔧**).
1. On the settings page, click "**Plugin Manager**", then "**Get More...**".
1. Type "Obico" in the box, you will see "Obico for OctoPrint" plugin.
1. Click "**Install**".
1. Click "**Restart Now**" when OctoPrint asks.

![Install the Plugin](/img/user-guides/setupguide/install-plugin.png)

Once OctoPrint has restarted, you will see dialog that pops up like this:

![](/img/user-guides/obico-migration/migration-success.jpg)

### Step 3. Login to the Obico app {#step-3-login-to-the-obico-app}

Login to [the Obico web app](https://app.obico.io) or the mobile app using your previous The Spaghetti Detective account credential to verify everything works.

## Frequently asked questions {#frequently-asked-questions}

### I already have a The Spaghetti Detective account. But I didn't see the dialog after I installed the Obico plugin and restarted OctoPrint. What do I do now? {#i-already-have-a-the-spaghetti-detective-account-but-i-didnt-see-the-dialog-after-i-installed-the-obico-plugin-and-restarted-octoprint-what-do-i-do-now}

You will need to manually link your OctoPrint to your Obico account.

1. Go to the Obico plugin settings page.
2. Depending on what you see, you will need to either the **Run Setup Wizard to Link OctoPrint** button, or the ** Re-run Wizard** button.

<img src="/img/user-guides/obico-migration/settings-run-setup-wizard.png" style={{maxWidth: "450px"}} alt=""></img>
<img src="/img/user-guides/obico-migration/settings-rerun-setup-wizard.jpg" style={{maxWidth: "450px"}} alt=""></img>

3. Follow <a href="https://www.obico.io/docs/user-guides/octoprint-plugin-setup-manual-link/">this guide</a> to link OctoPrint to your Obico account.

### I got the error <span className="text--danger">"The Obico plugin failed to start because "Access Anywhere - The Spaghetti Detective" plugin is still installed and enabled"</span> {#i-got-the-error-span-classnametext--dangerthe-obico-plugin-failed-to-start-because-access-anywhere---the-spaghetti-detective-plugin-is-still-installed-and-enabledspan}

This means somehow you missed [this migration step](#step-1-uninstall-the-access-anywhere---the-spaghetti-detective-plugin-but-keep-the-data).

Please uninstall or disable the "Access Anywhere - The Spaghetti Detective" plugin. Once you have done so and **restarted OctoPrint**, the Obico plugin should work correctly.

### I can't login Obico with my previous The Spaghetti Detective account credential. {#i-cant-login-obico-with-my-previous-the-spaghetti-detective-account-credential}

More likely than not, you just simply forgot your password or your account email.

If you forgot your password, click the "Forgot Password?" link on the login page to reset your password.

If you are not sure if you are using the correct email, you can also try to [sign up for a new Obico account](https://app.obico.io/accounts/signup/) with that email. The sign up page will tell you so if there has been an account with that email.

If everything fails, please reach out to [the Obico team](mailto:support@obico.io) for help.