<template>
  <div class="row justify-content-center">
    <div class="col-sm-11 col-md-10 col-lg-8">
      <div v-if="user" class="form-container">
        <!-- Profile -->
        <section class="profile">
          <h2 class="section-title">Profile</h2>
          <div class="form-group row">
            <label class="col-md-2 col-sm-3 col-form-label">Password</label>
            <div class="col-md-10 col-sm-9 col-form-label text-muted">
              <a href="/accounts/password/change">Change</a>
            </div>
          </div>
          <div class="form-group row">
            <label for="id_first_name" class="col-md-2 col-sm-3 col-form-label">First Name</label>
            <div class="col-md-10 col-sm-9">
              <saving-animation :errors="errorMessages.first_name" :saving="saving.first_name">
                <input
                  type="text"
                  maxlength="30"
                  class="form-control"
                  id="id_first_name"
                  v-model="user.first_name"
                >
              </saving-animation>
            </div>
          </div>
          <div class="form-group row">
            <label for="id_last_name" class="col-md-2 col-sm-3 col-form-label">Last Name</label>
            <div class="col-md-10 col-sm-9">
              <saving-animation :errors="errorMessages.last_name" :saving="saving.last_name">
                <input
                  type="text"
                  maxlength="30"
                  class="form-control"
                  id="id_last_name"
                  v-model="user.last_name"
                >
              </saving-animation>
            </div>
          </div>
        </section>

        <!-- Notifications -->
        <section class="notifications">
          <h2 class="section-title">Notifications</h2>
          <div class="row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.notify_on_done" :saving="saving.notify_on_done" height="small">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_notify_on_done"
                    v-model="user.notify_on_done"
                    @change="updateSetting('notify_on_done')"
                  >
                  <label class="custom-control-label" for="id_notify_on_done">
                    Notify me when print job is done
                  </label>
                </div>
              </saving-animation>
            </div>
          </div>
          <div class="row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.notify_on_canceled" :saving="saving.notify_on_canceled" height="small">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_notify_on_canceled"
                    v-model="user.notify_on_canceled"
                    @change="updateSetting('notify_on_canceled')"
                  >
                  <label class="custom-control-label" for="id_notify_on_canceled">
                    Notify me when print job is canceled
                  </label>
                </div>
              </saving-animation>
            </div>
          </div>
          <div class="row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.account_notification_by_email" :saving="saving.account_notification_by_email" height="small">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_account_notification_by_email"
                    v-model="user.account_notification_by_email"
                    @change="updateSetting('account_notification_by_email')"
                  >
                  <label class="custom-control-label" for="id_account_notification_by_email">
                    Notify me on account events (such as running out of Detective Hours)
                  </label>
                </div>
              </saving-animation>
            </div>
          </div>
        </section>

        <!-- Email -->
        <section class="email">
          <h2 class="section-title">Email</h2>
          <div class="row">
            <label for="id_email" class="col-md-2 col-sm-3 col-form-label">Primary Email</label>
            <div class="col-md-10 col-sm-9 col-form-label text-muted">{{user.email}} ({{user.is_primary_email_verified ? 'Verified' : 'Unverified'}})
              <div class="form-text"><a href="/accounts/email">Manage email addresses</a></div>
            </div>
          </div>
          <div class="row">
            <label class="col-md-2 col-sm-3 col-form-label"></label>
            <div class="col-md-10 col-sm-9 col-form-label">
              <saving-animation :errors="errorMessages.alert_by_email" :saving="saving.alert_by_email">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_alert_by_email"
                    v-model="user.alert_by_email"
                    @change="updateSetting('alert_by_email')"
                  >
                  <label class="custom-control-label" for="id_alert_by_email">
                    Send failure alerts to all verified email addresses
                  </label>
                </div>
              </saving-animation>
            </div>
          </div>
          <div class="row">
            <label class="col-md-2 col-sm-3 col-form-label"></label>
            <div class="col-md-10 col-sm-9 col-form-label">
              <saving-animation :errors="errorMessages.print_notification_by_email" :saving="saving.print_notification_by_email" height="small">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_print_notification_by_email"
                    v-model="user.print_notification_by_email"
                    @change="updateSetting('print_notification_by_email')"
                  >
                  <label class="custom-control-label" for="id_print_notification_by_email">
                    Send print job notifications to all verified email addresses
                  </label>
                </div>
              </saving-animation>
            </div>
          </div>
        </section>

        <!-- SMS -->
        <section class="sms">
          <h2 class="section-title">SMS</h2>
          <div class="form-group row">
            <label for="id_email" class="col-md-2 col-sm-3 col-form-label">Phone Number</label>
            <div class="col-md-10 col-sm-9 col-form-label">
              <div v-if="twilioEnabled">
                <saving-animation :errors="errorMessages.phone" :saving="saving.phone">
                  <div class="form-group row">
                    <div class="col-sm-6">
                      <div class="dropdown bootstrap-select form-control">
                        <select
                          class="form-control selectpicker"
                          id="id_phone_country_code"
                          data-live-search="true"
                          v-model="user.phone_country_code"
                        >
                          <option value="+1">USA/Canada (+1)</option>
                          <option value="+213">Algeria (+213)</option>
                          <option value="+376">Andorra (+376)</option>
                          <option value="+244">Angola (+244)</option>
                          <option value="+1264">Anguilla (+1264)</option>
                          <option value="+1268">Antigua &amp; Barbuda (+1268)</option>
                          <option value="+54">Argentina (+54)</option>
                          <option value="+374">Armenia (+374)</option>
                          <option value="+297">Aruba (+297)</option>
                          <option value="+61">Australia (+61)</option>
                          <option value="+43">Austria (+43)</option>
                          <option value="+994">Azerbaijan (+994)</option>
                          <option value="+1242">Bahamas (+1242)</option>
                          <option value="+973">Bahrain (+973)</option>
                          <option value="+880">Bangladesh (+880)</option>
                          <option value="+1246">Barbados (+1246)</option>
                          <option value="+375">Belarus (+375)</option>
                          <option value="+32">Belgium (+32)</option>
                          <option value="+501">Belize (+501)</option>
                          <option value="+229">Benin (+229)</option>
                          <option value="+1441">Bermuda (+1441)</option>
                          <option value="+975">Bhutan (+975)</option>
                          <option value="+591">Bolivia (+591)</option>
                          <option value="+387">Bosnia Herzegovina (+387)</option>
                          <option value="+267">Botswana (+267)</option>
                          <option value="+55">Brazil (+55)</option>
                          <option value="+673">Brunei (+673)</option>
                          <option value="+359">Bulgaria (+359)</option>
                          <option value="+226">Burkina Faso (+226)</option>
                          <option value="+257">Burundi (+257)</option>
                          <option value="+855">Cambodia (+855)</option>
                          <option value="+237">Cameroon (+237)</option>
                          <option value="+238">Cape Verde Islands (+238)</option>
                          <option value="+1345">Cayman Islands (+1345)</option>
                          <option value="+236">Central African Republic (+236)</option>
                          <option value="+56">Chile (+56)</option>
                          <option value="+86">China (+86)</option>
                          <option value="+57">Colombia (+57)</option>
                          <option value="+269">Comoros (+269)</option>
                          <option value="+242">Congo (+242)</option>
                          <option value="+682">Cook Islands (+682)</option>
                          <option value="+506">Costa Rica (+506)</option>
                          <option value="+385">Croatia (+385)</option>
                          <option value="+53">Cuba (+53)</option>
                          <option value="+90392">Cyprus North (+90392)</option>
                          <option value="+357">Cyprus South (+357)</option>
                          <option value="+420">Czech Republic (+420)</option>
                          <option value="+45">Denmark (+45)</option>
                          <option value="+253">Djibouti (+253)</option>
                          <option value="+1809">Dominica (+1809)</option>
                          <option value="+1809">Dominican Republic (+1809)</option>
                          <option value="+593">Ecuador (+593)</option>
                          <option value="+20">Egypt (+20)</option>
                          <option value="+503">El Salvador (+503)</option>
                          <option value="+240">Equatorial Guinea (+240)</option>
                          <option value="+291">Eritrea (+291)</option>
                          <option value="+372">Estonia (+372)</option>
                          <option value="+251">Ethiopia (+251)</option>
                          <option value="+500">Falkland Islands (+500)</option>
                          <option value="+298">Faroe Islands (+298)</option>
                          <option value="+679">Fiji (+679)</option>
                          <option value="+358">Finland (+358)</option>
                          <option value="+33">France (+33)</option>
                          <option value="+594">French Guiana (+594)</option>
                          <option value="+689">French Polynesia (+689)</option>
                          <option value="+241">Gabon (+241)</option>
                          <option value="+220">Gambia (+220)</option>
                          <option value="+7880">Georgia (+7880)</option>
                          <option value="+49">Germany (+49)</option>
                          <option value="+233">Ghana (+233)</option>
                          <option value="+350">Gibraltar (+350)</option>
                          <option value="+30">Greece (+30)</option>
                          <option value="+299">Greenland (+299)</option>
                          <option value="+1473">Grenada (+1473)</option>
                          <option value="+590">Guadeloupe (+590)</option>
                          <option value="+671">Guam (+671)</option>
                          <option value="+502">Guatemala (+502)</option>
                          <option value="+224">Guinea (+224)</option>
                          <option value="+245">Guinea - Bissau (+245)</option>
                          <option value="+592">Guyana (+592)</option>
                          <option value="+509">Haiti (+509)</option>
                          <option value="+504">Honduras (+504)</option>
                          <option value="+852">Hong Kong (+852)</option>
                          <option value="+36">Hungary (+36)</option>
                          <option value="+354">Iceland (+354)</option>
                          <option value="+91">India (+91)</option>
                          <option value="+62">Indonesia (+62)</option>
                          <option value="+98">Iran (+98)</option>
                          <option value="+964">Iraq (+964)</option>
                          <option value="+353">Ireland (+353)</option>
                          <option value="+972">Israel (+972)</option>
                          <option value="+39">Italy (+39)</option>
                          <option value="+1876">Jamaica (+1876)</option>
                          <option value="+81">Japan (+81)</option>
                          <option value="+962">Jordan (+962)</option>
                          <option value="+7">Kazakhstan (+7)</option>
                          <option value="+254">Kenya (+254)</option>
                          <option value="+686">Kiribati (+686)</option>
                          <option value="+850">Korea North (+850)</option>
                          <option value="+82">Korea South (+82)</option>
                          <option value="+965">Kuwait (+965)</option>
                          <option value="+996">Kyrgyzstan (+996)</option>
                          <option value="+856">Laos (+856)</option>
                          <option value="+371">Latvia (+371)</option>
                          <option value="+961">Lebanon (+961)</option>
                          <option value="+266">Lesotho (+266)</option>
                          <option value="+231">Liberia (+231)</option>
                          <option value="+218">Libya (+218)</option>
                          <option value="+417">Liechtenstein (+417)</option>
                          <option value="+370">Lithuania (+370)</option>
                          <option value="+352">Luxembourg (+352)</option>
                          <option value="+853">Macao (+853)</option>
                          <option value="+389">Macedonia (+389)</option>
                          <option value="+261">Madagascar (+261)</option>
                          <option value="+265">Malawi (+265)</option>
                          <option value="+60">Malaysia (+60)</option>
                          <option value="+960">Maldives (+960)</option>
                          <option value="+223">Mali (+223)</option>
                          <option value="+356">Malta (+356)</option>
                          <option value="+692">Marshall Islands (+692)</option>
                          <option value="+596">Martinique (+596)</option>
                          <option value="+222">Mauritania (+222)</option>
                          <option value="+269">Mayotte (+269)</option>
                          <option value="+52">Mexico (+52)</option>
                          <option value="+691">Micronesia (+691)</option>
                          <option value="+373">Moldova (+373)</option>
                          <option value="+377">Monaco (+377)</option>
                          <option value="+976">Mongolia (+976)</option>
                          <option value="+1664">Montserrat (+1664)</option>
                          <option value="+212">Morocco (+212)</option>
                          <option value="+258">Mozambique (+258)</option>
                          <option value="+95">Myanmar (+95)</option>
                          <option value="+264">Namibia (+264)</option>
                          <option value="+674">Nauru (+674)</option>
                          <option value="+977">Nepal (+977)</option>
                          <option value="+31">Netherlands (+31)</option>
                          <option value="+687">New Caledonia (+687)</option>
                          <option value="+64">New Zealand (+64)</option>
                          <option value="+505">Nicaragua (+505)</option>
                          <option value="+227">Niger (+227)</option>
                          <option value="+234">Nigeria (+234)</option>
                          <option value="+683">Niue (+683)</option>
                          <option value="+672">Norfolk Islands (+672)</option>
                          <option value="+670">Northern Marianas (+670)</option>
                          <option value="+47">Norway (+47)</option>
                          <option value="+968">Oman (+968)</option>
                          <option value="+680">Palau (+680)</option>
                          <option value="+507">Panama (+507)</option>
                          <option value="+675">Papua New Guinea (+675)</option>
                          <option value="+595">Paraguay (+595)</option>
                          <option value="+51">Peru (+51)</option>
                          <option value="+63">Philippines (+63)</option>
                          <option value="+48">Poland (+48)</option>
                          <option value="+351">Portugal (+351)</option>
                          <option value="+1787">Puerto Rico (+1787)</option>
                          <option value="+974">Qatar (+974)</option>
                          <option value="+262">Reunion (+262)</option>
                          <option value="+40">Romania (+40)</option>
                          <option value="+7">Russia (+7)</option>
                          <option value="+250">Rwanda (+250)</option>
                          <option value="+378">San Marino (+378)</option>
                          <option value="+239">Sao Tome &amp; Principe (+239)</option>
                          <option value="+966">Saudi Arabia (+966)</option>
                          <option value="+221">Senegal (+221)</option>
                          <option value="+381">Serbia (+381)</option>
                          <option value="+248">Seychelles (+248)</option>
                          <option value="+232">Sierra Leone (+232)</option>
                          <option value="+65">Singapore (+65)</option>
                          <option value="+421">Slovak Republic (+421)</option>
                          <option value="+386">Slovenia (+386)</option>
                          <option value="+677">Solomon Islands (+677)</option>
                          <option value="+252">Somalia (+252)</option>
                          <option value="+27">South Africa (+27)</option>
                          <option value="+34">Spain (+34)</option>
                          <option value="+94">Sri Lanka (+94)</option>
                          <option value="+290">St. Helena (+290)</option>
                          <option value="+1869">St. Kitts (+1869)</option>
                          <option value="+1758">St. Lucia (+1758)</option>
                          <option value="+249">Sudan (+249)</option>
                          <option value="+597">Suriname (+597)</option>
                          <option value="+268">Swaziland (+268)</option>
                          <option value="+46">Sweden (+46)</option>
                          <option value="+41">Switzerland (+41)</option>
                          <option value="+963">Syria (+963)</option>
                          <option value="+886">Taiwan (+886)</option>
                          <option value="+7">Tajikstan (+7)</option>
                          <option value="+66">Thailand (+66)</option>
                          <option value="+228">Togo (+228)</option>
                          <option value="+676">Tonga (+676)</option>
                          <option value="+1868">Trinidad &amp; Tobago (+1868)</option>
                          <option value="+216">Tunisia (+216)</option>
                          <option value="+90">Turkey (+90)</option>
                          <option value="+7">Turkmenistan (+7)</option>
                          <option value="+993">Turkmenistan (+993)</option>
                          <option value="+1649">Turks &amp; Caicos Islands (+1649)</option>
                          <option value="+688">Tuvalu (+688)</option>
                          <option value="+256">Uganda (+256)</option>
                          <option value="+44">UK (+44)</option>
                          <option value="+380">Ukraine (+380)</option>
                          <option value="+971">United Arab Emirates (+971)</option>
                          <option value="+598">Uruguay (+598)</option>
                          <option value="+7">Uzbekistan (+7)</option>
                          <option value="+678">Vanuatu (+678)</option>
                          <option value="+379">Vatican City (+379)</option>
                          <option value="+58">Venezuela (+58)</option>
                          <option value="+84">Vietnam (+84)</option>
                          <option value="+84">Virgin Islands - British (+1284)</option>
                          <option value="+84">Virgin Islands - US (+1340)</option>
                          <option value="+681">Wallis &amp; Futuna (+681)</option>
                          <option value="+969">Yemen (North)(+969)</option>
                          <option value="+967">Yemen (South)(+967)</option>
                          <option value="+260">Zambia (+260)</option>
                          <option value="+263">Zimbabwe (+263)</option>
                        </select>
                      </div>
                    </div>
                    <div class="col-sm-6">
                      <input
                        type="text"
                        class="form-control"
                        id="id_phone_number"
                        placeholder="Phone Number"
                        v-model="user.phone_number"
                      >
                    </div>
                  </div>
                </saving-animation>
                <small class="text-muted">
                  <div>Can't find your country code?</div>
                  <div>The Spaghetti Detective Team is currently self-funded. Therefore we can't afford to open to
                    countries with high SMS cost. We will add more countries once we find a cost-effective SMS solution,
                    or secure sufficient funding.</div>
                </small>
              </div>
              <p v-else class="text-muted">Please configure TWILIO_* items in settings to enable phone alert.</p>
            </div>
          </div>
          <div class="form-group row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.alert_by_sms" :saving="saving.alert_by_sms">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_alert_by_sms"
                    v-model="user.alert_by_sms"
                    @change="updateSetting('alert_by_sms')"
                  >
                  <label class="custom-control-label" for="id_alert_by_sms">
                    Alert me via SMS when print failures are detected
                  </label>
                </div>
              </saving-animation>
              <small v-if="!user.is_pro" class="text-warning">Note: You won't be alerted via SMS because this is a Pro feature and you are on the Free plan.</small>
            </div>
          </div>
        </section>

        <!-- Pushbullet -->
        <section class="pushbullet">
          <h2 class="section-title">Pushbullet</h2>
          <small class="form-text text-muted">
            If you have a Pushbullet account, you can
            <a href="https://www.pushbullet.com/#settings">generate an access token</a>
            and enter it here.
          </small>
          <br>
          <div class="form-group row">
            <label for="id_pushbullet_access_token" class="col-md-2 col-sm-3 col-form-label">Access Token</label>
            <div class="col-md-10 col-sm-9 col-form-label">
              <saving-animation :errors="errorMessages.pushbullet_access_token" :saving="saving.pushbullet_access_token">
                <input
                  type="text"
                  maxlength="45"
                  placeholder="Pushbullet Access Token"
                  class="form-control"
                  id="id_pushbullet_access_token"
                  v-model="user.pushbullet_access_token"
                >
              </saving-animation>
            </div>
          </div>
          <div class="form-group row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.print_notification_by_pushbullet" :saving="saving.print_notification_by_pushbullet" height="small">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_print_notification_by_pushbullet"
                    v-model="user.print_notification_by_pushbullet"
                    @change="updateSetting('print_notification_by_pushbullet')"
                  >
                  <label class="custom-control-label" for="id_print_notification_by_pushbullet">
                    Send print job notifications via PushPullet
                  </label>
                </div>
              </saving-animation>
              <small class="text-muted">You will always be alerted via PushPullet on print failures.</small>
            </div>
          </div>
        </section>

        <!-- Discord -->
        <section class="discord">
          <h2 class="section-title">Discord</h2>
          <small class="form-text text-muted">
            If you have a Discord channel you wish to receive notifications on, you can
            <a href="https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks">generate webhook url</a>
            and enter it here.
          </small>
          <br>
          <div class="form-group row">
            <label for="id_discord_webhook" class="col-md-2 col-sm-3 col-form-label">Webhook URL</label>
            <div class="col-md-10 col-sm-9 col-form-label">
              <saving-animation :errors="errorMessages.discord_webhook" :saving="saving.discord_webhook">
                <input
                  type="text"
                  maxlength="256"
                  placeholder="Discord Webhook"
                  class="form-control"
                  id="id_discord_webhook"
                  v-model="user.discord_webhook"
                >
              </saving-animation>
            </div>
          </div>
          <div class="form-group row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.print_notification_by_discord" :saving="saving.print_notification_by_discord">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_print_notification_by_discord"
                    v-model="user.print_notification_by_discord"
                    @change="updateSetting('print_notification_by_discord')"
                  >
                  <label class="custom-control-label" for="id_print_notification_by_discord">
                    Send print job notifications via Discord Webhook
                  </label>
                </div>
              </saving-animation>
              <small class="text-muted">You will always be alerted via Discord on print failures.</small>
            </div>
          </div>
        </section>

        <!-- pushover -->
        <section v-if="pushOverEnabled" class="pushover">
          <h2>Pushover</h2>
          <small class="form-text text-muted">
            If you have a Pushover account, you can
            <a href="https://support.pushover.net/i7-what-is-pushover-and-how-do-i-use-it">get your User Key</a>
            and enter it here.
          </small>
          <br />
          <div class="form-group row">
            <label for="id_pushover_user_token" class="col-md-2 col-sm-3 col-form-label">User Key</label>
            <div class="col-md-10 col-sm-9 col-form-label">
              <saving-animation :errors="errorMessages.pushover_user_token" :saving="saving.pushover_user_token">
                <input
                  type="text"
                  maxlength="256"
                  placeholder="Pushover User Key"
                  class="form-control"
                  id="id_pushover_user_token"
                  v-model="user.pushover_user_token"
                >
              </saving-animation>
            </div>
          </div>
          <div class="form-group row">
            <div class="col-md-10 offset-md-2 col-sm-9 offset-sm-3 col-form-label">
              <saving-animation :errors="errorMessages.print_notification_by_pushover" :saving="saving.print_notification_by_pushover">
                <div class="custom-control custom-checkbox form-check-inline">
                  <input
                    type="checkbox"
                    class="custom-control-input"
                    id="id_print_notification_by_pushover"
                    v-model="user.print_notification_by_pushover"
                    @change="updateSetting('print_notification_by_pushover')"
                  >
                  <label class="custom-control-label" for="id_print_notification_by_pushover">
                    Send print job notifications via Pushover
                  </label>
                </div>
              </saving-animation>
              <small class="text-muted">You will always be alerted via Pushover on print failures.</small>
            </div>
          </div>
        </section>

        <!-- Slack -->
        <section v-if="slackEnabled" class="slack">
          <h2 class="section-title">Slack</h2>
          <a href="/ent/slack_setup/">Set up Slack integration >>></a>
        </section>
      </div>
      <div v-else class="text-center">
        <b-spinner class="mt-5" label="Loading..."></b-spinner>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@lib/server_urls'
import SavingAnimation from '../common/SavingAnimation.vue'

export default {
  name: 'UserPreferencesPage',
  components: {
    SavingAnimation,
  },

  data() {
    return {
      user: null,
      saving: {},
      errorMessages: {},
      delayedSubmit: { // Make pause before sending new value to API
        'first_name': {
          'delay': 1000,
          'timeoutId': null
        },
        'last_name': {
          'delay': 1000,
          'timeoutId': null
        },
        'pushbullet_access_token': {
          'delay': 1000,
          'timeoutId': null
        },
        'discord_webhook': {
          'delay': 1000,
          'timeoutId': null
        },
        'phone_number': {
          'delay': 1000,
          'timeoutId': null
        },
        'pushover_user_token': {
          'delay': 1000,
          'timeoutId': null
        },
      },
      twilioEnabled: false,
      slackEnabled: false,
      pushOverEnabled: false,
      combinedInputs: { // Send changes to API only if all the other values in the array have data
        phone: ['phone_country_code', 'phone_number'],
      },
    }
  },

  computed: {
    firstName: {
      get: function() {
        return this.user ? this.user.first_name : null
      },
      set: function(newValue) {
        this.user.first_name = newValue
      }
    },
    lastName: {
      get: function() {
        return this.user ? this.user.last_name : null
      },
      set: function(newValue) {
        this.user.last_name = newValue
      }
    },
    phoneCountryCode: {
      get: function() {
        return this.user ? this.user.phone_country_code : null
      },
      set: function(newValue) {
        this.user.phone_country_code = newValue
      }
    },
    phoneNumber: {
      get: function() {
        return this.user ? this.user.phone_number : null
      },
      set: function(newValue) {
        this.user.phone_number = newValue
      }
    },
    pushbulletToken: {
      get: function() {
        return this.user ? this.user.pushbullet_access_token : null
      },
      set: function(newValue) {
        this.user.pushbullet_access_token = newValue
      }
    },
    discordWebhook: {
      get: function() {
        return this.user ? this.user.discord_webhook : null
      },
      set: function(newValue) {
        this.user.discord_webhook = newValue
      }
    },
    pushoverUserToken: {
      get: function() {
        return this.user ? this.user.pushover_user_token : null
      },
      set: function(newValue) {
        this.user.pushover_user_token = newValue
      }
    },
  },

  watch: {
    firstName: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('first_name')
      }
    },
    lastName: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('last_name')
      }
    },
    phoneCountryCode: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('phone_country_code')
      }
    },
    phoneNumber: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('phone_number')
      }
    },
    pushbulletToken: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('pushbullet_access_token')
      }
    },
    discordWebhook: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('discord_webhook')
      }
    },
    pushoverUserToken: function (newValue, oldValue) {
      if (oldValue !== null) {
        this.updateSetting('pushover_user_token')
      }
    }
  },

  props: {
    config: {
      default() {return {}},
      type: Object,
    },
  },

  mounted() {
    if (document.querySelector('#settings-json')) {
      const {TWILIO_ENABLED, SLACK_CLIENT_ID, PUSHOVER_APP_TOKEN} = JSON.parse(document.querySelector('#settings-json').text)
      this.twilioEnabled = !!TWILIO_ENABLED
      this.slackEnabled = !!SLACK_CLIENT_ID
      this.pushOverEnabled = !!PUSHOVER_APP_TOKEN
    }
    this.fetchUser()
  },

  methods: {
    /**
     * Get actual user preferences
     */
    fetchUser() {
      return axios
        .get(urls.user())
        .then(response => {
          this.user = response.data

          if (!this.user.phone_country_code) {
            this.user.phone_country_code = '+1'
          }
        })
    },

    /**
     * Update user settings
     * @param {String} propName
     * @param {any} propValue
     */
    patchUser(propName, propValue) {
      let data = {}

      let key = propName
      const combinedInputs = this.checkForCombinedValues(propName)
      if (combinedInputs) {
        // Must include all the inputs from the array
        // or don't send if some of them have no data
        for (const input of combinedInputs.inputs) {
          key = combinedInputs.key
          const value = this.user[input]
          if (value) {
            data[input] = value
          } else {
            return
          }
        }
      } else {
        data = {[propName]: propValue}
      }

      this.setSavingStatus(key, true)

      // Make request to API
      return axios
        .patch(urls.user(), data)
        .catch(err => {
          if (err.response && err.response.data && typeof err.response.data === 'object') {
            if (err.response.data.non_field_errors) {
              this.errorAlert(err.response.data.non_field_errors)
            } else {
              for (const error in err.response.data) {
                this.errorMessages[key] = err.response.data[error]
              }
            }
          } else {
            this.errorAlert()
          }
        })
        .then(() => {
          this.setSavingStatus(key, false)
        })
    },

    /**
     * Checks if value is associated with others (must be sent simultaneously)
     * and returns array of input names in the collection
     * @param {String} propName
     * @return {Array, Boolean} array with input names or False
     */
    checkForCombinedValues(propName) {
      for (const [key, inputs] of Object.entries(this.combinedInputs)) {
        if (inputs.includes(propName)) {
          return {inputs, key}
        }
      }

      return null
    },

    /**
     * Interlayer for saving status control to be able to set same saving status
     * for 2 or more different inputs grouped to one block
     * @param {String} propName
     * @param {String} status
     */
    setSavingStatus(propName, status) {
      if (status) {
        delete this.errorMessages[propName]
      }
      this.$set(this.saving, propName, status)
    },

    /**
     * Show error alert if can not save settings
     */
    errorAlert(text=null) {
      this.$swal({
        icon: 'error',
        html: `<p>${text ? text : 'Can not update your preferences.'}</p><p>Get help from <a href="https://discord.com/invite/NcZkQfj">TSD discussion forum</a> if this error persists.</p>`,
      })
    },

    /**
     * Update particular settings item
     * @param {String} settingsItem
     */
    updateSetting(settingsItem) {
      if (settingsItem in this.delayedSubmit) {
        const delayInfo = this.delayedSubmit[settingsItem]
        if (delayInfo['timeoutId']) {
          clearTimeout(delayInfo['timeoutId'])
        }
        this.delayedSubmit[settingsItem]['timeoutId'] = setTimeout(() => {
          this.patchUser(settingsItem, this.user[settingsItem])
        }, delayInfo['delay'])
        return
      }

      this.patchUser(settingsItem, this.user[settingsItem])
    },
  }
}
</script>

<style lang="sass" scoped>
@use "~main/theme"

section:not(:first-child)
  margin-top: 60px

  .section-title
    border-bottom: 1px solid theme.$white

</style>
