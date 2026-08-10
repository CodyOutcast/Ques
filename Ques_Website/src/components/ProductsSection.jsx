import { motion } from 'framer-motion';
import { FiArrowUpRight } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const ProductsSection = () => {
  const { t } = useTranslation();

  const features = [
    t('products_section.geoseer_feature_1'),
    t('products_section.geoseer_feature_2'),
    t('products_section.geoseer_feature_3'),
    t('products_section.geoseer_feature_4'),
    t('products_section.geoseer_feature_5'),
    t('products_section.geoseer_feature_6'),
  ];

  return (
    <div className="products-section section-shell">
      <motion.h2
        className="section-title products-section__title"
        initial={{ opacity: 0, y: 36 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-10%' }}
        transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
      >
        {t('products_section.title')}
      </motion.h2>

      <div className="product-showcase">
        <motion.div
          className="product-showcase__copy"
          initial={{ opacity: 0, x: -36 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-12%' }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="product-brand">
            <span className="product-brand__mark">
              <img
                src="/products/geoseer/logo-256.webp"
                alt=""
                width="256"
                height="256"
                loading="lazy"
                decoding="async"
              />
            </span>
            <div>
              <h3>{t('products_section.geoseer_title')}</h3>
              <p>{t('products_section.geoseer_tagline')}</p>
            </div>
          </div>

          <p className="product-description">
            {t('products_section.geoseer_description')}
          </p>

          <a
            href="https://geoseeer.com"
            target="_blank"
            rel="noopener noreferrer"
            className="premium-link"
          >
            <span>{t('products_section.visit_website')}</span>
            <FiArrowUpRight aria-hidden="true" />
          </a>
        </motion.div>

        <motion.div
          className="product-artwork"
          aria-hidden="true"
          initial={{ opacity: 0, y: 52, rotateX: 8 }}
          whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
          viewport={{ once: true, margin: '-10%' }}
          transition={{ duration: 1.05, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="product-artwork__glow" />
          <div className="product-shot product-shot--analysis">
            <img
              src="/products/geoseer/screenshots/analysis-1440.webp"
              alt=""
              width="1440"
              height="810"
              loading="lazy"
              decoding="async"
            />
          </div>
          <div className="product-shot product-shot--input">
            <img
              src="/products/geoseer/screenshots/input-1440.webp"
              alt=""
              width="1440"
              height="816"
              loading="lazy"
              decoding="async"
            />
          </div>
          <div className="product-shot product-shot--result">
            <img
              src="/products/geoseer/screenshots/result-1440.webp"
              alt=""
              width="1440"
              height="811"
              loading="lazy"
              decoding="async"
            />
          </div>
          <div className="product-artwork__current" aria-hidden="true" />
        </motion.div>
      </div>

      <motion.div
        className="product-capabilities"
        initial={{ opacity: 0, y: 32 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-8%' }}
        transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
      >
        <h4>{t('products_section.geoseer_features_title')}</h4>
        <div className="product-capabilities__grid">
          {features.map((feature) => (
            <div
              key={feature}
              className="capability-row"
            >
              <span className="capability-row__signal" aria-hidden="true" />
              <p>{feature}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default ProductsSection;
