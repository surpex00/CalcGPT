document.addEventListener('DOMContentLoaded', () => {
    const expressionInput = document.getElementById('expressionInput');
    const askAiButton = document.getElementById('askAiButton');
    const imageInput = document.getElementById('imageInput');
    const analyzeImageButton = document.getElementById('analyzeImageButton');
    const aiOutput = document.getElementById('aiOutput');
    const loadingIndicator = document.getElementById('loadingIndicator');

    askAiButton.addEventListener('click', async () => {
        const expression = expressionInput.value.trim();
        if (!expression) {
            aiOutput.textContent = 'Please enter an expression.';
            return;
        }

        loadingIndicator.classList.remove('hidden');
        aiOutput.textContent = '';

        try {
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expression: expression }),
            });

            const data = await response.json();

            if (response.ok) {
                aiOutput.innerHTML = marked.parse(data.result);
            } else {
                aiOutput.textContent = `Error: ${data.error || 'Something went wrong.'}`;
            }
        } catch (error) {
            aiOutput.textContent = `Network error: ${error.message}`;
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    });

    analyzeImageButton.addEventListener('click', async () => {
        const file = imageInput.files[0];
        if (!file) {
            aiOutput.textContent = 'Please select an image file.';
            return;
        }

        loadingIndicator.classList.remove('hidden');
        aiOutput.textContent = '';

        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64Image = e.target.result; // This is the base64 string

            try {
                const response = await fetch('/analyze_image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image: base64Image }),
                });

                const data = await response.json();

                if (response.ok) {
                    aiOutput.innerHTML = marked.parse(data.result);
                } else {
                    aiOutput.textContent = `Error: ${data.error || 'Something went wrong.'}`;
                }
            } catch (error) {
                aiOutput.textContent = `Network error: ${error.message}`;
            } finally {
                loadingIndicator.classList.add('hidden');
            }
        };
        reader.readAsDataURL(file); // Read file as base64 data URL
    });
});
