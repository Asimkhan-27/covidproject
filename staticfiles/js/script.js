// This script contains the mobile navigation toggle logic and plot preview logic.
document.addEventListener('DOMContentLoaded', function () {

    // --- Mobile Navigation Toggle Logic ---
    const navToggle = document.getElementById('navToggle');
    const mobileNavMenu = document.getElementById('mobileNavMenu');

    if (navToggle && mobileNavMenu) {
        navToggle.addEventListener('click', function () {
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
            mobileNavMenu.classList.toggle('hidden', isExpanded);
            mobileNavMenu.classList.toggle('flex', !isExpanded);
        });

        const mobileLinks = mobileNavMenu.querySelectorAll('a');
        if (mobileLinks.length > 0) {
            mobileLinks.forEach(link => {
                link.addEventListener('click', () => {
                    mobileNavMenu.classList.add('hidden');
                    mobileNavMenu.classList.remove('flex');
                    navToggle.setAttribute('aria-expanded', 'false');
                });
            });
        }
    }

    // --- Plot Preview Modal Logic ---
    const modal = document.getElementById('plotPreviewModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const modalContent = document.getElementById('modalContent');
    const body = document.body;

    if (modal && modalContent) {
        function openModal(content) {
            while (modalContent.firstChild) {
                modalContent.removeChild(modalContent.firstChild);
            }

            if (typeof content === 'string') {
                modalContent.innerHTML = content;
            } else if (Array.isArray(content)) {
                content.forEach(el => modalContent.appendChild(el));
            }

            modal.classList.remove('hidden');
            void modal.offsetWidth;
            modal.classList.remove('opacity-0');
            modal.classList.add('opacity-100');
            body.style.overflow = 'hidden';
        }

        function closeModal() {
            modal.classList.remove('opacity-100');
            modal.classList.add('opacity-0');
            modal.addEventListener('transitionend', function handler() {
                modal.classList.add('hidden');
                modalContent.innerHTML = '';
                body.style.overflow = '';
                modal.removeEventListener('transitionend', handler);
            }, { once: true });
        }

        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', closeModal);
        }

        modal.addEventListener('click', function (event) {
            if (event.target === modal) {
                closeModal();
            }
        });

        // --- Static Image Previews ---
        const staticTriggers = document.querySelectorAll('.js-preview-trigger');
        staticTriggers.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function (event) {
                if (event.target.tagName === 'A' || event.target.tagName === 'BUTTON') return;
                const imgElement = this.querySelector('img');
                if (imgElement && imgElement.src) {
                    const modalImgHtml = `<img src="${imgElement.src}" alt="Plot Preview" class="max-w-full max-h-full object-contain mx-auto my-auto rounded-lg shadow-lg">`;
                    openModal(modalImgHtml);
                }
            });
        });

        // --- Bokeh Plot Previews ---
        const bokehTriggers = document.querySelectorAll('.js-preview-trigger-bokeh');
        bokehTriggers.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function (event) {
                if (event.target.tagName === 'A' || event.target.tagName === 'BUTTON') return;

                const originalBokehDiv = this.querySelector('.bk-root');
                const originalBokehScript = this.querySelector('script[type="text/javascript"]');

                if (originalBokehDiv && originalBokehScript) {
                    const modalBokehDivId = 'bokeh-modal-plot-' + Date.now();
                    const newBokehDiv = document.createElement('div');
                    newBokehDiv.id = modalBokehDivId;
                    newBokehDiv.className = 'w-full h-full min-h-[400px] flex flex-col items-center justify-center';

                    const newBokehScript = document.createElement('script');
                    newBokehScript.type = 'text/javascript';

                    let scriptContent = originalBokehScript.textContent;
                    const originalIdPattern = originalBokehDiv.id;
                    const escapedOriginalId = originalIdPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                    const embedRegex = new RegExp(`(Bokeh\\.embed\\.embed_item\\([^,]+,\\s*)(['"])${escapedOriginalId}(['"])`, 'g');
                    scriptContent = scriptContent.replace(embedRegex, `$1$2${modalBokehDivId}$3`);
                    newBokehScript.textContent = scriptContent;

                    openModal([newBokehDiv, newBokehScript]);
                    window.dispatchEvent(new Event('resize'));
                } else {
                    openModal('<div class="text-xl text-gray-700 text-center p-8">Interactive Bokeh plot not found.</div>');
                }
            });
        });

        // --- Iframe Previews (Maps, Tables) ---
        const iframeTriggers = document.querySelectorAll('.js-preview-trigger-iframe');
        iframeTriggers.forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function (event) {
                if (event.target.tagName === 'A' || event.target.tagName === 'IFRAME' || event.target.tagName === 'BUTTON') return;
                const iframeElement = this.querySelector('iframe');
                if (iframeElement && iframeElement.src) {
                    const modalIframeHtml = `<iframe src="${iframeElement.src}" class="w-full h-full rounded-lg shadow-lg" frameborder="0" title="Map Preview" loading="lazy"></iframe>`;
                    openModal(modalIframeHtml);
                }
            });
        });
    }
});
