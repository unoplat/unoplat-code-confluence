import styles from './styles.module.css';
export default function Footer() {
    return (
        <footer className={`footer ${styles.footerColor}`}>
            <div class="container container--fluid">
                <div class="row footer__links">
                <div class="col footer__col">
                    <h4 class="footer__title">Docs</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Introduction</a>
                    </li>
                    
                    </ul>
                </div>
                <div class="col footer__col">
                    <h4 class="footer__title">Community</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Discord</a>
                    </li>
                    
                    </ul>
                </div>
                <div class="col footer__col">
                    <h4 class="footer__title">Social</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">GitHub</a>
                    </li>
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Twitter</a>
                    </li>
                    </ul>
                </div>
                <div class="col footer__col">
                    <h4 class="footer__title">Legal</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Privacy</a>
                    </li>
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Terms</a>
                    </li>
                    </ul>
                </div>
                </div>
                <div class="text--center">
                
                Copyright © 2024 Code Confluence, Inc.
                </div>
            </div>
        </footer>
        )

}