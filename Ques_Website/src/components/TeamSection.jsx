import { motion } from 'framer-motion';
import { FiArrowUpRight } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const TeamSection = () => {
  const { t } = useTranslation();

  const teamMembers = [
    {
      name: 'Cody',
      title: t('team_section.ceo_role'),
      image: '/team/cody-outcast-720.webp',
      bio: t('team_section.ceo_bio'),
      link: 'https://www.linkedin.com/in/zhuokaichen',
      width: 720,
      height: 961,
    },
    {
      name: 'William',
      title: t('team_section.coo_role'),
      image: '/team/william-kusnomo-720.webp',
      bio: t('team_section.coo_bio'),
      link: 'https://www.linkedin.com/in/williamjkkkk',
      width: 720,
      height: 691,
    },
    {
      name: 'Irene',
      title: t('team_section.cmo_role'),
      image: '/team/irene-chen-720.webp',
      bio: t('team_section.cmo_bio'),
      link: 'https://x.com/imIreneChen',
      width: 720,
      height: 1073,
    },
    {
      name: 'Zhuoheng',
      title: t('team_section.cto_role'),
      image: '/team/zhuoheng-chen-720.webp',
      bio: t('team_section.cto_bio'),
      link: 'https://ieeexplore.ieee.org/author/941313259273488',
      width: 720,
      height: 960,
    },
  ];

  return (
    <section id="team" data-section="team" className="team-section section-shell">
      <div className="team-heading">
        <motion.h2
          className="section-title"
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-10%' }}
          transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
        >
          {t('team_section.title')}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-10%' }}
          transition={{ duration: 0.75, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
        >
          {t('team_section.tagline')}
        </motion.p>
      </div>

      <motion.div
        className="team-grid"
        initial={{ opacity: 0, y: 36 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-8%' }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        {teamMembers.map((member) => (
          <article
            className="team-profile"
            key={member.name}
          >
            <a href={member.link} target="_blank" rel="noopener noreferrer">
              <div className="team-profile__portrait">
                <img
                  src={member.image}
                  alt={member.name}
                  width={member.width}
                  height={member.height}
                  loading="lazy"
                  decoding="async"
                />
              </div>

              <div className="team-profile__heading">
                <div>
                  <h3>{member.name}</h3>
                  <p>{member.title}</p>
                </div>
                <FiArrowUpRight aria-hidden="true" />
              </div>

              <p className="team-profile__bio">{member.bio}</p>
            </a>
          </article>
        ))}
      </motion.div>
    </section>
  );
};

export default TeamSection;
