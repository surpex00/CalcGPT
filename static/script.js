document.addEventListener('DOMContentLoaded', () => {
    const expressionInput = document.getElementById('expressionInput');
    const askAiButton = document.getElementById('askAiButton');
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
                aiOutput.textContent = data.result;
            } else {
                aiOutput.textContent = `Error: ${data.error || 'Something went wrong.'}`;
            }
        } catch (error) {
            aiOutput.textContent = `Network error: ${error.message}`;
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    });
});
