/**
 * Antigravity UI & Motion Engine
 * Delivers spatial depth, weightless floating elements, 3D interactive card tilt,
 * ambient spatial parallax, and buttery-smooth GSAP staggered entrances.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Accessibility: Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // 2. GSAP Staggered Entrance Animations
    if (typeof gsap !== 'undefined' && !prefersReducedMotion) {
        // Register ScrollTrigger if loaded
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
        }

        // Stagger hero & headers
        gsap.fromTo('.hero-pill, .hero-title, .hero-subtitle, .hero-cta-group, .demo-box, .teacher-header, .assessment-header', 
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.7, stagger: 0.07, ease: 'power3.out', clearProps: 'transform,opacity' }
        );

        // Stagger tier cards & metric summary cards
        const tierCards = document.querySelectorAll('.tier-card, .metric-card, .profile-metric-card');
        if (tierCards.length > 0) {
            gsap.fromTo(tierCards, 
                { opacity: 0, y: 25, scale: 0.98 },
                { opacity: 1, y: 0, scale: 1, stagger: 0.08, duration: 0.6, ease: 'power2.out', clearProps: 'transform,opacity', delay: 0.1 }
            );
        }

        // Stagger student cards / score cards / strategy cards / question cards
        const gridItems = document.querySelectorAll('.student-card, .score-card, .strategy-card, .question-card');
        if (gridItems.length > 0) {
            gsap.fromTo(gridItems, 
                { opacity: 0, y: 25 },
                { opacity: 1, y: 0, stagger: 0.05, duration: 0.6, ease: 'power2.out', clearProps: 'transform,opacity', delay: 0.15 }
            );
        }
    }

    // 3. 3D Spatial Interactive Tilt & Weightless Physics (Desktop)
    if (!prefersReducedMotion && window.innerWidth > 768) {
        const tiltCards = document.querySelectorAll(
            '.tier-card, .student-card, .metric-card, .profile-metric-card, .persona-hero-card, .result-hero-card, .score-card, .strategy-card, .card, .teacher-open-message-card'
        );

        tiltCards.forEach(card => {
            card.style.transformStyle = 'preserve-3d';
            card.style.perspective = '1000px';

            let isHovered = false;
            let currentX = 0, currentY = 0;
            let targetX = 0, targetY = 0;

            card.addEventListener('mouseenter', () => {
                isHovered = true;
            });

            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                targetX = ((y - centerY) / centerY) * -6; // max 6 deg
                targetY = ((x - centerX) / centerX) * 6;  // max 6 deg

                card.style.transform = `perspective(1000px) rotateX(${targetX}deg) rotateY(${targetY}deg) translateY(-8px) translateZ(10px)`;
                card.style.boxShadow = `0 24px 48px -12px rgba(0, 0, 0, 0.75), 0 0 25px rgba(99, 102, 241, 0.28)`;
            });

            card.addEventListener('mouseleave', () => {
                isHovered = false;
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px) translateZ(0px)';
                card.style.boxShadow = '';
            });
        });
    }

    // 4. Floating Ambient Orbs Mouse Parallax
    const orbs = document.querySelectorAll('.ambient-orb');
    if (orbs.length > 0 && !prefersReducedMotion) {
        window.addEventListener('mousemove', e => {
            const mouseX = e.clientX / window.innerWidth - 0.5;
            const mouseY = e.clientY / window.innerHeight - 0.5;

            orbs.forEach((orb, i) => {
                const speed = (i + 1) * 22;
                const offsetX = mouseX * speed;
                const offsetY = mouseY * speed;
                orb.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
            });
        });
    }

    // 5. Score Progress Meters Dynamic Fill
    document.querySelectorAll('.score-progress-fill[data-score], .score-meter-fill[data-score], .mini-bar-fill[data-score]').forEach(el => {
        const score = el.getAttribute('data-score') || '0';
        el.style.width = score + '%';
    });
});

/**
 * Google One-Tap Persona & Account Switcher
 */
window.switchGoogleOneTap = function(name, email, role, tier, avatarChar, roleLabel, context = 'nav') {
    const isNav = (context === 'nav');
    const chipAlex = document.getElementById(isNav ? 'chipAlex' : 'pageChipAlex');
    const chipSarah = document.getElementById(isNav ? 'chipSarah' : 'pageChipSarah');
    const nameEl = document.getElementById(isNav ? 'onetapName' : 'pageOnetapName');
    const emailEl = document.getElementById(isNav ? 'onetapEmail' : 'pageOnetapEmail');
    const roleTagEl = document.getElementById(isNav ? 'onetapRoleTag' : 'pageOnetapRoleTag');
    const avatarEl = document.getElementById(isNav ? 'onetapAvatar' : 'pageOnetapAvatar');
    const btnTextEl = document.getElementById(isNav ? 'onetapBtnText' : 'pageOnetapBtnText');
    const linkEl = document.getElementById(isNav ? 'oneTapContinueLink' : 'pageOneTapContinueLink');

    if (nameEl) nameEl.textContent = name;
    if (emailEl) emailEl.textContent = email;
    if (roleTagEl) roleTagEl.textContent = roleLabel;
    
    if (avatarEl) {
        avatarEl.textContent = avatarChar;
        if (role === 'TEACHER') {
            avatarEl.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            avatarEl.style.boxShadow = '0 2px 8px rgba(16, 185, 129, 0.4)';
        } else {
            avatarEl.style.background = 'linear-gradient(135deg, #4285F4, #1a73e8)';
            avatarEl.style.boxShadow = '0 2px 8px rgba(66, 133, 244, 0.4)';
        }
    }

    const firstName = name.split(' ')[0];
    if (btnTextEl) btnTextEl.textContent = `Continue as ${firstName}`;

    if (linkEl) {
        const encName = encodeURIComponent(name);
        const encEmail = encodeURIComponent(email);
        linkEl.href = `/accounts/google/callback/simulate/?name=${encName}&email=${encEmail}&role=${role}&tier=${tier}`;
    }

    if (chipAlex && chipSarah) {
        if (role === 'STUDENT') {
            chipAlex.classList.add('active');
            chipSarah.classList.remove('active');
        } else {
            chipSarah.classList.add('active');
            chipAlex.classList.remove('active');
        }
    }
};

/**
 * Google One-Tap Instant Click Feedback
 */
window.triggerOneTapLoginAnimation = function(event, element) {
    const btnText = element.querySelector('.onetap-btn-text');
    const btnLoader = element.querySelector('.onetap-btn-loader');
    
    if (btnText && btnLoader) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-flex';
        btnLoader.style.alignItems = 'center';
        btnLoader.style.justifyContent = 'center';
        btnLoader.style.gap = '0.5rem';
        element.style.pointerEvents = 'none';
        element.style.opacity = '0.92';
    }
};
