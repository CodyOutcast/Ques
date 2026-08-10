import { AnimatePresence, motion } from 'framer-motion';
import { FiMenu, FiX } from 'react-icons/fi';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

const Header = ({ isChinese, toggleLanguage, onNavigate, activeSection }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [isHeaderVisible, setIsHeaderVisible] = useState(true);
    const headerRef = useRef(null);
    const menuButtonRef = useRef(null);
    const mobileNavRef = useRef(null);
    const lastScrollYRef = useRef(0);
    const scrollFrameRef = useRef(null);
    const { t } = useTranslation();

    const navigationItems = [
        { name: t('header.about'), id: 'about' },
        { name: t('header.products'), id: 'products' },
        { name: t('header.team'), id: 'team' },
        { name: t('header.contact'), id: 'contact' },
    ];

    const handleNavClick = (sectionId) => {
        onNavigate(sectionId);
        setIsOpen(false);
    };

    const handleLanguageClick = () => {
        toggleLanguage();
        setIsOpen(false);
    };

    useEffect(() => {
        if (!isOpen) return undefined;

        const previousOverflow = document.body.style.overflow;
        const focusFrame = window.requestAnimationFrame(() => {
            mobileNavRef.current?.querySelector('button')?.focus();
        });
        const handlePointerDown = (event) => {
            if (!headerRef.current?.contains(event.target)) setIsOpen(false);
        };
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                event.preventDefault();
                setIsOpen(false);
                menuButtonRef.current?.focus();
                return;
            }

            if (event.key !== 'Tab') return;
            const focusable = Array.from(
                headerRef.current?.querySelectorAll('button:not([disabled]), a[href]') ?? [],
            ).filter((element) => element.offsetParent !== null);
            const first = focusable[0];
            const last = focusable.at(-1);

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last?.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first?.focus();
            }
        };

        document.body.style.overflow = 'hidden';
        document.addEventListener('pointerdown', handlePointerDown);
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            window.cancelAnimationFrame(focusFrame);
            document.body.style.overflow = previousOverflow;
            document.removeEventListener('pointerdown', handlePointerDown);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isOpen]);

    useEffect(() => {
        const desktopQuery = window.matchMedia('(min-width: 1081px)');
        const handleBreakpointChange = (event) => {
            if (event.matches) setIsOpen(false);
        };

        desktopQuery.addEventListener('change', handleBreakpointChange);
        return () => desktopQuery.removeEventListener('change', handleBreakpointChange);
    }, []);

    useEffect(() => {
        lastScrollYRef.current = Math.max(window.scrollY, 0);

        if (isOpen) setIsHeaderVisible(true);

        const handleScroll = () => {
            if (scrollFrameRef.current !== null) return;

            scrollFrameRef.current = window.requestAnimationFrame(() => {
                const currentScrollY = Math.max(window.scrollY, 0);
                const scrollDelta = currentScrollY - lastScrollYRef.current;

                if (isOpen || currentScrollY < 80) {
                    setIsHeaderVisible(true);
                } else if (Math.abs(scrollDelta) > 6) {
                    setIsHeaderVisible(scrollDelta < 0);
                }

                lastScrollYRef.current = currentScrollY;
                scrollFrameRef.current = null;
            });
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', handleScroll);
            if (scrollFrameRef.current !== null) {
                window.cancelAnimationFrame(scrollFrameRef.current);
                scrollFrameRef.current = null;
            }
        };
    }, [isOpen]);

    return (
        <header
            ref={headerRef}
            className={`site-header${isHeaderVisible || isOpen ? '' : ' is-hidden'}`}
        >
            <motion.div
                className="site-header__inner"
                initial={false}
                animate={{ opacity: 1, y: 0 }}
            >
                <button
                    type="button"
                    className="brand-lockup"
                    onClick={() => handleNavClick('home')}
                    aria-current={activeSection === 'home' ? 'location' : undefined}
                >
                    <span className="brand-lockup__mark">
                        <img src="/brand/mark.ico" alt="" width="256" height="256" />
                    </span>
                    <span className="brand-lockup__name">{t('header.logo_text')}</span>
                </button>

                <nav className="desktop-nav" aria-label={t('header.primary_navigation')}>
                    {navigationItems.map((item) => (
                        <button
                            type="button"
                            key={item.id}
                            onClick={() => handleNavClick(item.id)}
                            className={activeSection === item.id ? 'is-active' : ''}
                            aria-current={activeSection === item.id ? 'location' : undefined}
                        >
                            <span>{item.name}</span>
                        </button>
                    ))}
                </nav>

                <div className="site-header__actions">
                    <button
                        type="button"
                        className="language-control"
                        aria-label={t('header.language')}
                        onClick={handleLanguageClick}
                    >
                        <span className={!isChinese ? 'is-active' : ''}>EN</span>
                        <span className={isChinese ? 'is-active' : ''}>CN</span>
                    </button>

                    <button
                        ref={menuButtonRef}
                        type="button"
                        className="mobile-menu-button"
                        onClick={() => setIsOpen((current) => !current)}
                        aria-label={t(isOpen ? 'header.close_menu' : 'header.open_menu')}
                        aria-expanded={isOpen}
                        aria-controls="mobile-navigation"
                    >
                        {isOpen ? <FiX /> : <FiMenu />}
                    </button>
                </div>

            </motion.div>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        ref={mobileNavRef}
                        id="mobile-navigation"
                        className="mobile-nav"
                        role="navigation"
                        aria-label={t('header.mobile_navigation')}
                        initial={{ opacity: 0, y: -12, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -12, scale: 0.98 }}
                        transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
                    >
                        {navigationItems.map((item) => (
                            <button
                                type="button"
                                key={item.id}
                                onClick={() => handleNavClick(item.id)}
                                className={activeSection === item.id ? 'is-active' : ''}
                                aria-current={activeSection === item.id ? 'location' : undefined}
                            >
                                {item.name}
                            </button>
                        ))}
                        <div className="mobile-nav__language">
                            <span>{t('header.language')}</span>
                            <button type="button" onClick={handleLanguageClick} aria-label={t('header.language')}>
                                <span className={!isChinese ? 'is-active' : ''}>EN</span>
                                <span className={isChinese ? 'is-active' : ''}>CN</span>
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
};

export default Header;
