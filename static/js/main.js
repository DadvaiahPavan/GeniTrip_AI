/**
 * AI-Powered Smart Travel Planner
 * Main JavaScript file for client-side functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Travel Planner application initialized");
    
    // We're now handling the date picker in the index.html file directly
    // This prevents conflicts between multiple initializations

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Custom select styling for travel mode
    const travelModeCards = document.querySelectorAll('.travel-mode-card');
    
    travelModeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Find the radio input within this card
            const radioInput = this.querySelector('input[type="radio"]');
            
            // Check the radio input
            if (radioInput) {
                radioInput.checked = true;
                
                // Remove selected class from all cards
                travelModeCards.forEach(c => {
                    c.classList.remove('selected');
                });
                
                // Add selected class to this card
                this.classList.add('selected');
            }
        });
    });

    // Form validation
    const plannerForm = document.querySelector('form[action="/plan"]');
    
    if (plannerForm) {
        console.log("Travel plan form found, setting up submission handler");
        
        plannerForm.addEventListener('submit', function(e) {
            let isValid = true;
            const formData = new FormData(this);
            
            // Log form data for debugging
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
                if (!value) isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                alert("Please fill out all required fields");
                return false;
            }
            
            // Get selected travel mode
            const selectedTravelMode = document.querySelector('input[name="travel_mode"]:checked').value;
            console.log(`Selected travel mode: ${selectedTravelMode}`);
            
            // If we got here, show loading modal
            if (typeof bootstrap !== 'undefined') {
                const loadingModal = document.getElementById('loadingModal');
                if (loadingModal) {
                    // Update loading icon based on selected travel mode
                    const loadingIcon = document.getElementById('loadingModeIcon');
                    if (loadingIcon) {
                        // Remove existing icon class
                        loadingIcon.classList.remove('fa-plane', 'fa-car');
                        
                        // Add appropriate icon class based on selected mode
                        if (selectedTravelMode === 'car') {
                            loadingIcon.classList.add('fa-car');
                        } else {
                            loadingIcon.classList.add('fa-plane');
                        }
                    }
                    
                    const bsModal = new bootstrap.Modal(loadingModal);
                    bsModal.show();
                    
                    // Update progress bar animation with more realistic and engaging behavior
                    const progressBar = document.getElementById('progressBar');
                    const loadingText = document.querySelector('.loading-subtext');
                    const loadingStatus = document.querySelector('.mt-3.small.text-white-50');
                    
                    if (progressBar) {
                        let progress = 5;
                        const messages = [
                            "Gathering information about your destination...",
                            "Finding the best attractions...",
                            "Searching for top-rated hotels...",
                            "Planning your daily itinerary...",
                            "Finalizing your personalized travel plan..."
                        ];
                        
                        const statusMessages = [
                            "Analyzing travel data...",
                            "Checking weather conditions...",
                            "Optimizing routes...",
                            "Calculating travel times...",
                            "Generating 3D visualizations..."
                        ];
                        
                        let messageIndex = 0;
                        let statusIndex = 0;
                        
                        // Initial message
                        if (loadingText) loadingText.textContent = messages[0];
                        if (loadingStatus) loadingStatus.textContent = statusMessages[0];
                        
                        // More realistic progress simulation with variable speeds
                        const interval = setInterval(() => {
                            // Simulate different processing speeds
                            const increment = Math.random() * 3 + 2; // Random increment between 2-5
                            progress += increment;
                            
                            // Update progress bar with smooth animation
                            progressBar.style.width = Math.min(progress, 95) + '%';
                            
                            // Update messages at certain thresholds
                            if (progress > 20 && messageIndex === 0) {
                                messageIndex++;
                                if (loadingText) loadingText.textContent = messages[messageIndex];
                            } else if (progress > 40 && messageIndex === 1) {
                                messageIndex++;
                                if (loadingText) loadingText.textContent = messages[messageIndex];
                            } else if (progress > 60 && messageIndex === 2) {
                                messageIndex++;
                                if (loadingText) loadingText.textContent = messages[messageIndex];
                            } else if (progress > 80 && messageIndex === 3) {
                                messageIndex++;
                                if (loadingText) loadingText.textContent = messages[messageIndex];
                            }
                            
                            // Rotate status messages more frequently
                            if (progress % 10 < increment && loadingStatus) {
                                statusIndex = (statusIndex + 1) % statusMessages.length;
                                loadingStatus.textContent = statusMessages[statusIndex];
                            }
                            
                            // Stop at 95% - the server response will trigger the form submission
                            if (progress >= 95) clearInterval(interval);
                        }, 800);
                    }
                }
            }
            
            // Debug: Confirming form will submit as POST
            console.log("Submitting form as POST to /plan");
            // Do not preventDefault here; let the form submit normally as POST
            // Only block if invalid
        });
    }

    // Handle flash messages
    const flashes = document.querySelectorAll('.alert');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.classList.add('fade');
            setTimeout(() => {
                flash.remove();
            }, 500);
        }, 5000);
    });

    // Format markdown content on result page
    const markdownContent = document.querySelector('.markdown-content');
    if (markdownContent) {
        console.log("Found markdown content, applying formatting");
        
        // Create table of contents
        const headings = markdownContent.querySelectorAll('h2');
        if (headings.length > 0) {
            const tocContainer = document.createElement('div');
            tocContainer.className = 'card mb-4 p-3';
            tocContainer.innerHTML = '<h5>Table of Contents</h5>';
            
            const tocList = document.createElement('ul');
            tocList.className = 'list-unstyled';
            
            headings.forEach((heading, index) => {
                const id = `toc-heading-${index}`;
                heading.id = id;
                
                const listItem = document.createElement('li');
                const link = document.createElement('a');
                link.href = `#${id}`;
                link.textContent = heading.textContent;
                
                listItem.appendChild(link);
                tocList.appendChild(listItem);
            });
            
            tocContainer.appendChild(tocList);
            markdownContent.prepend(tocContainer);
        }
        
        // Enhance specific sections
        const allStrongs = markdownContent.querySelectorAll('strong');
        
        // Filter for headings containing specific text
        allStrongs.forEach(element => {
            const text = element.textContent;
            if (text.includes('Morning')) {
                element.innerHTML = '🌅 ' + element.innerHTML;
            } else if (text.includes('Afternoon')) {
                element.innerHTML = '☀️ ' + element.innerHTML;
            } else if (text.includes('Evening')) {
                element.innerHTML = '🌙 ' + element.innerHTML;
            }
        });
    }
}); 