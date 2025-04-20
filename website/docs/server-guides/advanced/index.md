---
title: Advanced Topics
---

## Configure Obico Server using `.env` {#configure-obico-server-using-env}

You can further configure Obico Server using the `.env` file.

:::caution
Configuring Obico Server using the `.env` file is for advanced users. If incorrectly configured, Obico Server may not start up or function correctly.
:::


1. In `obico-server` directory, make a copy of `dotenv.example` and rename the copy as `.env`. If you are on a Linux the server, run `cp dotenv.example .env`.

:::caution
The `.env` file name is NOT a typo. Please don't name the file `env`. Otherwise Obico Server won't try to read that file.
:::

2. Open `.env` using your favorite editor.

3. Go through the lines in the file, and remove the leading `#` on the lines that you intend to change. Please do NOT remove the leading `#` on any line that you don't understand or don't intend to change. It may cause unexpected server behaviors.


## Other advanced server setups {#other-advanced-server-setups}

```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```
