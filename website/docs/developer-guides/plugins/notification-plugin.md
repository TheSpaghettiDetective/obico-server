---
id: notification-plugin
title: Notification plugin
---

You may be interested in getting a notification when certain printer events happen, such as when a print is done, or a possible print failure is detected. But different people have their own preferred way to get notified: Email, Mobile Push Notification, Telegram, Discord, etc.

This is why we created the notification plugin structure in the Obico Server. It allows these events to be sent to almost any channel you prefer. The Obico Server is shipped with quite a few built-in notification channels. But if your preferred channel is not there, you can always build one.

:::info
Following [this tutorial](/docs/tutorials/pushover-notification-plugin) is the quickest way to have a new notification plugin up and running in your self-hosted Obico Server.
:::

## The structure of a notification plugin {#the-structure-of-a-notification-plugin}

A notification plugin consists of 3 parts. 2 are required and 1 optional.

- **[The backend](#the-plugin-backend) (required).** The backend is written in python. The Obico Server will call the backend when a printer event happens. The backend will then send a notification for this event, or simply ignore it.
- **[The frontend for the plugin preference page](#the-plugin-frontend) (required).** The frontend is written in Vue.js. It will become a section on the user preference page. The frontend is responsible for taking user's input. For instance, a Telegram plugin will need the user to authorize it to send notifications to the user's telegram account. Hence a Telegram plugin's frontend will need to show a "Link Telegram" button to the user.
- **[The environment variables](#the-environment-variables) (optional).** Some notification plugins will need some server-side configuration. For instance, a Pushover plugin will need an *Pushover App Token* in order to send a notification through the Pushover server. These configurations are done via *the environment variables*. Some notification plugins, such as the Discord plugin, don't need any server-side configurations. Hence this part is optional.

A notification plugin should also have a unique ID so that the Obico Server can tell it apart from other plugins. In this document, this ID will be represented as `\{plugin_id\}`.

## The plugin backend {#the-plugin-backend}

### Directory structure {#directory-structure}

All plugin backend files should be located in the folder `backend/notifications/plugins/\{plugin_id\}`.

#### `backend/notifications/plugins/\{plugin_id\}/__init__.py` {#backendnotificationspluginsplugin_id__init__py}

Required. This is the entry point for the plugin backend.

#### Other python files in `backend/notifications/plugins/\{plugin_id\}/` {#other-python-files-in-backendnotificationspluginsplugin_id}

Optional. If present, they must be imported in the `__init__.py`. Otherwise they won't be loaded successfully.

### Class `BaseNotificationPlugin` {#class-basenotificationplugin}

The base class from which the plugin backend needs to extend from.

Example:

```python
from notifications.plugin import BaseNotificationPlugin

class PushOverNotificationPlugin(BaseNotificationPlugin):
    ...
```

`BaseNotificationPlugin` defines the following methods that can be overridden by the plugin class. Most of them have a reasonable default and hence they are not optional in the plugin class.


#### `validate_config` {#validate_config}

Validate the form data submitted by the user from the plugin's preference page.

This method is optional if your plugin doesn't need any configuration. This is rare.

##### Signature {#signature}

    def validate_config(self, data: Dict) -> Dict:

##### Parameters {#parameters}

- `data`: A `Dict` that contains the form data submitted by the user from the plugin's preference page. For instance, the Pushover plugin's preference page asks the user for a *user_key*. In this case, `data` will look like `{'user_key': 'xxx-xxxx-xxxxx'}`.

##### Return value {#return-value}

- A `Dict`: The form data that has been cleaned up. For instance, you may want to trim the leading/trailing white spaces. The return value will be saved to the database. It will be retrieved from the database and passed to the plugin when a notification needs to be sent.

:::info
The Obico Server has already sanitized the form data against common attacks before passing it to this method.
:::

##### Exceptions {#exceptions}

- `rest_framework.serializers.ValidationError`: Throw this exception if `data` failed in validation.


#### `env_vars` {#env_vars}

The method that tells the Obico Server what environment variables this plugin needs.

This method is optional if your plugin doesn't require any environment variables.

##### Signature {#signature-1}

    def env_vars(self) -> Dict:

##### Parameters {#parameters-1}

- None.

##### Return value {#return-value-1}

- A `Dict`. This return value will also be passed to the plugin frontend in case the frontend needs some of them on the preference page.

Example:

```python
    def env_vars(self) -> Dict:
        return \{
            'SLACK_CLIENT_ID': \{
                'is_required': True,
                'is_set': 'SLACK_CLIENT_ID' in os.environ,
                'value': os.environ.get('SLACK_CLIENT_ID'),
            \},
            'SLACK_CLIENT_SECRET': \{
                'is_required': True,
                'is_set': 'SLACK_CLIENT_SECRET' in os.environ,
            \},
        \}
```


:::danger
Never return the value of an environment variable that is supposed to be kept secret, such as `SLACK_CLIENT_SECRET`. Whatever returned from this call will be exposed to the app users.
:::

##### Exceptions {#exceptions-1}

- None.


#### `supported_features` {#supported_features}

The method that tells the Obico Server what features this plugin supports.

This method is optional if your plugin supports all features.

##### Signature {#signature-2}

    def supported_features(self) -> Set[Feature]:

##### Parameters {#parameters-2}

- None.


##### Return value {#return-value-2}

- A `Set` of [`Feature`](#class-feature)s.

##### Exceptions {#exceptions-2}

- None.


#### `send_failure_alert` {#send_failure_alert}

The method the Obico Server will call when a possible failure is detected.

This method is optional if your plugin doesn't support the `Feature.notify_on_failure_alert` feature.

##### Signature {#signature-3}

    def send_failure_alert(self, context: FailureAlertContext) -> None:

##### Parameters {#parameters-3}

- `context`: A [`FailureAlertContext`](#class-failurealertcontext) that contains the data for the detected failure.


##### Return value {#return-value-3}

- None.

##### Exceptions {#exceptions-3}

- None.


#### `send_printer_notification` {#send_printer_notification}

The method the Obico Server will call when a printer notification needs to be sent, in general but not always when a printer event happens.

This method is optional if your plugin doesn't support **any** of the following features.

- notify_on_print_done
- notify_on_print_cancelled
- notify_on_filament_change
- notify_on_heater_status
- notify_on_print_start
- notify_on_print_pause
- notify_on_print_resume

##### Signature {#signature-4}

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:

##### Parameters {#parameters-4}

- `context`: A [`PrinterNotificationContext`](#class-printernotificationcontext) that contains the data for the notification


##### Return value {#return-value-4}

- None.

##### Exceptions {#exceptions-4}

- None.


#### `send_test_message` {#send_test_message}

The method the Obico Server will call when the user press the "Test notification" button on the plugin's preference page.

##### Signature {#signature-5}

    def send_test_message(self, context: TestMessageContext) -> None:

##### Parameters {#parameters-5}

- `context`: A [`TestMessageContext`](#class-testmessagecontext) that contains the data for the test notification.


##### Return value {#return-value-5}

- None.

##### Exceptions {#exceptions-5}

- None.


### Class `FailureAlertContext` {#class-failurealertcontext}

#### Properties {#properties}

- `config`: `Dict`. The same as what was previously returned from [`validate_config`](#validate_config) and saved in the database.
- `user`: [`UserContext`](#class-usercontext).
- `printer`: [`PrinterContext`](#class-printercontext).
- `print`: [`PrintContext`](#class-printcontext).
- `extra_context`: `Dict`. Reserved for internal use.
- `img_url`: `str`. The url for the webcam image. If no webcam image is available, this will be an empty string (not `None`).
- `is_warning`: `bool`. If the detected failure is a "warning".
- `print_paused`: `bool`. If the print was paused as the result of the detected failure.


### Class `PrinterNotificationContext` {#class-printernotificationcontext}

#### Properties {#properties-1}

- `config`: `Dict`. The same as what was previously returned from [`validate_config`](#validate_config) and saved in the database.
- `user`: [`UserContext`](#class-usercontext).
- `printer`: [`PrinterContext`](#class-printercontext).
- `print`: [`PrintContext`](#class-printcontext).
- `extra_context`: `Dict`. Reserved for internal use.
- `img_url`: `str`. The url for the webcam image. If no webcam image is available, this will be an empty string (not `None`).
- `feature`: [`Feature`](#class-feature).
- `notification_type`: [`str`](#module-notification_types). The type of this notification.


### Class `UserContext` {#class-usercontext}

#### Properties {#properties-2}

- `id`: `int`
- `email`: `str`
- `first_name`: `str`
- `last_name`: `str`
- `unsub_token`: `str`
- `dh_balance`: `float`
- `is_pro`: `bool`


### Class `PrinterContext` {#class-printercontext}

#### Properties {#properties-3}

- `id`: `int`
- `name`: `str`
- `pause_on_failure`: `bool`
- `watching_enabled`: `bool`


### Class `PrintContext` {#class-printcontext}

#### Properties {#properties-4}

- `id`: `int`
- `filename`: `str`
- `started_at`: `Optional[datetime.datetime]`
- `ended_at`: `Optional[datetime.datetime]`
- `alerted_at`: `Optional[datetime.datetime]`
- `alert_overwrite`: `str`


### Class `TestMessageContext` {#class-testmessagecontext}

#### Properties {#properties-5}

- `config`: `Dict`
- `user`: `UserContext`
- `extra_context`: `Dict`


### Class `Feature` {#class-feature}

An Enum that tells what feature(s) a plugin supports.

When a feature is declared supported by a plugin, a toggle will be shown on its preference page so that the user can toggle on/off that feature. Also the Obico Server will try to call a corresponding method of that plugin when there is a notification classified under that feature.

#### List of `Feature`s {#list-of-features}

- `notify_on_failure_alert`
- `notify_on_print_done`
- `notify_on_print_cancelled`
- `notify_on_filament_change`
- `notify_on_print_start`
- `notify_on_print_pause`
- `notify_on_print_resume`
- `notify_on_heater_status`

### module `notification_types` {#module-notification_types}

Example:

    from notifications import notification_types
    ...


#### list of `notification_types` {#list-of-notification_types}

- `PrintStarted`
- `PrintDone`
- `PrintCancelled`
- `PrintPaused`
- `PrintResumed`
- `FilamentChange`
- `HeaterCooledDown`
- `HeaterTargetReached`


## The plugin frontend {#the-plugin-frontend}

### Directory structure {#directory-structure-1}

All plugin frontend files should be located in the folder `frontend/src/notifications/`.

#### `backend/notifications/plugins/{plugin_id}.vue` {#backendnotificationspluginsplugin_idvue}

Required. The Vue component that will be shown to the user. It should contain the following:

- A form input to let the user enter [the config data](#validate_config) necessary to receive a notification. For instance, this is how the Pushover plugin lets the user enter a *user_key*:

```
    ...
    <notification-channel-template
        :errorMessages="errorMessages"
        :saving="saving"
        :notificationChannel="notificationChannel"

        configVariableTitle="User Key"
        configVariablePlaceholder="Pushover User Key"
        configVariableName="user_key"

        @createNotificationChannel="(channel, config) => $emit('createNotificationChannel', channel, config)"
        @updateNotificationChannel="(channel, changedProps) => $emit('updateNotificationChannel', channel, changedProps)"
        @deleteNotificationChannel="(channel) => $emit('deleteNotificationChannel', channel)"
        @clearErrorMessages="(settingKey) => $emit('clearErrorMessages', settingKey)"
    >
    ...
```

- A paragraph to explain to the user about how to set up to receive the notification, such as where to download the app, how to install it, and how to obtain the config data (if necessary). For instance:
```
      ...
      <small class="form-text text-muted">
        If you have a Pushover account, you can
        <a href="https://support.pushover.net/i7-what-is-pushover-and-how-do-i-use-it" target="_blank">get your User Key</a>
        and enter it here.
      </small>
      ...
```

:::caution
The `{plugin_id}` should match the value used in the [plugin backend](#the-plugin-backend). Otherwise the plugin's preference page can't be displayed correctly.
:::

#### Add a section to `frontend/src/notifications/plugins.js` {#add-a-section-to-frontendsrcnotificationspluginsjs}

```javascript
    \{plugin_id\}: \{
        displayName: 'Plugin name',
    \},
```

:::caution
The `{plugin_id}` should match the value used in the [plugin backend](#the-plugin-backend). Otherwise the plugin's preference page can't be displayed correctly.
:::


## The environment variables {#the-environment-variables}

Skip this part if your plugin doesn't need any new environment variables.

### Set up environment variables {#set-up-environment-variables}

Follow [this guide](/docs/server-guides/configure/#if-you-need-to-add-a-new-environment-variable) to add new environment variables to the self-hosted Obico Server.

### Declare the environment variable requirements in the plugin {#declare-the-environment-variable-requirements-in-the-plugin}

Add [`env_vars`](#env_vars) method to your plugin to declare  the environment variable requirements.


## Compile the plugin and load it in your Obico Server {#compile-the-plugin-and-load-it-in-your-obico-server}

Every time you make a change to the plugin frontend, you need to re-compile the plugin and restart your server to test the change.

    cd frontend
    yarn
    yarn build
    cd ..
    docker-compose restart


## Contribute your plugin back to the Obico project {#contribute-your-plugin-back-to-the-obico-project}

:::info
This step is completely optional. You won't violate the Obico license if you just want to keep the plugin to yourself without contributing back.
:::

Please read this [contributor's guide](../contribute.md) for how you can contribute the plugin you developed back to the Obico project.
