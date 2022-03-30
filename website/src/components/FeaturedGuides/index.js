import React from 'react';
import clsx from 'clsx';
import styles from './index.module.css';

const LinksList = [
  {
    title: 'Why is The Detective "not watching"?',
    route: '/docs/user_guides/detective-not-watching/',
  },
  {
    title: 'Why is OctoPrint showing as "offline"?',
    route: '/docs/user_guides/octoprint-is-offline/',
  },
  {
    title: 'What is Detective Hour and how does it work?',
    route: '/docs/user_guides/how-does-detective-hour-work/',
  },
  {
    title: 'Troubleshoot Choppy/Jerky Premium Streaming',
    route: '/docs/user_guides/webcam-feed-is-laggy/',
  },
  {
    title: 'Set up your own TSD private server',
    route: '/docs/user_guides/open-source/',
  },
  {
    title: 'The Pro plan vs the Free plan',
    route: '/docs/user_guides/upgrade-to-pro/',
  },
  {
    title: 'I want to help The Detective get better at her job. How can I do it?',
    route: '/docs/user_guides/how-does-credits-work/',
  },
  {
    title: 'Two modes in the Premium Streaming',
    route: '/docs/user_guides/streaming-compatibility-mode/',
  },
];

function GuideLink({title, route}) {
  const Icon = require('../../../static/img/user_guides/home/guide-icon.svg').default;

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
  const Icon = require('../../../static/img/user_guides/home/get-started.svg').default;
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
            <a href='/docs/user_guides/octoprint-plugin-setup' className={clsx('guide-link', styles.guideLink)}>
              <Icon className={styles.linkIcon} alt='Getting Started with The Spaghetti Detective' />
              <div>Getting Started with The Spaghetti Detective</div>
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
