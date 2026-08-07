import { useTranslation } from 'react-i18next';

const Footer = () => {
  const { t } = useTranslation();

  return (
    <footer className="site-footer">
      <div className="site-footer__line" aria-hidden="true" />
      <div className="site-footer__inner">
        <span>{t('footer.company')}</span>
        <div className="site-footer__legal">
          <a
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener noreferrer"
          >
            {t('footer.icp')}
          </a>
          <a
            href="https://beian.mps.gov.cn/#/query/webSearch?code=44030002008139"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src="/legal/police-badge.png"
              alt=""
              width="14"
              height="16"
              loading="lazy"
              decoding="async"
            />
            <span>粤公网安备44030002008139号</span>
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
