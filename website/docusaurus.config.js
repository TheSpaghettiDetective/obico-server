const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'The Spaghetti Detective', // Title for your website.
  tagline: '3D Printer Remote Monitoring & Control',
  url: 'https://www.thespaghettidetective.com', // Your website URL
  baseUrl: '/', // Base URL for your project */
  trailingSlash: true,
  projectName: 'public',
  organizationName: 'The Spaghetti Detective',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',
  favicon: 'favicon-32x32.png',
  themeConfig: {
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
      logo: {
        alt: 'The Spaghetti Detective Logo',
        src: 'img/logo.svg',
        srcDark: 'img/logo_dark.svg',
        href: 'https://www.thespaghettidetective.com',
        target: '_self',
      },
      items: [
        {
          label: 'Pricing',
          to: 'https://app.thespaghettidetective.com/ent_pub/pricing/',
          target: '_self',
        },
        {
          label: 'Help',
          href: '/help',
        },
        {
          label: 'Forum',
          to: 'https://discord.gg/hsMwGpD',
          target: '_self',
        },
        {
          label: 'About',
          position: 'left', // or 'right'
          items: [
            {
              label: 'Open Source',
              to: '/docs/user_guides/open-source',
              target: '_self',
            },
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'The Detective Team',
              to: 'https://www.thespaghettidetective.com/team.html',
              target: '_self',
            },
          ],
        },
        {
          label: 'Sign In',
          to: 'https://app.thespaghettidetective.com/accounts/login/',
          target: '_self',
          position: 'right',
          className: ' tsd-button tsd-button-secondary tsd-navbar-button',
        },
        {
          label: 'Sign Up',
          to: 'https://app.thespaghettidetective.com/accounts/signup/',
          target: '_self',
          position: 'right',
          className: 'tsd-button tsd-button-primary tsd-navbar-button',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'The Product',
          items: [
            {
              label: 'What Is The Spaghetti Detective',
              to: 'https://thespaghettidetective.com/',
              target: '_self',
            },
            {
              label: 'See It In Action',
              to: 'https://www.thespaghettidetective.com/#gallery',
              target: '_self',
            },
            {
              label: 'Pricing',
              to: 'https://app.thespaghettidetective.com/ent_pub/pricing/',
              target: '_self',
            },
            {
              label: 'Open Source',
              to: '/docs/user_guides/open-source',
            },
          ],
        },
        {
          title: 'Help',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/user_guides/octoprint-plugin-setup',
            },
            {
              label: 'Failure Detection',
              to: '/docs/user_guides/detection-print-job-settings',
            },
            {
              label: 'Webcam Streaming',
              to: '/docs/user_guides/webcam-streaming-for-human-eyes',
            },
            {
              label: 'Troubleshooting Guides',
              to: '/docs/user_guides/troubleshoot-server-connection-issues/',
            },
          ],
        },

        {
          title: 'About',
          items: [
            {
              label: 'Contact Us',
              to: '/docs/user_guides/contact-us-for-support',
            },
            {
              label: 'Terms of Use',
              to: 'https://www.thespaghettidetective.com/terms.html',
              target: '_self',
            },
            {
              label: 'Privacy Policy',
              to: 'https://www.thespaghettidetective.com/privacy.html',
              target: '_self',
            },
            {
              label: 'Disclaimer',
              to: 'https://www.thespaghettidetective.com/disclaimer.html',
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
      copyright: `<div class="copyright">Copyright © The Spaghetti Detective ${new Date().getFullYear()}. All Rights Reserved.</div>`,
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
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
          'https://github.com/TheSpaghettiDetective/TheSpaghettiDetective/edit/master/website/',
        },
        blog: {
          showReadingTime: true,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  // Add custom scripts here that would be placed in <script> tags.
  scripts: [
    'https://buttons.github.io/buttons.js',
    'https://www.thespaghettidetective.com/vendor/jquery/jquery.min.js',
    'https://www.thespaghettidetective.com/js/analytics.min.js',
    '/js/compact-view.js',
  ],
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        fromExtensions: ['html'],
      },
    ],
  ],
};
