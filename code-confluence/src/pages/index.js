import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Svg from '@site/static/img/confluence_logo.svg'; 
import Heading from '@theme/Heading';
import styles from './index.module.css';
import Footer from '../components/Footer';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner, styles.blackText)}>
      <div className="container">
        {/* <Svg role="img" /> */}
        <Heading as="h1" className="hero__title gradient-text">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        
        <div className={styles.buttons}>
          <Link
            className={clsx(
              'button button--secondary button--lg',
              styles.getStarted,
            )}
            to="/docs/quickstart/how-to-run">
            🚀 Quick Start Guide - 5min ⏱️
          </Link>
          <Link
            className={clsx(
              'button button--outline button--lg',
              styles.learnMore,
            )}
            to="/docs/deep-dive/roadmap">
            📍 View Roadmap
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main className={styles.mainContainer}>
        <HomepageFeatures />
      </main>
      <Footer/>
    </Layout>
  );
}
