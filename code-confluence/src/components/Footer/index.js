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
                        <a class="footer__link-item" href="/unoplat-code-confluence/docs/">Introduction</a>
                    </li>
                    
                    </ul>
                </div>
                <div class="col footer__col">
                    <h4 class="footer__title">Community</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="https://discord.com/channels/1131597983058755675/1169968780953260106">Discord</a>
                    </li>
                    
                    </ul>
                </div>
                <div class="col footer__col">
                    <h4 class="footer__title">Social</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="https://github.com/unoplat/unoplat-code-confluence">GitHub</a>
                    </li>
                    <li class="footer__item">
                        <a class="footer__link-item" href="https://x.com/unoplatio">Twitter</a>
                    </li>
                    </ul>
                </div>
                {/* <div class="col footer__col">
                    <h4 class="footer__title">Legal</h4>
                    <ul class="footer__items clean-list">
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Privacy</a>
                    </li>
                    <li class="footer__item">
                        <a class="footer__link-item" href="#url">Terms</a>
                    </li>
                    </ul>
                </div> */}
                </div>
                <div class="text--center">
                
                Copyright © 2024 Unoplat Technologies, Private Limited.
                </div>
            </div>
        </footer>
        )

}