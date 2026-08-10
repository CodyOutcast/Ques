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
import GenerativeField from './components/GenerativeField';
import InferenceRoute from './components/InferenceRoute';
import LowerNarrative from './components/LowerNarrative';
import './i18n';
import './viewportFix.css';
import i18n from 'i18next';

const SECTION_IDS = ['home', 'about', 'products', 'team', 'contact'];
const LANGUAGE_STORAGE_KEY = 'ques-language';

export default function App() {
    const [isChinese, setIsChinese] = useState(i18n.language === 'cn');
    const [activeSection, setActiveSection] = useState('home');

    useEffect(() => {
        const sections = SECTION_IDS
            .map((id) => document.getElementById(id))
            .filter(Boolean);

        if (!sections.length) return undefined;

        const observer = new IntersectionObserver((entries) => {
            const activeEntry = entries.find(
                (entry) => entry.isIntersecting && entry.intersectionRatio > 0,
            );

            if (!activeEntry) return;
            setActiveSection((current) => (
                current === activeEntry.target.id ? current : activeEntry.target.id
            ));
        }, {
            rootMargin: '-33% 0px -66% 0px',
            threshold: 0,
        });

        sections.forEach((section) => observer.observe(section));

        return () => {
            observer.disconnect();
        };
    }, []);

    useEffect(() => {
        document.documentElement.classList.add('is-hydrated');
        document.documentElement.lang = isChinese ? 'zh-CN' : 'en';
    }, [isChinese]);

    useEffect(() => {
        try {
            const savedLanguage = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
            if (!['en', 'cn'].includes(savedLanguage) || savedLanguage === i18n.language) return;
            i18n.changeLanguage(savedLanguage);
            setIsChinese(savedLanguage === 'cn');
        } catch {
            // Storage may be unavailable in privacy-restricted browsing contexts.
        }
    }, []);

    const toggleLanguage = () => {
        const newLang = isChinese ? 'en' : 'cn';
        i18n.changeLanguage(newLang);
        setIsChinese((current) => !current);
        try {
            window.localStorage.setItem(LANGUAGE_STORAGE_KEY, newLang);
        } catch {
            // The language still changes for the current session when storage is blocked.
        }
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
                <GenerativeField />
                <InferenceRoute />

                <Header
                    isChinese={isChinese}
                    toggleLanguage={toggleLanguage}
                    onNavigate={handleNavigate}
                    activeSection={activeSection}
                />

                <main>
                    <HomeSection />
                    <AboutSection />

                    <LowerNarrative>
                        <section id="products" data-section="products" className="product-chapter">
                            <ProductsSection />
                            <ProductsDemoSection />
                        </section>

                        <TeamSection />
                        <ContactSection />
                    </LowerNarrative>
                </main>

                <Footer />
            </div>
        </MotionConfig>
    );
}
