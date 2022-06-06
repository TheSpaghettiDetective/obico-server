import React from 'react';
import clsx from 'clsx';
import styles from './index.module.css';

const LinksList = [
  {
    title: 'Why is the AI failure detection off?',
    route: '/docs/user-guides/detective-not-watching/',
  },
  {
    title: 'What is AI Detection Hour and how does it work?',
    route: '/docs/user-guides/how-does-detective-hour-work/',
  },
  {
    title: 'Troubleshoot Choppy/Jerky Premium Streaming',
    route: '/docs/user-guides/webcam-feed-is-laggy/',
  },
  {
    title: 'The Pro plan vs the Free plan',
    route: '/docs/user-guides/upgrade-to-pro/',
  },
  {
    title: 'I want to help The Detective get better at her job. How can I do it?',
    route: '/docs/user-guides/how-does-credits-work/',
  },
  {
    title: 'Two modes in the Premium Streaming',
    route: '/docs/user-guides/streaming-compatibility-mode/',
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
  const Icon = require('../../../static/img/user-guides/home/get-started.svg').default;
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
            <a href='/docs/user-guides/octoprint-plugin-setup' className={clsx('guide-link', styles.guideLink)}>
              <Icon className={styles.linkIcon} alt='Getting Started with the Obico app' />
              <div>Getting Started with the Obico app</div>
            </a>
          </div>
          {LinksList.map((props, idx) => (
            <GuideLink key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
