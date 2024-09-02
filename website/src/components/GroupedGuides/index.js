import React from 'react';
import clsx from 'clsx';
import styles from './index.module.css';
import {guideSidebar} from '../../../sidebars'


const GroupedGuides = [
  {
    groupTitle: 'Getting Started',
    Svg: require('../../../static/img/user-guides/home/getting-started.svg').default,
    links: [
      {
        title: 'Set up Obico for Klipper',
        route: '/docs/user-guides/klipper-setup/',
      },
      {
        title: 'Set up Obico for OctoPrint',
        route: '/docs/user-guides/octoprint-plugin-setup/',
      },
      {
        title: 'Self-hosted Obico Server Guides',
        route: '/docs/server-guides/',
      },
    ]
  },
  {
    groupTitle: 'Obico App (Mobile & Web)',
    Svg: require('../../../static/img/user-guides/home/use-the-app.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Obico App (Mobile & Web)',
  },
  {
    groupTitle: 'Failure Detection',
    Svg: require('../../../static/img/user-guides/home/failure-detection.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Failure Detection',
  },
  {
    groupTitle: 'Webcam Streaming',
    Svg: require('../../../static/img/user-guides/home/webcam-streaming.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Webcam Streaming',
  },
  {
    groupTitle: 'Account & Subscription',
    Svg: require('../../../static/img/user-guides/home/account.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Account & Subscription',
  },
  {
    groupTitle: 'Troubleshooting Guides',
    Svg: require('../../../static/img/user-guides/home/troubleshooting.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Troubleshooting Guides',
  },
  {
    groupTitle: 'Obico for OctoPrint',
    Svg: require('../../../static/img/user-guides/home/use-the-app.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Obico for OctoPrint',
  },
  {
    groupTitle: 'Obico for Klipper',
    Svg: require('../../../static/img/user-guides/home/use-the-app.svg').default,
    links: [],
    loadFromSidebar: true,
    labelInSidebar: 'Obico for Klipper',
  },
  {
    groupTitle: 'Get Help',
    Svg: require('../../../static/img/user-guides/home/get-help.svg').default,
    links: [
      {
        title: 'Get help from a human',
        route: '/docs/user-guides/contact-us-for-support',
      },
    ]
  },
]

GroupedGuides.forEach(group => {
  if (!group.links.length && group.loadFromSidebar && group.labelInSidebar) {
    let documents = guideSidebar.filter((category) => {
      if (typeof category !== 'object' || category === null) {
        return false;
      }

      return category.label === group.labelInSidebar
    })

    if (documents.length) {
      documents = documents[0].items
    } else {
      return
    }

    documents.forEach(docPath => {
      addDocToGroup(group, docPath)
    })
  }
});

function addDocToGroup(group, docPath) {
  if (typeof docPath === 'string') {
    const docContents = require(`../../../docs/${docPath}.md`)
    const docTitle = docContents.metadata.title
    group.links.push({
      title: docTitle,
      route: `/docs/${docPath}`,
    })
  } else if (docPath.type === 'category') {
    docPath.items.forEach(subDocPath => {
      addDocToGroup(group, subDocPath)
    })
  }
}

function GuideLink({title, route}) {
  return <a href={route} className={clsx('guide-link', styles.guideLink)}>{title}</a>;
}

function GuideGroup({Svg, groupTitle, index}) {
  return (
    <div className={styles.guideGroup}>
      <div className={styles.groupInfo}>
        <Svg className={styles.groupIcon} alt={groupTitle} />
        <h3 className={styles.groupTitle}>{groupTitle}</h3>
      </div>
      <div className={styles.groupLinks}>
        {GroupedGuides[index].links.map((props, idx) => (
          <GuideLink key={idx} {...props} />
        ))}
      </div>
    </div>
  );
}

export default function ThematicGuides() {
  return (
    <section className={styles.wrapper}>
      {GroupedGuides.map((props, idx) => (
        <GuideGroup key={idx} {...props} index={idx} />
      ))}
    </section>
  );
}
