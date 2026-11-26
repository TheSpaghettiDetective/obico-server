/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import {translate} from '@docusaurus/Translate';
export default function BlogSidebar({sidebar, tags}) {
  if (sidebar.items.length === 0) {
    return null;
  }

  return (
    <>
      <div className={styles.nozzleNinzaBlock}>
        <h2>JusPrin 2</h2>
        <h3>The AI slicer that helps you get better prints <span className={styles.obicoAccent}>Out now</span></h3>
        <div className={clsx(styles.nozzleNizaBadgeImage, styles.jusprinLockup)}>
          <img className={styles.jusprinCone} src='/img/jusprin-2/jusprin-cone-white.svg' alt=''/>
          <picture>
            <source srcSet='/img/jusprin-2/jusprin-name.png' media='(prefers-reduced-motion: reduce)'/>
            <img className={styles.jusprinName} src='/img/jusprin-2/jusprin-name-animated.webp' alt='JusPrin 2, the AI slicer'/>
          </picture>
        </div>
        <div>
          <a href='/blog/introducing-jusprin-2/'>
            <button className={styles.learnMoreButton}>Check it out</button>
          </a>
        </div>
      </div>
      {tags && tags.length > 0 && (
        <nav
          className={clsx(styles.sidebar, styles.categories)}
          aria-label={translate({
            id: 'theme.blog.sidebar.navAriaLabel',
            message: 'Blog recent posts navigation',
            description: 'The ARIA label for recent posts in the blog sidebar',
          })}>
          <div className={clsx(styles.sidebarItemTitle, 'margin-bottom--md')}>
            Tags
          </div>
          <ul className={styles.sidebarItemList}>
            {tags.map((item, index) => (
              <li key={`tag-${item.permalink}-${index}`} className={styles.sidebarItem}>
                <Link
                  isNavLink
                  to={item.permalink}
                  className={styles.sidebarItemLink}
                  activeClassName={styles.sidebarItemLinkActive}>
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}

      <nav
        className={clsx(styles.sidebar)}
        aria-label={translate({
          id: 'theme.blog.sidebar.navAriaLabel',
          message: 'Blog recent posts navigation',
          description: 'The ARIA label for recent posts in the blog sidebar',
        })}>
        <div className={clsx(styles.sidebarItemTitle, 'margin-bottom--md')}>
          {sidebar.title}
        </div>
        <ul className={styles.sidebarItemList}>
          {sidebar.items.map((item, index) => (
            <li key={`sidebar-${item.permalink}-${index}`} className={styles.sidebarItem}>
              <Link
                isNavLink
                to={item.permalink}
                className={styles.sidebarItemLink}
                activeClassName={styles.sidebarItemLinkActive}>
                {item.title}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </>
  );
}
