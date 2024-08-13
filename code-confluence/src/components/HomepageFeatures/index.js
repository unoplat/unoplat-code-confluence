import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Seamless Collaboration',
    Svg: require('@site/static/img/collab.svg').default,
    description: (
      <>
        Experience seamless collaboration with our cutting-edge platform, 
        where generating summaries of any team member's code is just a click away. 
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    Svg: require('@site/static/img/documentation.svg').default,
    description: (
      <>
        Empower your team with the ability to quickly comprehend 
        and integrate each other's work, boosting productivity and innovation.
      </>
    ),
  },
  {
    title: 'Improve Developer Experience',
    Svg: require('@site/static/img/happy_remote.svg').default,
    description: (
      <>
        Say goodbye to misunderstandings and hello to streamlined workflows, 
        ensuring everyone stays on the same page effortlessly.
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
        <Heading as="h3"> Transforming Code into Plain Language.</Heading>
        <p>
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
