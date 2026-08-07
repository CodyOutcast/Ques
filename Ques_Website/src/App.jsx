import { useEffect, useState } from 'react';
import { MotionConfig } from 'framer-motion';
import Header from './components/Header';
import Footer from './components/Footer';
import HomeSection from './components/HomeSection';
import AboutSection from './components/AboutSection';
import ProductsDemoSection from './components/ProductsDemoSection';
import ProductsSection from './components/ProductsSection';
import TeamSection from './components/TeamSection';
import ContactSection from './components/ContactSection';
import './i18n';
import './viewportFix.css';
import i18n from 'i18next';

const SECTION_IDS = ['home', 'about', 'products', 'team', 'contact'];

export default function App() {
    const [isChinese, setIsChinese] = useState(i18n.language === 'cn');
    const [activeSection, setActiveSection] = useState('home');

    useEffect(() => {
        const sections = SECTION_IDS
            .map((id) => document.getElementById(id))
            .filter(Boolean);

        let frameId = 0;
        const updateActiveSection = () => {
            frameId = 0;
            const marker = window.innerHeight * 0.34;
            let currentSection = sections[0]?.id ?? 'home';

            sections.forEach((section) => {
                if (section.getBoundingClientRect().top <= marker) {
                    currentSection = section.id;
                }
            });

            if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
                currentSection = sections.at(-1)?.id ?? currentSection;
            }

            setActiveSection((current) => current === currentSection ? current : currentSection);
        };

        const queueUpdate = () => {
            if (!frameId) frameId = window.requestAnimationFrame(updateActiveSection);
        };

        updateActiveSection();
        window.addEventListener('scroll', queueUpdate, { passive: true });
        window.addEventListener('resize', queueUpdate);

        return () => {
            window.removeEventListener('scroll', queueUpdate);
            window.removeEventListener('resize', queueUpdate);
            if (frameId) window.cancelAnimationFrame(frameId);
        };
    }, []);

    useEffect(() => {
        document.documentElement.classList.add('is-hydrated');
        document.documentElement.lang = isChinese ? 'zh-CN' : 'en';
    }, [isChinese]);

    const toggleLanguage = () => {
        const newLang = isChinese ? 'en' : 'cn';
        i18n.changeLanguage(newLang);
        setIsChinese((current) => !current);
    };

    const handleNavigate = (sectionId) => {
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        setActiveSection(sectionId);
        document.getElementById(sectionId)?.scrollIntoView({
            behavior: reduceMotion ? 'auto' : 'smooth',
            block: 'start',
        });
    };

    return (
        <MotionConfig reducedMotion="user">
            <div className="site-shell">
                <div className="global-aurora" aria-hidden="true">
                    <span className="global-aurora__orb global-aurora__orb--one" />
                    <span className="global-aurora__orb global-aurora__orb--two" />
                </div>

                <Header
                    isChinese={isChinese}
                    toggleLanguage={toggleLanguage}
                    onNavigate={handleNavigate}
                    activeSection={activeSection}
                />

                <main>
                    <HomeSection />
                    <AboutSection />

                    <section id="products" data-section="products" className="product-chapter">
                        <ProductsSection />
                        <ProductsDemoSection />
                    </section>

                    <TeamSection />
                    <ContactSection />
                </main>

                <Footer />
            </div>
        </MotionConfig>
    );
}
