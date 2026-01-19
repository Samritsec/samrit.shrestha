document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('uploadModal');
    const uploadBtn = document.getElementById('uploadBtn');
    const closeBtn = document.querySelector('.modal-close');
    const projectForm = document.getElementById('projectForm');
    const projectsGrid = document.querySelector('.project-grid');

    // Modal Triggers
    uploadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        modal.style.display = 'flex';
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
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
