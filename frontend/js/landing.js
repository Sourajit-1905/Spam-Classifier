document.addEventListener('DOMContentLoaded', () => {
    const arrowBtn = document.querySelector('.arrow-btn');

    // The arrow is an <a> tag, so it navigates by default.
    // This listener is kept for extensibility (e.g. animations before redirect).
    arrowBtn.addEventListener('click', (e) => {
        // Currently uses default href navigation to index.html
        // No extra logic needed unless you want a transition effect
    });
});