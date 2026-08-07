import { motion } from 'framer-motion';
import { FiMail, FiMapPin, FiPhone } from 'react-icons/fi';
import {
  FaFacebookF,
  FaInstagram,
  FaLinkedinIn,
  FaTiktok,
  FaXTwitter,
  FaYoutube,
} from 'react-icons/fa6';
import { useTranslation } from 'react-i18next';

const ContactSection = () => {
  const { t } = useTranslation();

  const socialLinks = [
    { href: 'https://x.com/GeoSeeer', label: 'X', icon: FaXTwitter },
    { href: 'https://www.instagram.com/geoseeer/', label: 'Instagram', icon: FaInstagram },
    { href: 'https://www.tiktok.com/@geoseeer', label: 'TikTok', icon: FaTiktok },
    { href: 'https://www.facebook.com/profile.php?id=61583773556872', label: 'Facebook', icon: FaFacebookF },
    { href: 'https://www.youtube.com/@geoseeer', label: 'YouTube', icon: FaYoutube },
    { href: 'https://www.linkedin.com/company/geoseer', label: 'LinkedIn', icon: FaLinkedinIn },
  ];

  return (
    <section id="contact" data-section="contact" className="contact-section section-shell">
      <div className="contact-section__orb" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>

      <motion.div
        className="contact-heading"
        initial={{ opacity: 0, y: 36 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-12%' }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
      >
        <h2 className="section-title">{t('contact_section.title')}</h2>
        <p>{t('contact_section.subtitle')}</p>
      </motion.div>

      <motion.div
        className="contact-panel"
        initial={{ opacity: 0, y: 44 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-8%' }}
        transition={{ duration: 0.95, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="contact-panel__main">
          <div className="contact-detail">
            <FiMail aria-hidden="true" />
            <div>
              <span>{t('contact_section.email_label')}</span>
              <a href="mailto:support@quesx.com">support@quesx.com</a>
            </div>
          </div>

          <div className="contact-detail">
            <FiPhone aria-hidden="true" />
            <div>
              <span>{t('about_section.contact_title')}</span>
              <a href={`tel:${t('about_section.contact_value')}`}>
                {t('about_section.contact_value')}
              </a>
            </div>
          </div>

          <div className="contact-detail contact-detail--address">
            <FiMapPin aria-hidden="true" />
            <div>
              <span>{t('about_section.address_title')}</span>
              <p>{t('about_section.address_value')}</p>
            </div>
          </div>
        </div>

        <div className="contact-panel__social">
          <span>{t('contact_section.social_media')}</span>
          <div>
            {socialLinks.map(({ href, label, icon: Icon }) => (
              <a
                key={label}
                href={href}
                aria-label={label}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Icon aria-hidden="true" />
              </a>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default ContactSection;
