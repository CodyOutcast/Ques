import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import AboutSection from './components/AboutSection';
import ProductsSection from './components/ProductsSection';
import TeamSection from './components/TeamSection';
import ContactSection from './components/ContactSection';
import './i18n';
import './viewportFix.css';
import setAppHeight from './utils/viewportHeight';
import i18n from 'i18next';

// Immediately executing function to set Meta tags for iOS notch screens
(function() {
    // Remove existing viewport meta tags
    const existingViewports = document.querySelectorAll('meta[name="viewport"]');
    existingViewports.forEach(meta => meta.remove());
    
    // Add new viewport meta tag
    const meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
    document.head.appendChild(meta);
    
    // Force set body styles to eliminate potential white space
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
        background-color: #1d4ed8 !important;
    `;
    
    // Set CSS variables to match top gradient color
    document.documentElement.style.setProperty('--top-background-color', '#1d4ed8');
    document.documentElement.style.setProperty('--safe-area-inset-top', 'env(safe-area-inset-top)');
})();

export default function App() {
    // Language state
    const [isChinese, setIsChinese] = useState(i18n.language === 'cn');
    
    // Active section state (0: About, 1: Products, 2: Team, 3: Contact)
    const [activeSection, setActiveSection] = useState(0);
    
    // Section names for tracking
    const sections = ['about', 'products', 'team', 'contact'];

    // Wheel scroll management
    const wheelDeltaRef = useRef(0);
    const wheelResetTimeoutRef = useRef(null);
    const throttleTimeoutRef = useRef(null);
    const scrollThreshold = 180;
    const wheelResetDelay = 220;
    const throttleDuration = 900;

    const [isThrottled, setIsThrottled] = useState(false);
    
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
    const [touchStart, setTouchStart] = useState(0);
    const [touchEnd, setTouchEnd] = useState(0);

    const handleTouchStart = (e) => {
        setTouchStart(e.targetTouches[0].clientY);
    };

    const handleTouchMove = (e) => {
        setTouchEnd(e.targetTouches[0].clientY);
    };

    const handleTouchEnd = () => {
        if (touchStart - touchEnd > 75) {
            // Swipe up - next section
            setActiveSection(prev => Math.min(prev + 1, sections.length - 1));
        }

        if (touchStart - touchEnd < -75) {
            // Swipe down - previous section
            setActiveSection(prev => Math.max(prev - 1, 0));
        }
    };

    // Wheel handling for desktop navigation with momentum control
    const handleWheel = (e) => {
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
    };

    return (
        <div
            className="dynamic-height w-full overflow-hidden fixed bg-gradient-to-b from-blue-700 to-gray-400"
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
            onWheel={handleWheel}
        >
            <Header 
                isChinese={isChinese}
                toggleLanguage={toggleLanguage}
                onNavigate={handleNavigate}
                activeSection={sections[activeSection]}
            />
            
            {/* About Section */}
            <AboutSection isVisible={activeSection === 0} />
            
            {/* Products Section */}
            <ProductsSection isVisible={activeSection === 1} />
            
            {/* Team Section */}
            <TeamSection isVisible={activeSection === 2} />
            
            {/* Contact Section */}
            <ContactSection isVisible={activeSection === 3} />
            
            {/* Footer */}
            <Footer />
        </div>
    );
}
