/**
 * AI-Powered Smart Travel Planner
 * Modern 3D Effects and Animations
 * Created: 2025-04-21
 */

// Performance optimization settings
const PERFORMANCE = {
  // Set to true to reduce animations for better performance
  REDUCE_ANIMATIONS: false, // Changed to false by default, will be managed by performance monitor
  // Maximum number of particles to render
  MAX_PARTICLES: 15,
  // Whether to use hardware acceleration for animations
  USE_HARDWARE_ACCELERATION: true,
  // Disable heavy effects on mobile
  DISABLE_HEAVY_EFFECTS_ON_MOBILE: true
};

// Check if device is mobile
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

// Check if performance mode is enabled by the performance monitor
function isPerformanceModeEnabled() {
  return window.performanceMonitor && window.performanceMonitor.isPerformanceModeEnabled();
}

document.addEventListener('DOMContentLoaded', function() {
  console.log("Modern 3D effects initialized with performance optimizations");
  
  // Apply hardware acceleration
  function applyHardwareAcceleration() {
    if (!PERFORMANCE.USE_HARDWARE_ACCELERATION) return;
    
    const elements = document.querySelectorAll('.hero-image, .feature-card, .timeline-item, .map-container, .hotel-card, .attraction-card');
    elements.forEach(el => {
      // Force hardware acceleration
      el.style.transform = 'translateZ(0)';
      el.style.backfaceVisibility = 'hidden';
    });
  }
  applyHardwareAcceleration();
  
  // Handle preloader
  function handlePreloader() {
    const preloader = document.getElementById('preloader');
    if (preloader) {
      // Hide preloader after page is fully loaded
      window.addEventListener('load', function() {
        setTimeout(function() {
          preloader.classList.add('preloader-hidden');
          
          // Remove preloader from DOM after animation completes
          setTimeout(function() {
            preloader.remove();
          }, 500);
        }, 500); // Reduced from 1000ms to 500ms for faster loading
      });
    }
  }
  handlePreloader();
  
  // Handle scroll to top button
  function handleScrollToTop() {
    const scrollToTopBtn = document.getElementById('scrollToTop');
    
    if (scrollToTopBtn) {
      // Show/hide button based on scroll position
      window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
          scrollToTopBtn.classList.add('active');
        } else {
          scrollToTopBtn.classList.remove('active');
        }
      });
      
      // Scroll to top when button is clicked
      scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });
      
      // Add hover effect
      scrollToTopBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px) rotate(360deg)';
        this.style.transition = 'all 0.5s ease';
      });
      
      scrollToTopBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) rotate(0deg)';
      });
    }
  }
  handleScrollToTop();
  
  // Initialize libraries with performance considerations
  function initializeAOS() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: PERFORMANCE.REDUCE_ANIMATIONS ? 400 : 800,
        easing: 'ease-out',
        once: true, // Changed to true to trigger animations only once
        mirror: false, // Changed to false to reduce repaints
        offset: 50,
        disable: PERFORMANCE.DISABLE_HEAVY_EFFECTS_ON_MOBILE && isMobile
      });
    }
  }
  initializeAOS();
  
  // Delay non-critical initializations
  setTimeout(() => {
    // Only initialize if performance mode is not enabled
    if (!isPerformanceModeEnabled()) {
      // Initialize VanillaTilt for 3D hover effects
      function initializeVanillaTilt() {
        // Skip on mobile if heavy effects are disabled
        if (PERFORMANCE.DISABLE_HEAVY_EFFECTS_ON_MOBILE && isMobile) {
          console.log("VanillaTilt disabled on mobile for performance");
          return;
        }

        if (typeof VanillaTilt !== 'undefined') {
          // Apply tilt effect to hero image
          const heroImage = document.querySelector('.hero-image');
          if (heroImage) {
            VanillaTilt.init(heroImage, {
              max: PERFORMANCE.REDUCE_ANIMATIONS ? 5 : 15,
              speed: 400,
              glare: PERFORMANCE.REDUCE_ANIMATIONS ? false : true,
              "max-glare": 0.3,
              scale: 1.05
            });
          }
          
          // Apply tilt to feature cards - limit to first 3 for performance
          const featureCards = document.querySelectorAll('.feature-card');
          if (featureCards.length > 0) {
            const limitedCards = PERFORMANCE.REDUCE_ANIMATIONS ? 
              Array.from(featureCards).slice(0, 3) : featureCards;
            
            VanillaTilt.init(limitedCards, {
              max: 5,
              speed: 400,
              glare: false,
              scale: 1.03
            });
          }
          
          // Apply tilt to hotel and attraction cards - limit for performance
          const cards = document.querySelectorAll('.hotel-card, .attraction-card');
          if (cards.length > 0) {
            const limitedCards = PERFORMANCE.REDUCE_ANIMATIONS ? 
              Array.from(cards).slice(0, 4) : cards;
            
            VanillaTilt.init(limitedCards, {
              max: 5,
              speed: 400,
              glare: false,
              scale: 1.02
            });
          }
        }
      }
      initializeVanillaTilt();
      
      // Initialize scroll effects with performance optimizations
      function initializeScrollEffects() {
        // Skip on mobile if heavy effects are disabled
        if (PERFORMANCE.DISABLE_HEAVY_EFFECTS_ON_MOBILE && isMobile) {
          console.log("Scroll effects disabled on mobile for performance");
          return;
        }

        // Parallax effect for hero section - using requestAnimationFrame for performance
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
          let ticking = false;
          let lastScrollY = window.scrollY;
          
          window.addEventListener('scroll', function() {
            lastScrollY = window.scrollY;
            
            if (!ticking) {
              window.requestAnimationFrame(function() {
                if (lastScrollY < 500) { // Only apply effect near the top of the page
                  const heroElements = heroSection.querySelectorAll('.hero-content, .hero-image-container');
                  
                  heroElements.forEach(element => {
                    const speed = element.classList.contains('hero-image-container') ? 0.05 : 0.03;
                    element.style.transform = `translateY(${lastScrollY * speed}px)`;
                  });
                }
                ticking = false;
              });
              
              ticking = true;
            }
          });
        }
        
        // Animate timeline items on scroll - using Intersection Observer for performance
        const timelineItems = document.querySelectorAll('.timeline-item');
        if (timelineItems.length > 0) {
          const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                // Unobserve after animation to save resources
                observer.unobserve(entry.target);
              }
            });
          }, { threshold: 0.2 });
          
          timelineItems.forEach(item => {
            observer.observe(item);
          });
        }
      }
      initializeScrollEffects();
      
      // Further delay the heaviest effects
      setTimeout(() => {
        if (!isPerformanceModeEnabled()) {
          if (!PERFORMANCE.REDUCE_ANIMATIONS) {
            // Initialize particles effect with reduced count for better performance
            function initializeParticles() {
              // Skip on mobile if heavy effects are disabled
              if (PERFORMANCE.DISABLE_HEAVY_EFFECTS_ON_MOBILE && isMobile) {
                console.log("Particle effects disabled on mobile for performance");
                return;
              }

              const heroSection = document.querySelector('.hero-section');
              const resultsHeader = document.querySelector('.results-header');
              
              if (heroSection || resultsHeader) {
                const targetElement = heroSection || resultsHeader;
                
                // Create particles container
                const particlesContainer = document.createElement('div');
                particlesContainer.className = 'particles-container';
                particlesContainer.style.position = 'absolute';
                particlesContainer.style.top = '0';
                particlesContainer.style.left = '0';
                particlesContainer.style.width = '100%';
                particlesContainer.style.height = '100%';
                particlesContainer.style.overflow = 'hidden';
                particlesContainer.style.zIndex = '0';
                
                // Insert particles container at the beginning of the target element
                targetElement.insertBefore(particlesContainer, targetElement.firstChild);
                
                // Create particles - reduced count for performance
                const particleCount = PERFORMANCE.REDUCE_ANIMATIONS ? 
                  Math.min(15, PERFORMANCE.MAX_PARTICLES) : 
                  Math.min(30, PERFORMANCE.MAX_PARTICLES);
                
                for (let i = 0; i < particleCount; i++) {
                  // Create individual particle
                  function createParticle(container) {
                    const particle = document.createElement('div');
                    
                    // Random size between 3px and 8px
                    const size = Math.random() * 5 + 3;
                    
                    // Random position
                    const posX = Math.random() * 100;
                    const posY = Math.random() * 100;
                    
                    // Random opacity between 0.1 and 0.3
                    const opacity = Math.random() * 0.2 + 0.1;
                    
                    // Random animation duration between 15s and 30s
                    const duration = Math.random() * 15 + 15;
                    
                    // Random animation delay
                    const delay = Math.random() * 5;
                    
                    // Set particle styles
                    particle.style.position = 'absolute';
                    particle.style.width = `${size}px`;
                    particle.style.height = `${size}px`;
                    particle.style.borderRadius = '50%';
                    particle.style.backgroundColor = 'rgba(255, 255, 255, ' + opacity + ')';
                    particle.style.left = `${posX}%`;
                    particle.style.top = `${posY}%`;
                    particle.style.animation = `floatParticle ${duration}s ease-in-out ${delay}s infinite`;
                    
                    // Add particle to container
                    container.appendChild(particle);
                    
                    // Add keyframes for particle animation if not already added
                    if (!document.querySelector('#particle-keyframes')) {
                      const style = document.createElement('style');
                      style.id = 'particle-keyframes';
                      style.textContent = `
                        @keyframes floatParticle {
                          0% { transform: translate(0, 0); }
                          25% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px); }
                          50% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px); }
                          75% { transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px); }
                          100% { transform: translate(0, 0); }
                        }
                      `;
                      document.head.appendChild(style);
                    }
                  }
                  createParticle(particlesContainer);
                }
              }
            }
            initializeParticles();
          } else {
            // Use simpler particles for reduced animations
            const particleCount = Math.min(10, PERFORMANCE.MAX_PARTICLES);
            const heroSection = document.querySelector('.hero-section');
            if (heroSection) {
              for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.style.position = 'absolute';
                particle.style.width = '5px';
                particle.style.height = '5px';
                particle.style.borderRadius = '50%';
                particle.style.backgroundColor = '#4361ee';
                particle.style.opacity = '0.2';
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                heroSection.appendChild(particle);
              }
            }
          }
        }
      }, 1000);
    }
  }, 500);
  
  // Handle navbar scroll effect - using requestAnimationFrame for performance
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    let ticking = false;
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', function() {
      lastScrollY = window.scrollY;
      
      if (!ticking) {
        window.requestAnimationFrame(function() {
          if (lastScrollY > 50) {
            navbar.classList.add('scrolled');
          } else {
            navbar.classList.remove('scrolled');
          }
          ticking = false;
        });
        
        ticking = true;
      }
    });
  }
});
