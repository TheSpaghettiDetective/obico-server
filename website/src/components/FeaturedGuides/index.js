import React from 'react';
import clsx from 'clsx';
import styles from './index.module.css';

const LinksList = [
  {
    title: 'What is AI Detection Hour and how does it work?',
    route: '/docs/user-guides/how-does-detective-hour-work/',
  },
  {
    title: 'I want to help The Detective get better at her job. How can I do it?',
    route: '/docs/user-guides/how-does-credits-work/',
  },
  {
    title: 'The Pro plan vs the Free plan',
    route: '/docs/user-guides/upgrade-to-pro/',
  },
  {
    title: 'Webcam streaming resolution and frame rate',
    route: '/docs/user-guides/webcam-streaming-resolution-framerate/',
  },
  {
    title: 'OctoPrint Tunneling',
    route: '/docs/user-guides/octoprint-tunneling/',
  },
  {
    title: 'Optimal camera and lighting setup for the best results',
    route: '/docs/user-guides/optimal-camera-setup/',
  },

];

function GuideLink({title, route}) {
  const Icon = require('../../../static/img/user-guides/home/guide-icon.svg').default;

  return (
    <div className={clsx('col col--6')}>
      <a href={route} className={clsx('guide-link', styles.guideLink)}>
        <Icon className={styles.linkIcon} alt={title} />
        <div>{title}</div>
      </a>
    </div>
  );
}

export default function FeaturedGuides() {
  const GetStartedIcon = require('../../../static/img/user-guides/home/getting-started.svg').default;
  const TroubleshootingIcon = require('../../../static/img/user-guides/home/troubleshooting.svg').default;
  return (
    <section className={styles.wrapper}>
       <div className="container">
        <div className="row">
          <div className="col">
            <h2 className={styles.title}>Featured guides</h2>
          </div>
        </div>
        <div className="row">
          <div className={clsx('col col--6')}>
            <a href='/docs/user-guides/klipper-setup/' className={clsx('guide-link', styles.guideLink)}>
              <GetStartedIcon className={styles.linkIcon} alt='Set up Obico for Klipper' />
              <div>Set up Obico for Klipper</div>
            </a>
          </div>
          <div className={clsx('col col--6')}>
            <a href='/docs/user-guides/octoprint-plugin-setup/' className={clsx('guide-link', styles.guideLink)}>
              <GetStartedIcon className={styles.linkIcon} alt='Set up Obico for OctoPrint' />
              <div>Set up Obico for OctoPrint</div>
            </a>
          </div>
          <div className={clsx('col col--6')}>
            <a href='/docs/server-guides/' className={clsx('guide-link', styles.guideLink)}>
              <GetStartedIcon className={styles.linkIcon} alt='Self-hosted Obico Server Guides' />
              <div>Self-hosted Obico Server Guides</div>
            </a>
          </div>
          {LinksList.map((props, idx) => (
            <GuideLink key={idx} {...props} />
          ))}
          <div className={clsx('col col--6')}>
            <a href='/docs/user-guides/detective-not-watching/' className={clsx('guide-link', styles.guideLink)}>
              <TroubleshootingIcon className={styles.linkIcon} alt='Why is the Failure Detection Off?' />
              <div>Why is the Failure Detection Off?</div>
            </a>
          </div>
          <div className={clsx('col col--6')}>
            <a href='/docs/user-guides/webcam-feed-is-not-showing/' className={clsx('guide-link', styles.guideLink)}>
              <TroubleshootingIcon className={styles.linkIcon} alt='Troubleshoot the webcam streaming issues' />
              <div>Troubleshoot the webcam streaming issues</div>
            </a>
          </div>
          <div className={clsx('col col--6')}>
            <a href='/docs/user-guides/troubleshoot-server-connection-issues/' className={clsx('guide-link', styles.guideLink)}>
              <TroubleshootingIcon className={styles.linkIcon} alt='Troubleshoot connection issues' />
              <div>Troubleshoot connection issues</div>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
