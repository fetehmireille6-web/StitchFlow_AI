/**
 * StitchFlow AI - Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("🧵 StitchFlow Script Initialized");
    
    // Navigation Drawer Logic
    const menuBtn = document.querySelector('.menu-btn');
    const closeBtn = document.querySelector('.close-btn');
    const drawer = document.querySelector('.drawer');
    const overlay = document.querySelector('.overlay');

    if (menuBtn && drawer && overlay) {
        menuBtn.addEventListener('click', () => {
            drawer.classList.add('open');
            overlay.classList.add('active');
        });

        const closeMenu = () => {
            drawer.classList.remove('open');
            overlay.classList.remove('active');
        };

        if (closeBtn) closeBtn.addEventListener('click', closeMenu);
        overlay.addEventListener('click', closeMenu);
    }

    // AI Command Processing
    window.processAICommand = async (text) => {
        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            return await response.json();
        } catch (error) {
            console.error("AI Error:", error);
            return { status: "error", message: error.message };
        }
    };

    // Image Analysis Logic
    window.analyzeImage = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/process-image', {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error("Image Analysis Error:", error);
            return { status: "error", message: error.message };
        }
    };

    // SMS Notification
    window.sendSMS = async (orderId) => {
        try {
            const response = await fetch(`/send-sms/${orderId}`, { method: 'POST' });
            const result = await response.json();
            alert(result.message);
            return result;
        } catch (error) {
            alert("Failed to send SMS");
        }
    };

    // Delete Order
    window.deleteOrder = async (orderId) => {
        if (!confirm("Are you sure you want to delete this order?")) return;
        
        try {
            const response = await fetch(`/orders/${orderId}`, { method: 'DELETE' });
            if (response.ok) {
                location.reload();
            }
        } catch (error) {
            console.error("Delete Error:", error);
        }
    };

    // Form Utilities
    const uploadForm = document.getElementById('uploadStyleForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            const btn = uploadForm.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            }
        });
    }
});

/**
 * Display a temporary alert message
 */
function showAlert(message, type = 'info') {
    const container = document.getElementById('alert-container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    container.prepend(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 300);
    }, 4000);
}