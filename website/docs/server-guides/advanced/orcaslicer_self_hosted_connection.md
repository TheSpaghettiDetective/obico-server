---
title: Orcaslicer Connection Self Hosted guide
---

This is how to connect orcaslicer to self hosted obico

## Generate Token {#generate-token}

1. Go to http://your_obico_server/admin/oauth2_provider/accesstoken/add/

2. Select your user

3. Define a token you want to use (make it strong)

4. Add an expire date

5. Add Scope: `read write`

6. Click "Save"


## Connect Orcaslicer {#connect-orcaslicer}

Open Orcaslicer and click the "connection" button next to the printer and fill in the fields below:

      Host Type: Obico
      Hostname: obico.your.domain or ip:port
      Device Ui: Will be filled in when you select the printer dropdown or manually enter url to printer screen in obico
      API Key / Password: use the previously generated token in the #generate-token step 3
      Click Refresh Printers
      Printer: Select your printer
      Click OK
