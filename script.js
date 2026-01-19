document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('uploadModal');
    const uploadBtn = document.getElementById('uploadBtn');
    const closeBtn = document.querySelector('.modal-close');
    const projectForm = document.getElementById('projectForm');
    const projectsGrid = document.querySelector('.project-grid');

    // Modal Triggers
    // Login specific elements
    const loginModal = document.getElementById('loginModal');
    const loginForm = document.getElementById('loginForm');
    const closeLoginBtn = document.querySelector('.modal-close-login');

    // Credentials (Client-side check)
    const USER = "samrit.potfolio";
    const PASS = "9140100459@Samrit";

    // Modal Triggers
    uploadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const isLoggedIn = sessionStorage.getItem('isLoggedIn');

        if (isLoggedIn === 'true') {
            modal.style.display = 'flex';
        } else {
            loginModal.style.display = 'flex';
        }
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    closeLoginBtn.addEventListener('click', () => {
        loginModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
        if (e.target === loginModal) {
            loginModal.style.display = 'none';
        }
    });

    // Login Handle
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const u = document.getElementById('username').value;
        const p = document.getElementById('password').value;

        if (u === USER && p === PASS) {
            sessionStorage.setItem('isLoggedIn', 'true');
            loginModal.style.display = 'none';
            modal.style.display = 'flex'; // Open upload modal
            loginForm.reset();
        } else {
            alert("Invalid Credentials");
        }
    });



    // Form Handle
    projectForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Get Values
        const title = document.getElementById('pTitle').value;
        const desc = document.getElementById('pDesc').value;
        const tags = document.getElementById('pTags').value.split(',').map(t => t.trim());
        const link = document.getElementById('pLink').value;

        // Create Card HTML
        const card = document.createElement('div');
        card.className = 'project-card';
        card.innerHTML = `
            <h3>${title}</h3>
            <p>${desc}</p>
            <div class="tags">
                ${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <a href="${link}" class="btn" target="_blank">View Project <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
        `;

        // Add to Grid (Prepend or Append)
        const firstCard = projectsGrid.firstElementChild;
        projectsGrid.insertBefore(card, firstCard.nextSibling); // Insert after the first one (TenshiGuard)

        // Reset & Close
        projectForm.reset();
        modal.style.display = 'none';

        // Optional: Scroll to it
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
});
