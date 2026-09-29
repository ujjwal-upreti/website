document.addEventListener('DOMContentLoaded', () => {
    const nav = document.getElementById('mainNav');

    const updateNav = () => {
        if (!nav) return;
        nav.classList.toggle('scrolled', window.scrollY > 15);
    };

    updateNav();
    window.addEventListener('scroll', updateNav, { passive: true });

    const revealItems = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });
        revealItems.forEach(item => observer.observe(item));
    } else {
        revealItems.forEach(item => item.classList.add('visible'));
    }

    document.querySelectorAll('.wishlist-btn[data-wishlist-url]').forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const url = button.dataset.wishlistUrl;
            if (!url) return;

            const csrf = document.querySelector('meta[name="csrf-token"]')?.content ||
                document.querySelector('input[name="csrf_token"]')?.value;
            const icon = button.querySelector('i');

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrf || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                if (!response.ok) throw new Error('Wishlist request failed');
                const data = await response.json();
                button.classList.toggle('active', data.saved);
                if (icon) {
                    icon.classList.toggle('bi-heart-fill', data.saved);
                    icon.classList.toggle('bi-heart', !data.saved);
                }
            } catch (error) {
                console.error(error);
            }
        });
    });

    // Product gallery: hovering a thumbnail changes the large image.
    const mainImage = document.getElementById('detailMainImage');
    const thumbs = document.querySelectorAll('.detail-thumb');
    thumbs.forEach(thumb => {
        const showImage = () => {
            if (!mainImage) return;
            mainImage.src = thumb.dataset.image;
            thumbs.forEach(item => item.classList.remove('active'));
            thumb.classList.add('active');
        };
        thumb.addEventListener('mouseenter', showImage);
        thumb.addEventListener('focus', showImage);
        thumb.addEventListener('click', showImage);
    });

    // Product size/color selector.
    const variants = window.PRODUCT_VARIANT_DATA || [];
    const sizeButtons = document.querySelectorAll('#sizeOptions .variant-option');
    const colorButtons = document.querySelectorAll('#colorOptions .variant-option');
    const sizeInput = document.getElementById('selectedSizeInput');
    const colorInput = document.getElementById('selectedColorInput');
    const selectedSize = document.getElementById('selectedSize');
    const selectedColor = document.getElementById('selectedColor');
    const variantStock = document.getElementById('variantStock');
    const addForm = document.getElementById('addToCartForm');

    let chosenSize = '';
    let chosenColor = '';

    const refreshVariant = () => {
        if (!variants.length) return;
        const match = variants.find(v => v.size === chosenSize && v.color === chosenColor);
        if (variantStock) {
            variantStock.textContent = match
                ? (match.stock > 0 ? `${match.stock} available` : 'Sold out for this combination')
                : (chosenSize || chosenColor ? 'Choose an available size and color combination.' : '');
            variantStock.classList.toggle('out', !!match && match.stock <= 0);
        }
        if (addForm) {
            const button = addForm.querySelector('button[type="submit"]');
            const quantityInput = addForm.querySelector('input[name="quantity"]');
            const valid = !!match && match.stock > 0;
            button.disabled = !valid;
            button.title = valid ? '' : 'Choose an available size and color';
            if (quantityInput && match) {
                quantityInput.max = match.stock;
                if (Number(quantityInput.value) > match.stock) quantityInput.value = match.stock;
            }
        }
    };

    sizeButtons.forEach(button => {
        button.addEventListener('click', () => {
            chosenSize = button.dataset.size;
            if (sizeInput) sizeInput.value = chosenSize;
            if (selectedSize) selectedSize.textContent = chosenSize;
            sizeButtons.forEach(item => item.classList.toggle('selected', item === button));
            refreshVariant();
        });
    });

    colorButtons.forEach(button => {
        button.addEventListener('click', () => {
            chosenColor = button.dataset.color;
            if (colorInput) colorInput.value = chosenColor;
            if (selectedColor) selectedColor.textContent = chosenColor;
            colorButtons.forEach(item => item.classList.toggle('selected', item === button));
            refreshVariant();
        });
    });

    if (addForm && variants.length) {
        addForm.addEventListener('submit', event => {
            if (!chosenSize || !chosenColor) {
                event.preventDefault();
                if (variantStock) variantStock.textContent = 'Please choose a size and color first.';
            }
        });
        refreshVariant();
    }

    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', () => {
            img.style.opacity = '0.25';
        });
    });
});
