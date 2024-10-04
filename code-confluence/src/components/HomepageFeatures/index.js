import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Deterministic and language-agnostic code parsing',
    Svg: require('@site/static/img/collab.svg').default,
    description: (
      <>
        Experience deterministic code parsing like never before. Unoplat Code Confluence extends CHAPI with ANTLR grammar 
        to parse codebases across any architecture and programming language. Gain a consistent and precise understanding of complex codebases, 
        enabling your team to navigate and comprehend projects with unparalleled clarity.
      </>
    ),
  },
  {
    title: 'Automated Code Summarization with State of the art Dspy Pipelines',
    Svg: require('@site/static/img/documentation.svg').default,
    description: (
      <>
        Accelerate onboarding and enhance collaboration. Our platform utilizes state-of-the-art LLM pipelines 
        to generate detailed objectives and summaries for every function, class, package, and the entire codebase in a depth-first search
        fashion. This comprehensive documentation is created automatically, reducing onboarding time to almost zero and empowering
        cross-team synergy.
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    Svg: require('@site/static/img/happy_remote.svg').default,
    description: (
      <>
        Engage with your codebase/s through grounded and context-aware chat. By ingesting code information into a graph database, 
        Unoplat Code Confluence provides an optimal representation of code relationships. Interact with your codebase using intuitive TUI
        and chat with your codebase using advanced LLM pipelines and Graph Retrieval Augmented Generation (GraphRAG), 
        allowing for intuitive querying to retrieve context-specific information swiftly.
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
