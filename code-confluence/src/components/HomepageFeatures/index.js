import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Deterministic Language-Agnostic Code Parsing',
    Svg: require('@site/static/img/collab.svg').default,
    description: (
      <>
        Unoplat-CodeConfluence employs a deterministic, language-agnostic parser to analyze and interpret codebases across any programming language or framework without relying on AI. 
        This ensures precise code context understanding by generating structured JSON representations of the code's essential constructs. 
      </>
    ),
  },
  {
    title: 'Enhanced Metadata Generation and LLM Integration',
    Svg: require('@site/static/img/documentation.svg').default,
    description: (
      <>
        The tool transforms the parsed JSON into an optimized data model, enriching metadata for better code representation. 
        It integrates with customizable LLM pipelines, allowing users to select preferred open-source or commercial models for generating summaries at the function, class, package, and codebase levels.
      </>
    ),
  },
  {
    title: 'Efficient and Compliant Code Understanding',
    Svg: require('@site/static/img/happy_remote.svg').default,
    description: (
      <>
        By avoiding reliance on external AI services and embeddings, Unoplat-CodeConfluence offers an efficient solution that overcomes common AI tool limitations like limited context windows and high operational costs. 
        This approach also addresses compliance and security concerns, providing a detailed and navigable code representation for accurate and swift code comprehension.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
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
