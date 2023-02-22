import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './help.module.css';
import FeaturedGuides from '../components/FeaturedGuides/index';
import GroupedGuides from '../components/GroupedGuides/index';
import CustomSearchBar from '../components/CustomSearchBar/index';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();

  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <CustomSearchBar />
      </div>
    </header>
  );
}

export default function Home() {
  // const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Obico Knowledge Base"
      description="Access the Obico app knowledge base to learn more about popular topics and find resources that will help you answer any questions you may have.">
      <HomepageHeader />
      <main>
        <FeaturedGuides />
        <GroupedGuides />
      </main>
    </Layout>
  );
}
