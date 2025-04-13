AOS.init({


  // Settings that can be overridden on per-element basis, by `data-aos-*` attributes:
  offset: 120, // offset (in px) from the original trigger point
  delay: 0, // values from 0 to 3000, with step 50ms
  duration: 900, // values from 0 to 3000, with step 50ms
  easing: 'ease', // default easing for AOS animations
  once: false, // whether animation should happen only once - while scrolling down
  mirror: false, // whether elements should animate out while scrolling past them
  anchorPlacement: 'top-bottom', // defines which position of the element regarding to window should trigger the animation

});


// Select the spinner wrapper element
const spinnerWrapperEl = document.querySelector('.spinner-wrapper');

// Wait for the page to load
window.addEventListener('load', () => {
    // Keep the spinner visible for a longer duration before fading out
    setTimeout(() => {
        // Fade out the spinner
        spinnerWrapperEl.style.opacity = '0';

        // Hide the spinner after fade out
        setTimeout(() => {
            spinnerWrapperEl.style.display = 'none';
        }, 500); // 500ms fade-out duration
    }, 1000); // Increased delay to 2000ms (2 seconds) before fading out
});
