import { motion } from 'framer-motion';
import { FiArrowUpRight } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const TeamSection = () => {
  const { t } = useTranslation();

  const teamMembers = [
    {
      name: 'Cody',
      title: t('team_section.ceo_role'),
      image: '/team/cody-outcast.jpg',
      bio: t('team_section.ceo_bio'),
      link: 'https://www.linkedin.com/in/zhuokaichen',
      width: 1279,
      height: 1706,
    },
    {
      name: 'William',
      title: t('team_section.coo_role'),
      image: '/team/william-kusnomo.jpg',
      bio: t('team_section.coo_bio'),
      link: 'https://www.linkedin.com/in/williamjkkkk',
      width: 1076,
      height: 1032,
    },
    {
      name: 'Irene',
      title: t('team_section.cmo_role'),
      image: '/team/irene-chen.png',
      bio: t('team_section.cmo_bio'),
      link: 'https://x.com/imIreneChen',
      width: 784,
      height: 1168,
    },
    {
      name: 'Zhuoheng',
      title: t('team_section.cto_role'),
      image: '/team/zhuoheng-chen.png',
      bio: t('team_section.cto_bio'),
      link: 'https://ieeexplore.ieee.org/author/941313259273488',
      width: 1200,
      height: 1600,
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

      <div className="team-grid">
        {teamMembers.map((member, index) => (
          <motion.article
            className="team-profile"
            key={member.name}
            initial={{ opacity: 0, y: 42 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-8%' }}
            transition={{
              duration: 0.75,
              delay: index * 0.07,
              ease: [0.16, 1, 0.3, 1],
            }}
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
                <span className="team-profile__portrait-shine" aria-hidden="true" />
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
          </motion.article>
        ))}
      </div>
    </section>
  );
};

export default TeamSection;
