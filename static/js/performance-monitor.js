/**
 * Performance Monitor
 * Automatically detects performance issues and reduces animations to improve user experience
 */

(function() {
  // Configuration
  const config = {
    // FPS threshold below which we consider performance to be poor
    lowFpsThreshold: 30,
    
    // Number of consecutive frames with low FPS to trigger performance mode
    consecutiveLowFpsFrames: 5,
    
    // Check interval in milliseconds
    checkInterval: 2000,
    
    // Debug mode
    debug: false
  };
  
  // State
  let isPerformanceModeEnabled = false;
  let lowFpsCounter = 0;
  let lastTime = performance.now();
  let frames = 0;
  let currentFps = 60;
  
  // Elements that will have animations reduced
  const animatedElementSelectors = [
    '.hero-image', 
    '.feature-card', 
    '.timeline-item', 
    '.hotel-card', 
    '.attraction-card',
    '.map-container',
    '.day-plan',
    '.spinner-3d',
    '.particles-container',
    '.particles-3d-container'
  ];
  
  // Check if device is mobile or has low memory
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const hasLowMemory = navigator.deviceMemory && navigator.deviceMemory < 4;
  
  // Enable performance mode immediately for mobile devices with low memory
  if (isMobile && hasLowMemory) {
    enablePerformanceMode();
    if (config.debug) console.log('Performance mode enabled automatically for low-memory mobile device');
  }
  
  // Calculate FPS
  function calculateFps() {
    const now = performance.now();
    const elapsed = now - lastTime;
    
    if (elapsed >= config.checkInterval) {
      currentFps = Math.round((frames * 1000) / elapsed);
      
      if (config.debug) {
        console.log(`Current FPS: ${currentFps}`);
      }
      
      // Check if FPS is below threshold
      if (currentFps < config.lowFpsThreshold) {
        lowFpsCounter++;
        
        if (lowFpsCounter >= config.consecutiveLowFpsFrames && !isPerformanceModeEnabled) {
          enablePerformanceMode();
        }
      } else {
        lowFpsCounter = 0;
      }
      
      frames = 0;
      lastTime = now;
    }
    
    frames++;
    requestAnimationFrame(calculateFps);
  }
  
  // Enable performance mode
  function enablePerformanceMode() {
    if (isPerformanceModeEnabled) return;
    
    isPerformanceModeEnabled = true;
    
    // Add reduce-animation class to body
    document.body.classList.add('reduce-animation');
    
    // Add hardware acceleration to key elements
    animatedElementSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        el.classList.add('hardware-accelerated');
      });
    });
    
    // Disable heavy animations
    const heavyAnimations = document.querySelectorAll('.particles-container, .particles-3d-container');
    heavyAnimations.forEach(el => {
      el.style.display = 'none';
    });
    
    // Simplify shadows
    const elementsWithShadows = document.querySelectorAll('.card, .card-3d, .feature-card, .timeline-content, .hotel-card, .attraction-card');
    elementsWithShadows.forEach(el => {
      el.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
    });
    
    // Show notification to user
    showPerformanceNotification();
    
    if (config.debug) {
      console.log('Performance mode enabled due to low FPS');
    }
  }
  
  // Show notification to user
  function showPerformanceNotification() {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'performance-notification';
    notification.innerHTML = `
      <div class="performance-notification-content">
        <p>Performance optimizations applied for smoother experience</p>
        <button class="close-notification">OK</button>
      </div>
    `;
    
    // Style notification
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    notification.style.color = 'white';
    notification.style.padding = '10px 15px';
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '300px';
    notification.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
    notification.style.transition = 'opacity 0.3s ease';
    
    // Add close button event
    notification.querySelector('.close-notification').addEventListener('click', function() {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    });
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 5000);
  }
  
  // Handle performance toggle button
  function initPerformanceToggle() {
    const toggleBtn = document.getElementById('performanceToggle');
    if (!toggleBtn) return;
    
    // Set initial state based on performance mode
    if (isPerformanceModeEnabled) {
      toggleBtn.classList.add('active');
      toggleBtn.title = 'Disable performance mode';
    }
    
    // Add click event
    toggleBtn.addEventListener('click', function() {
      if (isPerformanceModeEnabled) {
        disablePerformanceMode();
        toggleBtn.classList.remove('active');
        toggleBtn.title = 'Enable performance mode';
        
        // Show notification
        showNotification('Performance mode disabled. Full animations enabled.');
      } else {
        enablePerformanceMode();
        toggleBtn.classList.add('active');
        toggleBtn.title = 'Disable performance mode';
        
        // Show notification
        showNotification('Performance mode enabled for smoother experience.');
      }
    });
  }
  
  // Disable performance mode
  function disablePerformanceMode() {
    if (!isPerformanceModeEnabled) return;
    
    isPerformanceModeEnabled = false;
    
    // Remove reduce-animation class from body
    document.body.classList.remove('reduce-animation');
    
    // Remove hardware acceleration from elements
    animatedElementSelectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        el.classList.remove('hardware-accelerated');
      });
    });
    
    // Re-enable heavy animations
    const heavyAnimations = document.querySelectorAll('.particles-container, .particles-3d-container');
    heavyAnimations.forEach(el => {
      el.style.display = '';
    });
    
    // Restore shadows
    const elementsWithShadows = document.querySelectorAll('.card, .card-3d, .feature-card, .timeline-content, .hotel-card, .attraction-card');
    elementsWithShadows.forEach(el => {
      el.style.boxShadow = '';
    });
    
    if (config.debug) {
      console.log('Performance mode disabled manually');
    }
    
    // Reload modern effects
    if (typeof initializeAOS === 'function') {
      initializeAOS();
    }
  }
  
  // Show notification
  function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'performance-notification';
    notification.innerHTML = `
      <div class="performance-notification-content">
        <p>${message}</p>
        <button class="close-notification">OK</button>
      </div>
    `;
    
    // Add close button event
    notification.querySelector('.close-notification').addEventListener('click', function() {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    });
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 5000);
  }
  
  // Listen for browser warnings about unresponsive page
  window.addEventListener('beforeunload', function(e) {
    // If the browser is showing "page unresponsive" dialog, enable performance mode
    if (performance.now() - lastTime > 5000) {
      enablePerformanceMode();
    }
  });
  
  // Start monitoring
  document.addEventListener('DOMContentLoaded', function() {
    // Initialize performance toggle
    initPerformanceToggle();
    
    // Wait a bit for the page to stabilize
    setTimeout(() => {
      calculateFps();
    }, 1000);
  });
  
  // Expose API
  window.performanceMonitor = {
    enablePerformanceMode: enablePerformanceMode,
    disablePerformanceMode: disablePerformanceMode,
    getCurrentFps: () => currentFps,
    isPerformanceModeEnabled: () => isPerformanceModeEnabled,
    showNotification: showNotification
  };
})();
