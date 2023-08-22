const form = document.getElementById('form');
        const output = document.getElementById('output');

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const url = document.getElementById('url').value;
            await fetch('/', {
                method: 'POST',
                body: JSON.stringify({ url }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        });

        setInterval(async () => {
            const response = await fetch('/output');
            const text = await response.text();
            output.value = text;
        }, 3000);