async function sendCommand() {
    const text = document.getElementById('userInput').value;
    const resBox = document.getElementById('response');

    resBox.innerHTML = '';
    if(!text.trim()){
        resBox.innerHTML = '<p style = "color: red;">Please enter a command.</p>';
        return;
    }
    resBox.innerHTML = '<p><i>Processing...</i></p>';

    try{
        const response = await
        fetch('/process',{
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({text: text})
        });
        if(!response.ok){
            throw new Error('HTTP error! status: ${response.status}');
        }
        const data = await response.json();
        resBox.innerHTML = `<p><b>AI:</b> ${data.ai_response}</p>`;
    } catch (error){
        console.error("Error sending command:", error);
        resBox.innerHTML = '<p style="color: red;">Error: Could not process command. Please try again.</p>'
    }  
}