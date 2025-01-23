import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import { useState, useEffect, useRef } from 'react';

const FeatureList = [
  {
    title: 'Deterministic and language-agnostic code parsing',
    Svg: require('@site/static/img/arch_chapi_tree_sitter.svg').default,
    description: (
      <>
        Decode any codebase with unmatched clarity using Unoplat Code Confluence. Our powerful combination of ArchGuard, CHAPI, Tree-sitters, linters and inhouse data structures and algorithms delivers deterministic parsing across all programming languages and architectures. Get consistent, reliable insights that make complex projects instantly understandable. Transform how your team navigates and comprehends code, enabling smarter, faster development decisions.
      </>
    ),
    imgStyle: {
      width: '100%',
      height: 'auto',
      maxWidth: '800px'
    }
  },
  {
    title: 'Automated Code Summarization with State of the art LLM Pipelines',
    Svg: require('@site/static/img/automatic_documentation.svg').default,
    description: (
      <>
        Turn your codebase into an interactive knowledge map where every component is instantly discoverable. Unoplat automatically documents all functions, classes, and dependencies while revealing their connections in intuitive graphs. New team members can dive right in, while seasoned developers make confident contributions with full context at their fingertips. From understanding code to shipping features—we make it seamless.
      </>
    ),
    imgStyle: {
      width: '100%', 
      height: 'auto',
      maxWidth: '800px'
    }
  },
  {
    title: 'Integration with Knowledge Engines and Copilots',
    Svg: require('@site/static/img/integration_tooling.svg').default,
    description: (
      <>
      Supercharge your AI stack with deterministic code understanding. Our self-hosted, open-source platform seamlessly integrates with knowledge engines and copilots, delivering domain-aware insights across your codebases. Built for cloud-native enterprises, it offers enterprise-grade scalability, reliability, and security while keeping you in full control of your data and infrastructure. Empower your AI tools to truly comprehend your organization's unique code ecosystem—and unlock new levels of innovation.
      </>
    ),
    imgStyle: {
      width: '100%',
      height: 'auto', 
      maxWidth: '800px'
    }
  },
];
// Add ImageModal component
function ImageModal({ isOpen, onClose, children }) {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    let timeoutId;
    if (isOpen) {
      // Small delay before showing to prevent accidental triggers
      timeoutId = setTimeout(() => {
        setIsVisible(true);
      }, 100); // 200ms delay before showing
    } else {
      setIsVisible(false);
    }
    return () => clearTimeout(timeoutId);
  }, [isOpen]);

  if (!isOpen) return null;
  
  return (
    <div 
      className={`${styles.modalOverlay} ${isVisible ? styles.show : ''}`} 
      onClick={onClose}
    >
      <div className={`${styles.modalContent} ${isVisible ? styles.show : ''}`}>
        {children}
      </div>
    </div>
  );
}


function Feature({ Svg, title, description, imgStyle }) {
  const [showModal, setShowModal] = useState(false);
  const hoverTimeoutRef = useRef(null);

  const handleMouseEnter = () => {
    hoverTimeoutRef.current = setTimeout(() => {
      setShowModal(true);
    }, 500); // 500ms hover delay before showing modal
  };

  const handleMouseLeave = () => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }
    setShowModal(false);
  };

  return (
    <div className={clsx('col col--4')}>
      <div 
        className="text--center"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <Svg style={imgStyle} role="img" />
        <ImageModal 
          isOpen={showModal} 
          onClose={() => setShowModal(false)}
        >
          <Svg style={{ width: '100%', maxWidth: '1200px' }} role="img" />
        </ImageModal>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <div className={styles.lessWidth}>
      <section className={styles.advertise}>
        <Heading as="h3" className={styles.paddingLeftRight}> Transforming Code into Plain Language.</Heading>
        <p className={styles.paddingLeftRight}>
          Centralize your knowledge base, empowering employees to find answers quickly and become more efficient.
        </p>
      </section>
      <section className={styles.features}>
        <div className="container">
          <div className="row">
            {FeatureList.map((props, idx) => (
              <Feature key={idx} {...props} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
