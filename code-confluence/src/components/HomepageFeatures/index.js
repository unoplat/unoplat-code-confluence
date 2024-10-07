import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Deterministic and language-agnostic code parsing',
    Svg: require('@site/static/img/collab.svg').default,
    description: (
      <>
        Unlock deterministic code parsing with Unoplat Code Confluence. Powered by CHAPI and ANTLR, it seamlessly parses any architecture and programming language. Gain clear, consistent insights into complex codebases, enabling your team to navigate and understand projects with exceptional clarity.
      </>
    ),
  },
  {
    title: 'Automated Code Summarization with State of the art Dspy Pipelines',
    Svg: require('@site/static/img/documentation.svg').default,
    description: (
      <>
        Automatically generate comprehensive documentation covering every aspect of your codebase—including functions, classes, imports, relationships, and more. Our platform organizes this information into an intuitive graph structure that mirrors how developers think, reducing onboarding time to nearly zero and empowering your team to collaborate seamlessly with all the details they need.
      </>
    ),
  },
  {
    title: 'Engage With Your Code Effortlessly',
    Svg: require('@site/static/img/happy_remote.svg').default,
    description: (
      <>
        Interact with one or multiple codebases seamlessly through smart, context-aware chat. Unoplat Code Confluence organizes your code into an intuitive, interconnected system, allowing you to ask questions and instantly access the insights you need. Enhance collaboration and boost your productivity with effortless code exploration tailored to your needs.
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
