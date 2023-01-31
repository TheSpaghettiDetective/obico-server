---
id: overview
title: Obico for Klipper Overview
---

**Obico for Klipper** is implemented as a [**Moonraker agent**](https://moonraker.readthedocs.io/en/latest/web_api/).

:::info
[Moonraker](https://moonraker.readthedocs.io/en/latest/web_api/) is a "middleware" that handles the low-level communication with the Klipper firmware.

It sits between Klipper and the "frontend". [Mainsail](https://docs.mainsail.xyz/) and [Fluidd](https://docs.fluidd.xyz/) are 2 popular frontends.
:::

:::caution
OctoPrint is also commonly used to communicate with the Klipper firmware. If this is how you do it, please use [Obico for OctoPrint](/docs/user-guides/octoprint-plugin-setup/) instead.
:::

The source code of **Obico for Klipper** is located at [https://github.com/TheSpaghettiDetective/moonraker-obico](https://github.com/TheSpaghettiDetective/moonraker-obico).


```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```
