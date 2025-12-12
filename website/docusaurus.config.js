const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'Obico', // Title for your website.
  tagline: 'Open-Source, Community-Built Smart 3D Printing Platform',
  url: 'https://www.obico.io', // Your website URL
  baseUrl: '/', // Base URL for your project */
  trailingSlash: true,
  projectName: 'public',
  organizationName: 'Obico',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',
  favicon: '/img/favicon.png',
  themes: ['@docusaurus/theme-mermaid'],
  markdown: {
    mermaid: true,
  },
  themeConfig: {
    announcementBar: {
      id: 'giveStarOnGitHubAnnouncement',
      content: `⭐️ If you like Obico, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/TheSpaghettiDetective/obico-server">GitHub</a>`,
    },
    colorMode: {
      // "light" | "dark"
      defaultMode: 'dark',

      // Hides the switch in the navbar
      // Useful if you want to support a single color mode
      disableSwitch: false,

      // Should we use the prefers-color-scheme media-query,
      // using user system preferences, instead of the hardcoded defaultMode
      respectPrefersColorScheme: true,

      // switchConfig: {
      //   // Icon for the switch while in dark mode
      //   darkIcon: '\u{263D}',

      //   // CSS to apply to dark icon,
      //   // React inline style object
      //   // see https://reactjs.org/docs/dom-elements.html#style
      //   darkIconStyle: {
      //     marginLeft: '2px',
      //   },

      //   // Unicode icons such as '\u2600' will work
      //   // Unicode with 5 chars require brackets: '\u{1F602}'
      //   lightIcon: '\u{1F602}',

      //   lightIconStyle: {
      //     marginLeft: '1px',
      //   },
      // },
    },
    navbar: {
      title: '',
      hideOnScroll: true,
      logo: {
        alt: 'Obico logo',
        src: 'img/logo.svg',
        srcDark: 'img/logo_dark.svg',
        href: 'https://www.obico.io',
        target: '_self',
      },
      items: [
        {
          label: 'Product',
          items: [
            {
              label: 'Obico for Octoprint',
              to: '/docs/user-guides/octoprint-plugin-setup/',
            },
            {
              label: 'Obico for Klipper',
              to: '/docs/user-guides/klipper-setup/',
            },
            {
              label: 'Obico Android Mobile App',
              to: 'https://play.google.com/store/apps/details?id=com.thespaghettidetective.android&hl=en_US&gl=US',
              target: '_self',
            },
            {
              label: 'Obico iOS Mobile App',
              to: 'https://apps.apple.com/sg/app/the-spaghetti-detective/id1540646623',
              target: '_self',
            },
            {
              label: 'Obico Server',
              to: 'https://github.com/TheSpaghettiDetective/obico-server',
              target: '_self',
            },
            {
              label: 'Obico Cloud vs Self-Hosted',
              to: 'https://obico.io/obico-cloud-vs-self-hosted.html',
              target: '_self',
            },
          ],
        },
        {
          label: 'Docs',
          items: [
            {
              label: 'Set up Obico for OctoPrint',
              to: '/docs/user-guides/octoprint-plugin-setup/',
            },
            {
              label: 'Set up Obico for Klipper',
              to: '/docs/user-guides/klipper-setup/',
            },
            {
              label: 'Self-hosting',
              to: '/docs/server-guides/',
            },
            {
              label: 'Client APIs',
              to: '/docs/api/',
            },
            {
              label: 'Developer Tutorials',
              to: '/docs/tutorials/',
            },
          ],
        },
        {
          label: 'Contribute',
          to: '/docs/developer-guides/contribute/',
        },
        {
          label: 'Community',
          to: 'https://obico.io/discord',
          target: '_self',
        },
        {
          label: 'Blog',
          to: '/blog',
        },
        {
          label: 'Pricing',
          to: 'https://app.obico.io/ent_pub/pricing/',
          target: '_self',
        },
        {
          label: 'About',
          position: 'left', // or 'right'
          items: [
            {
              label: 'Obico Team',
              to: 'https://www.obico.io/team.html',
              target: '_self',
            },
          ],
        },
        {
          label: 'Log in',
          to: 'https://app.obico.io/accounts/login/',
          target: '_self',
          position: 'right',
          className: ' obico-button obico-button-secondary obico-navbar-button',
        },
        {
          label: 'Get Started',
          to: 'https://app.obico.io/accounts/signup/',
          target: '_self',
          position: 'right',
          className: 'obico-button obico-button-primary obico-navbar-button',
        },
      ],
    },
    footer: {
      style: 'light',
      links: [
        {
          title: 'Product',
          items: [
            {
              label: 'Obico for OctoPrint',
              to: '/docs/user-guides/octoprint-plugin-setup/',
            },
            {
              label: 'Obico for Klipper',
              to: '/docs/user-guides/klipper-setup',
            },
            {
              label: 'Obico Cloud vs Self-Hosted',
              to: 'https://obico.io/obico-cloud-vs-self-hosted.html',
              target: '_self',
            },
            {
              label: 'Obico Cloud Pricing',
              to: 'https://app.obico.io/ent_pub/pricing/',
              target: '_self',
            },
          ],
        },
        {
          title: 'Features',
          items: [
            {
              label: 'Monitor and Control',
              to: 'https://www.obico.io/',
              target: '_self',
            },
            {
              label: 'AI Failure Detection',
              to: 'https://obico.io/failure-detection.html',
              target: '_self',
            },
          ],
        },
        {
          title: 'Docs',
          items: [
            {
              label: 'Obico Cloud Help',
              to: '/help',
            },
            {
              label: 'Self-Hosting',
              to: '/docs/server-guides/install/',
            },
            {
              html: '<b style="display: block; margin-top: .5rem;">Developer</b>',
            },
            {
              label: 'Obico Server Plugin',
              to: '/docs/developer-guides/plugins/',
            },
            {
              label: 'Client APIs',
              to: '/docs/api/',
            },
            {
              label: 'Developer Tutorials',
              to: '/docs/tutorials/',
            },
            {
              label: 'Orange Pi Zero 2 OctoPrint Kit',
              to: '/docs/user-guides/install-octoprint-orange-pi-zero-2-kit/',
            },
          ],
        },


        {
          title: 'Company',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'Team',
              to: 'https://obico.io/team.html',
              target: '_self',
            },
            {
              label: 'Contact Us',
              to: 'mailto:support@obico.io',
            },
            {
              label: 'Privacy Policy',
              to: 'https://obico.io/privacy.html',
              target: '_self',
            },
            {
              label: 'Terms of Use',
              to: 'https://obico.io/terms.html',
              target: '_self',
            },
            {
              label: 'Disclaimer',
              to: 'https://obico.io/disclaimer.html',
              target: '_self',
            },
          ],
        },
        {
          title: 'Stay Updated',
          items: [
            {
              html: `
                <div class="social-link-wrapper">
                  <iframe
                    src="https://platform.twitter.com/widgets/follow_button.06c6ee58c3810956b7509218508c7b56.en.html#dnt=false&amp;id=twitter-widget-0&amp;lang=en&amp;screen_name=thespaghettispy&amp;show_count=false&amp;show_screen_name=true&amp;size=m"
                    title="Twitter Follow Button"
                    scrolling="no"
                    frameborder="0"
                    allowtransparency="true"
                    allowfullscreen="true"
                    data-screen-name="thespaghettispy"
                    class="social-button-iframe twitter"
                  ></iframe>
                </div>
              `
            },
            {
              html: `
                <div class="social-link-wrapper">
                  <iframe
                    src="https://www.facebook.com/v2.7/plugins/like.php?app_id=176252365784303&amp;channel=https%3A%2F%2Fstaticxx.facebook.com%2Fx%2Fconnect%2Fxd_arbiter%2F%3Fversion%3D46%23cb%3Df2364772d933e6%26domain%3Dwww.thespaghettidetective.com%26origin%3Dhttps%253A%252F%252Fwww.thespaghettidetective.com%252Ff36caae895dd3f%26relation%3Dparent.parent&amp;color_scheme=dark&amp;container_width=247&amp;href=https%3A%2F%2Fwww.thespaghettidetective.com%2F&amp;layout=button&amp;locale=en_US&amp;sdk=joey&amp;share=true&amp;show_faces=false&amp;width=225"
                    title="fb:like Facebook Social Plugin"
                    name="f11c34588db2de4"
                    data-testid="fb:like Facebook Social Plugin"
                    frameborder="0"
                    allowtransparency="true"
                    allowfullscreen="true"
                    scrolling="no"
                    allow="encrypted-media"
                    class="social-button-iframe facebook"
                  ></iframe>
                </div>
              `
            },
            {
              html: `
                <div class="social-link-wrapper">
                  <iframe
                    src="https://www.youtube.com/subscribe_embed?usegapi=1&amp;channelid=UCbAJcR6t5lrdZ1JXjPPRjGA&amp;layout=default&amp;theme=dark&amp;count=hidden&amp;origin=https%3A%2F%2Fwww.thespaghettidetective.com&amp;gsrc=3p&amp;ic=1&amp;jsh=m%3B%2F_%2Fscs%2Fapps-static%2F_%2Fjs%2Fk%3Doz.gapi.en_GB.QgrvvY-3vaw.O%2Fam%3DAQ%2Fd%3D1%2Frs%3DAGLTcCPVcBVMBqiUiuyGKXb0Nv-aIZTldw%2Fm%3D__features__#_methods=onPlusOne%2C_ready%2C_close%2C_open%2C_resizeMe%2C_renderstart%2Concircled%2Cdrefresh%2Cerefresh%2Conload&amp;id=I0_1626789716512&amp;_gfid=I0_1626789716512&amp;parent=https%3A%2F%2Fwww.thespaghettidetective.com&amp;pfname=&amp;rpctoken=26693666"
                    ng-non-bindable=""
                    frameborder="0"
                    hspace="0"
                    marginheight="0"
                    marginwidth="0"
                    scrolling="no"
                    tabindex="0"
                    vspace="0"
                    id="I0_1626789716512"
                    name="I0_1626789716512"
                    data-gapiattached="true"
                    class="social-button-iframe youtube"
                  ></iframe>
                </div>
              `
            },
            {
              html: `
                <div class="social-link-wrapper">
                  <iframe
                    src="https://ghbtns.com/github-btn.html?user=TheSpaghettiDetective&amp;repo=TheSpaghettiDetective&amp;type=star&amp;count=true"
                    title="GitHub"
                    frameborder="0"
                    scrolling="0"
                    class="social-button-iframe github"
                  ></iframe>
                </div>
              `
            },
          ],
        },
      ],
      copyright: `<div class="copyright">Copyright © Obico ${new Date().getFullYear()}. All Rights Reserved.</div>`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
    algolia: {
      appId: 'QZIJCE3LMI',
      apiKey: '7c0a59c31476fdd2b09d262975a7e1e8',
      indexName: 'thespaghettidetective',
      searchParameters: {
      }, // Optional, if provided by Algolia
      placeholder: 'Search help doc'
    },
    themeConfig: {
      imageZoom: {
        // CSS selector to apply the plugin to, defaults to '.markdown img'
        selector: '.markdown img',
        // Optional medium-zoom options
        // see: https://www.npmjs.com/package/medium-zoom#options
        options: {
          margin: 24,
          background: '#BADA55',
          scrollOffset: 0,
          container: '#zoom-container',
          template: '#zoom-template',
        },
      },
      metadata: [{name: 'og:title', content: 'Obico'}],
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
          'https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/edit/master/website/',
        },
        blog: {
          showReadingTime: true,
          onInlineAuthors: 'ignore'
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        sitemap: false,
      },
    ],
  ],
  // Add custom scripts here that would be placed in <script> tags.
  scripts: [
    'https://buttons.github.io/buttons.js',
    'https://code.jquery.com/jquery-3.6.0.min.js',
    'https://www.googletagmanager.com/gtag/js?id=UA-133768246-1',
    'https://www.obico.io/js/analytics.js',
  ],
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        fromExtensions: ['html'],
      },
    ],
    'plugin-image-zoom',
  ],
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'de-DE', 'es-ES', 'fr-FR', 'it-IT', 'nl-NL', 'pl-PL', 'pt-BR', 'ru-RU'],
  },
};
