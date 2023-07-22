/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
import ObicoAppPreview from'./3-screens-obico-app-preview.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
  import { faXmark } from '@fortawesome/free-solid-svg-icons'

export default function BlogAd() {

  const [showSidebarAd, setShowSidebarAd] = React.useState(false);

  const [showPopup, setShowPopup] = React.useState(false);
  const [popupHiddenByUser, setPopupHiddenByUser] = React.useState(false);

  React.useEffect(() => {

    // In dev environement these errors are quite often, not sure about production so I created this check
    if (!posthog) {
      console.error("Posthog is not defined.")
      return
    }
    if (!posthog.onFeatureFlags) {
      console.error("Posthog onFeatureFlags is not defined.")
      return
    }

    posthog.onFeatureFlags(function() {
      if (posthog.getFeatureFlag('ab_test_blog_ad')  == 'test') {
        setShowSidebarAd(true);

        const handleScroll = () => {
          const { offsetHeight } = document.querySelector('.main-wrapper');
          if ((window.scrollY + window.innerHeight) >= offsetHeight) {
            setShowPopup(true);
          }
        }
        window.addEventListener('scroll', handleScroll, { passive: true });
      }
    })
    
  }, [])

  const hidePopup = () => {
    setPopupHiddenByUser(true);
  }

  return showSidebarAd ? (
    <>
    <div className={clsx(styles.signupSidebar)}>
      <h3 className={clsx(styles.signupTitle)}>The ultimate smart 3D printing platform for OctoPrint and Klipper.</h3>
      <img className={clsx(styles.signupImage)} src={ObicoAppPreview} alt="Obico App Preview" />
      <a href="https://app.obico.io/accounts/signup/?utm_source=sidebar_learn_more&utm_medium=blog&utm_campaign=0717202" className={clsx(styles.buttonPrimary)}>Get Started</a>
      <small className={clsx(styles.signupSmall)}>No credit card required</small>
      <a href="https://obico.io/?utm_source=sidebar_learn_more&utm_medium=blog&utm_campaign=07172023" className={clsx(styles.buttonPrimary)}>Learn More</a>
    </div>
    {(showPopup && !popupHiddenByUser) && (
      <div className={clsx(styles.popupWrapper)} onClick={hidePopup}>
        <div className={clsx(styles.popupInner)} onClick={(e) => e.stopPropagation()}>
          <button className={clsx(styles.popupCloseBtn)} onClick={hidePopup}><FontAwesomeIcon icon={faXmark} /></button>

          <h2 className={clsx(styles.popupTitle)}>The ultimate smart 3D printing platform for OctoPrint and Klipper.</h2>

          <img className={clsx(styles.popupImage)} src={ObicoAppPreview} alt="Obico App Preview" />

          <div className={clsx(styles.popupButtons)}>
            <div className={clsx(styles.popupButtonGroup)}>
              <a href="https://app.obico.io/accounts/signup/?utm_source=sidebar_learn_more&utm_medium=blog&utm_campaign=0717202" className={clsx(styles.buttonPrimary)}>Get Started</a>
              <small className={clsx(styles.signupSmall)}>No credit card required</small>
            </div>

            <div className={clsx(styles.popupButtonGroup)}>
              <a href="https://obico.io/?utm_source=sidebar_learn_more&utm_medium=blog&utm_campaign=07172023" className={clsx(styles.buttonPrimary)}>Learn More</a>
            </div>
          </div>
        </div>
      </div>
    )}
    </>
  ) : null;
}
