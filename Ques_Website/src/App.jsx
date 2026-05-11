import { useState, useEffect, useRef, useEffectEvent } from 'react';
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
import setAppHeight from './utils/viewportHeight';
import i18n from 'i18next';

function applyViewportChrome() {
    const existingViewports = document.querySelectorAll('meta[name="viewport"]');
    existingViewports.forEach((meta) => meta.remove());

    const meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
    document.head.appendChild(meta);

    document.documentElement.style.cssText = `
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
        overflow: hidden !important;
    `;
    document.body.style.cssText = `
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
        height: 100vh !important;
        height: 100dvh !important;
        overflow: hidden !important;
        background-color: #020617 !important;
    `;

    document.documentElement.style.setProperty('--top-background-color', '#020617');
    document.documentElement.style.setProperty('--safe-area-inset-top', 'env(safe-area-inset-top)');
}

export default function App() {
    // Language state
    const [isChinese, setIsChinese] = useState(i18n.language === 'cn');
    const appContainerRef = useRef(null);
    
    // Active section state (0: Home, 1: About, 2: Products Demo, 3: Products Details, 4: Team, 5: Contact)
    const [activeSection, setActiveSection] = useState(0);
    const [visitedSections, setVisitedSections] = useState(() => new Set([0]));
    
    // Section names for tracking
    const sections = ['home', 'about', 'products', 'products-detail', 'team', 'contact'];

    // Wheel scroll management
    const wheelDeltaRef = useRef(0);
    const wheelResetTimeoutRef = useRef(null);
    const throttleTimeoutRef = useRef(null);
    const scrollThreshold = 180;
    const wheelResetDelay = 220;
    const throttleDuration = 900;

    const [isThrottled, setIsThrottled] = useState(false);

    useEffect(() => {
        setVisitedSections((prev) => {
            if (prev.has(activeSection)) {
                return prev;
            }

            const next = new Set(prev);
            next.add(activeSection);
            return next;
        });
    }, [activeSection]);

    useEffect(() => {
        applyViewportChrome();
    }, []);
    
    // Set viewport height on component mount
    useEffect(() => {
        // Initial setup
        setAppHeight();
        
        // Recalculate on scroll to handle Safari address bar hide/show
        const handleScroll = () => {
            requestAnimationFrame(setAppHeight);
        };
        
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Cleanup timers on unmount
    useEffect(() => {
        return () => {
            if (wheelResetTimeoutRef.current) {
                clearTimeout(wheelResetTimeoutRef.current);
            }

            if (throttleTimeoutRef.current) {
                clearTimeout(throttleTimeoutRef.current);
            }
        };
    }, []);

    // Language toggle function
    const toggleLanguage = () => {
        const newLang = isChinese ? 'en' : 'cn';
        i18n.changeLanguage(newLang);
        setIsChinese(!isChinese);
    };

    // Navigation handler
    const handleNavigate = (sectionId) => {
        const sectionIndex = sections.indexOf(sectionId);
        if (sectionIndex !== -1) {
            setActiveSection(sectionIndex);
        }
    };

    // Touch handling for swipe navigation
    const touchStartRef = useRef(null);
    const touchEndRef = useRef(null);

    const handleTouchStart = (e) => {
        const startY = e.targetTouches[0].clientY;
        touchStartRef.current = startY;
        touchEndRef.current = startY;
    };

    const handleTouchMove = (e) => {
        touchEndRef.current = e.targetTouches[0].clientY;
    };

    const handleTouchEnd = () => {
        const touchStart = touchStartRef.current;
        const touchEnd = touchEndRef.current;

        if (touchStart === null || touchEnd === null) {
            return;
        }

        const touchDelta = touchStart - touchEnd;

        touchStartRef.current = null;
        touchEndRef.current = null;

        if (touchDelta > 75) {
            // Swipe up - next section
            setActiveSection(prev => Math.min(prev + 1, sections.length - 1));
        }

        if (touchDelta < -75) {
            // Swipe down - previous section
            setActiveSection(prev => Math.max(prev - 1, 0));
        }
    };

    // Wheel handling for desktop navigation with momentum control
    const handleWheel = useEffectEvent((e) => {
        if (typeof e.preventDefault === 'function') {
            e.preventDefault();
        }

        if (isThrottled) {
            return;
        }

        wheelDeltaRef.current += e.deltaY;

        if (wheelResetTimeoutRef.current) {
            clearTimeout(wheelResetTimeoutRef.current);
        }

        wheelResetTimeoutRef.current = setTimeout(() => {
            wheelDeltaRef.current = 0;
        }, wheelResetDelay);

        if (wheelDeltaRef.current >= scrollThreshold) {
            setActiveSection(prev => Math.min(prev + 1, sections.length - 1));
            wheelDeltaRef.current = 0;
            setIsThrottled(true);

            if (throttleTimeoutRef.current) {
                clearTimeout(throttleTimeoutRef.current);
            }

            throttleTimeoutRef.current = setTimeout(() => {
                setIsThrottled(false);
            }, throttleDuration);
        } else if (wheelDeltaRef.current <= -scrollThreshold) {
            setActiveSection(prev => Math.max(prev - 1, 0));
            wheelDeltaRef.current = 0;
            setIsThrottled(true);

            if (throttleTimeoutRef.current) {
                clearTimeout(throttleTimeoutRef.current);
            }

            throttleTimeoutRef.current = setTimeout(() => {
                setIsThrottled(false);
            }, throttleDuration);
        }
    });

    useEffect(() => {
        const appContainer = appContainerRef.current;

        if (!appContainer) {
            return undefined;
        }

        const handleNativeWheel = (event) => {
            handleWheel(event);
        };

        appContainer.addEventListener('wheel', handleNativeWheel, { passive: false });

        return () => {
            appContainer.removeEventListener('wheel', handleNativeWheel);
        };
    }, [handleWheel]);

    return (
        <div
            ref={appContainerRef}
            className="dynamic-height w-full overflow-hidden fixed bg-grid-pattern"
            style={{
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                paddingTop: 0,
                marginTop: 0,
                paddingBottom: 'env(safe-area-inset-bottom)',
                WebkitPaddingBottom: 'env(safe-area-inset-bottom)'
            }}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
        >
            {/* Ambient Background Effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[40rem] h-[40rem] bg-blue-900/20 rounded-full mix-blend-screen filter blur-[80px] animate-blob"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[45rem] h-[45rem] bg-blue-800/15 rounded-full mix-blend-screen filter blur-[80px] animate-blob animation-delay-4000"></div>
            </div>

            <Header 
                isChinese={isChinese}
                toggleLanguage={toggleLanguage}
                onNavigate={handleNavigate}
                activeSection={sections[activeSection]}
            />
            
            {/* Home Section */}
            {visitedSections.has(0) && <HomeSection isVisible={activeSection === 0} />}
            
            {/* About Section */}
            {visitedSections.has(1) && <AboutSection isVisible={activeSection === 1} />}
            
            {/* Products Section - Demo Video */}
            {visitedSections.has(2) && <ProductsDemoSection isVisible={activeSection === 2} />}
            
            {/* Products Section - Details */}
            {visitedSections.has(3) && <ProductsSection isVisible={activeSection === 3} />}
            
            {/* Team Section */}
            {visitedSections.has(4) && <TeamSection isVisible={activeSection === 4} />}
            
            {/* Contact Section */}
            {visitedSections.has(5) && <ContactSection isVisible={activeSection === 5} />}
            
            {/* Footer */}
            <Footer />
        </div>
    );
}
