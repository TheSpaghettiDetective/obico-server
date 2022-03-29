import React from 'react';
import styles from './styles.module.css';
import clsx from 'clsx';

function CustomSearchBar() {
  const onOpen = () => {
    document.querySelector('button.DocSearch.DocSearch-Button').click();
  }

  const SearchIcon = require('../../../static/img/search.svg').default;

  return (
    <>
      <div>
        <div
          className={styles.searchBox}
          onClick={onOpen}
        >
          <SearchIcon className={styles.searchIcon} />
          <span className={clsx(styles.searchPlaceholder, styles.desktopPlaceholder)}>Search the knowledge base...</span>
          <span className={clsx(styles.searchPlaceholder, styles.mobilePlaceholder)}>Search...</span>
        </div>
      </div>
    </>
  );
}

export default CustomSearchBar;
