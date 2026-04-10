document.addEventListener("DOMContentLoaded", () => {
  const userInput = document.getElementById("inputBox");
  const voiceBtn = document.getElementById("voiceBtn");
  const sendBtn = document.getElementById("sendBtn");
  const uploadForm = document.getElementById("uploadForm");
  const ordersList = document.getElementById("ordersList");
  const fileInput = document.querySelector('input[name="file"]');
  const previewContainer = document.getElementById("preview");

  // Image Preview Logic
  if (fileInput) {
    fileInput.onchange = () => {
    const [file] = fileInput.files;
    if (file) {
      previewContainer.innerHTML = `
        <p>Selected: ${file.name}</p>
        <img src="${URL.createObjectURL(file)}" style="max-width: 200px; border-radius: 8px; margin-top: 10px;">
      `;
    }
  };
  }

  // Mic setup
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition && voiceBtn) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    voiceBtn.onclick = () => {
    if (voiceBtn.classList.contains("recording")) {
      recognition.stop();
      voiceBtn.classList.remove("recording");
    } else {
      recognition.start();
      voiceBtn.classList.add("recording");
    }
  };

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (userInput) userInput.value = transcript;
    };

    recognition.onend = () => {
      voiceBtn.classList.remove("recording");
    };
  }

  // Send button
  if (sendBtn && userInput) {
    sendBtn.onclick = async () => {
      const text = userInput.value;
      const res = await fetch("/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      console.log("Response:", data);
    };
  }

  // Upload form
  if (uploadForm) {
    uploadForm.onsubmit = async (e) => {
      e.preventDefault();
      const formData = new FormData(uploadForm);

      const res = await fetch("/upload-style", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.text();
        alert("Upload failed: " + err);
        return;
      }

      const data = await res.json();
      console.log("Upload response:", data);
      alert("Order uploaded successfully!");
      
      // Display summary of the order taken on the same page
      if (previewContainer) {
        console.log("Attempting to display order summary in previewContainer with data:", data);
        previewContainer.innerHTML = `
          <div class="order-summary" style="background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-top: 20px;">
            <h3 style="margin-top: 0; color: #2c3e50;">Order Summary</h3>
            <p><strong>Customer:</strong> ${data.customer}</p>
            <p><strong>Due Date:</strong> ${data.due_date}</p>
            <p><strong>Measurements:</strong> ${data.measurements}</p>
            ${data.image_url ? `<img src="${data.image_url}" alt="Style" style="max-width: 150px; border-radius: 4px; margin-top: 10px;">` : ""}
          </div>
        `;
      }

      // Refresh logic
      uploadForm.reset();
      loadOrders(); 
    };
  }

  // Load orders
 async function loadOrders() {
    const container = document.getElementById("ordersList");
    if (!container) {
      console.warn("Element #ordersList not found on this page.");
      return; 
    }

    container.innerHTML = "<p>Loading orders...</p>"; 

    try {
      const res = await fetch("/orders");
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      console.log("Fetched orders:", data);

      container.innerHTML = ""; // Clear loading message

      if (data.length === 0) {
        container.innerHTML = "<p>No orders found. Start by creating a new order!</p>";
        return;
      }

      data.forEach((order, index) => {
        container.innerHTML += `
          <div class="order-card">
            <h3>Order #${index + 1}</h3>
            <p><strong>Customer:</strong> ${order.customer}</p>
            <p><strong>Due Date:</strong> ${order.due_date}</p>
            <p><strong>Measurements:</strong> ${order.measurements}</p>
            ${order.image_url ? `<img src="${order.image_url}" alt="Uploaded Style" style="max-width: 100px; border-radius: 4px; margin-top: 5px;">` : ""}
            <div class="order-actions">
              <button class="edit-btn" data-id="${order.id}">Edit</button>
              <button class="delete-btn" data-id="${order.id}">Delete</button>
            </div>
          </div>
        `;
      });

      // Add event listeners for delete and edit buttons
      document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", async (e) => {
          const orderId = e.target.dataset.id;
          if (confirm(`Are you sure you want to delete Order #${orderId}?`)) {
            await deleteOrder(orderId);
          }
        });
      });

      document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", async (e) => {
          const orderId = e.target.dataset.id;
          await editOrder(orderId);
        });
      });
    } catch (error) {
      console.error("Failed to load orders:", error);
      container.innerHTML = `<p style="color: red;">Error loading orders: ${error.message}. Please try again later.</p>`;
    }
  }

  async function deleteOrder(orderId) {
    try {
      const res = await fetch(`/orders/${orderId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      alert(`Order #${orderId} deleted successfully!`);
      loadOrders(); // Refresh the list
    } catch (error) {
      console.error("Failed to delete order:", error);
      alert(`Error deleting order: ${error.message}`);
    }
  }

  async function editOrder(orderId) {
    const newMeasurements = prompt("Enter new measurements for this order:", "");
    if (newMeasurements === null || newMeasurements.trim() === "") {
      return; // User cancelled or entered empty string
    }
    try {
      const res = await fetch(`/orders/${orderId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ measurements: newMeasurements }),
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      alert(`Order #${orderId} updated successfully!`);
      loadOrders(); // Refresh the list
    } catch (error) {
      console.error("Failed to update order:", error);
      alert(`Error updating order: ${error.message}`);
    }
  }

  loadOrders();
});
