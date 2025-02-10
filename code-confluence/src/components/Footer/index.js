import styles from './styles.module.css';

export default function Footer() {
    return (
        <footer className={`footer ${styles.footerColor}`}>
            <div className="container container--fluid">
                <div className="row footer__links">
                    <div className="col footer__col">
                        <h4 className="footer__title">Docs</h4>
                        <ul className="footer__items clean-list">
                            <li className="footer__item">
                                <a className="footer__link-item" href="/docs/quickstart/how-to-run">
                                    Quick Start Guide
                                </a>
                            </li>
                            <li className="footer__item">
                                <a className="footer__link-item" href="/docs/deep-dive/vision">
                                    Vision
                                </a>
                            </li>
                        </ul>
                    </div>
                    <div className="col footer__col">
                        <h4 className="footer__title">Community</h4>
                        <ul className="footer__items clean-list">
                            <li className="footer__item">
                                <a className="footer__link-item" href="https://discord.com/channels/1131597983058755675/1169968780953260106">
                                    Discord
                                </a>
                            </li>
                        </ul>
                    </div>
                    <div className="col footer__col">
                        <h4 className="footer__title">Social</h4>
                        <ul className="footer__items clean-list">
                            <li className="footer__item">
                                <a className="footer__link-item" href="https://github.com/unoplat/unoplat-code-confluence">
                                    GitHub
                                </a>
                            </li>
                            <li className="footer__item">
                                <a className="footer__link-item" href="https://x.com/unoplatio">
                                    Twitter
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
                <div className="text--center" style={{ color: 'rgba(17, 16, 17, 0.8)' }}>
                    Copyright © {new Date().getFullYear()} Unoplat Technologies, Private Limited.
                </div>
            </div>
        </footer>
    );
}