---
title: '"The same authentication token is being used by another printer"'
---

![](/img/user-guides/helpdocs/shared-auth-token-warning.png)

You will see this error in one of the following situations:

* The token for your printer to authenticate with the Obico server is somehow leaked and being used by other people. This is a serious security hazard as anyone who has your authentication token will also have a full control of your printer.
* You duplicated the content of your original SD card to another one. This hence causes the same authentication token to be shared across both printers. There is no security risk in this situation, assuming both SD cards are still in your possession. However, both printers will talk over each other and confuses the Obico server on everything from the status of the printer to the failure detection, hence rendering the app useless.

When you see this error, please immediately [re-link **all of your printers**](/docs/user-guides/relink-printer/) to the Obico server. This will refresh authentication tokens for all of them, and hence eliminate any potential security risks.
