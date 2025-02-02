import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import { useState, useEffect, useRef } from 'react';

const FeatureList = [
  {
    title: 'Deterministic and Language-Agnostic Code Analysis',
    Svg: require('@site/static/img/arch_chapi_tree_sitter.svg').default,
    description: (
      <>
        <div className={styles.featurePoints}>
          <div className={styles.featurePoint}>
            <strong>🎯 Deterministic Parsing</strong>
            <p>Advanced parsing techniques powered by <a href="https://archguard.org" className={styles.inlineLink}>ArchGuard</a> and <a href="https://tree-sitter.github.io/tree-sitter/" className={styles.inlineLink}>Treesitters</a> ensure consistent and reliable insights across all programming languages.</p>
          </div>
          
          <div className={styles.featurePoint}>
            <strong>🔍 Intelligent Linting</strong>
            <p><a href="https://www.sonarsource.com/learn/linter" className={styles.inlineLink}>Linters</a> maintain code quality and eliminate code smells and ambiguities, ensuring consistent and reliable insights.</p>
          </div>
          
          <div className={styles.featurePoint}>
            <strong>📦 Smart Dependency Resolution</strong>
            <p>Deep parsing and understanding of <a href="https://devopedia.org/package-manager" className={styles.inlineLink}>package manager's</a> data reveals project structure and library relationships, both internal and external.</p>
          </div>
        </div>
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
        <div className={styles.featurePoints}>
          <div className={styles.featurePoint}>
            <strong>🔄 Bottom-Up Summarization</strong>
            <p>Hierarchical deterministic summarization from functions to entire codebases, ensuring precise and contextual understanding at every level.</p>
          </div>
          
          <div className={styles.featurePoint}>
            <strong>🚀 Enhanced Onboarding</strong>
            <p>New team members can quickly understand complex codebases through intuitive, interconnected documentation at every level of a codebase and explore connected codebases through Domains.</p>
          </div>
          
          <div className={styles.featurePoint}>
            <strong>💬 Interactive Code Intelligence</strong>
            <p>Query and explore your codebase through intelligent mapping of repositories, codebases, packages, classes, and function calls in their true <a href="https://neo4j.com/whitepapers/knowledge-graphs-unlimited-insights/" className={styles.inlineLink}>graphical</a> form, making information retrieval natural and efficient.</p>
          </div>
        </div>
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
        <div className={styles.featurePoints}>
          <div className={styles.featurePoint}>
            <strong>🔌 Seamless Ecosystem Integration</strong>
            <p>Working closely with developer tools like copilots/ides and knowledge engines to deliver insights seamlessly within your workflow, reducing cognitive load and maximizing productivity through contextual assistance.</p>
          </div>
          
          <div className={styles.featurePoint}>
            <strong>🤝 Enterprise-Ready</strong>
            <p>Built for cloud-native enterprises with self-hosted deployment options, offering enterprise-grade scalability, reliability, and security while maintaining full data control.</p>
          </div>
          
          
        </div>
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
      timeoutId = setTimeout(() => {
        setIsVisible(true);
      }, 100);
    } else {
      setIsVisible(false);
    }

    // Enhanced event handler for better cross-browser compatibility
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' || event.key === 'Esc' || event.keyCode === 27) {
        event.preventDefault(); // Prevent default browser behavior
        onClose();
      }
    };

    if (isOpen) {
      // Capture phase to ensure we get the event before other handlers
      document.addEventListener('keydown', handleEscapeKey, true);
    }

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('keydown', handleEscapeKey, true);
    };
  }, [isOpen, onClose]);

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
        <Heading as="h2" className={styles.paddingLeftRight}>Empower Your Code: From Static Syntax to Dynamic Dialogue.</Heading>
        <p className={styles.paddingLeftRight}>
          Centralize your siloed codebases across your organization, empowering all stakeholders.
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
