document.addEventListener('DOMContentLoaded', () => {
    // 1. Atualização do Slider de Porcentagem
    const rangeInput = document.getElementById('test-percentage');
    const rangeVal = document.getElementById('range-val');

    rangeInput.addEventListener('input', (e) => {
        rangeVal.textContent = `${e.target.value}%`;
    });

    // 2. Lógica do Dropdown de Usuário
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('hidden');
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener('click', (e) => {
        if (!userDropdown.contains(e.target) && !userMenuBtn.contains(e.target)) {
            userDropdown.classList.add('hidden');
        }
    });

    // 3. Lógica do Dark Mode
    const themeToggle = document.getElementById('theme-toggle');
    const darkModeCheckbox = document.getElementById('dark-mode-checkbox');
    const html = document.documentElement;

    // Verificar preferência guardada
    if (localStorage.getItem('theme') === 'dark' || 
       (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        html.classList.add('dark');
        darkModeCheckbox.checked = true;
    } else {
        html.classList.remove('dark');
        darkModeCheckbox.checked = false;
    }

    // Função para alternar o tema
    function toggleTheme() {
        if (html.classList.contains('dark')) {
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            darkModeCheckbox.checked = false;
        } else {
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            darkModeCheckbox.checked = true;
        }
    }

    // Ouvintes de evento para o Dark Mode
    themeToggle.addEventListener('click', (e) => {
        // Evita disparar duas vezes se clicar diretamente no checkbox
        if(e.target !== darkModeCheckbox) {
            toggleTheme();
        }
    });

    darkModeCheckbox.addEventListener('change', () => {
        toggleTheme();
    });
    
    // 4. Lógica de Upload de Arquivo (Visual)
    const fileUploadBox = document.querySelector('.border-dashed');
    const fileInput = document.getElementById('file-upload');
    const fileText = fileUploadBox.querySelector('span');

    fileUploadBox.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileText.textContent = e.target.files[0].name;
            fileUploadBox.classList.add('border-primary', 'bg-blue-50', 'dark:bg-gray-700');
        } else {
            fileText.textContent = 'Carregar Arquivo (.csv, .xlsx)';
            fileUploadBox.classList.remove('border-primary', 'bg-blue-50', 'dark:bg-gray-700');
        }
    });

    const analysisMethod = document.getElementById('analysis-method');
    const runButton = document.getElementById('run-button');
    const runAllButton = document.getElementById('run-all-button');
    const status = document.getElementById('analysis-status');

    function showStatus(message, isError = false) {
        status.textContent = message;
        status.className = `mb-4 rounded-lg px-4 py-3 text-sm ${isError
            ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200'
            : 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'}`;
        status.classList.remove('hidden');
    }

    async function runAnalysis(method) {
        if (!fileInput.files.length) {
            throw new Error('Selecione um arquivo CSV ou XLSX.');
        }
        if (!method) {
            throw new Error('Selecione classificação ou regressão.');
        }

        const formData = new FormData();
        formData.append('arquivo', fileInput.files[0]);
        formData.append('metodo', method);
        formData.append('test_size', rangeInput.value);

        const response = await fetch('/api/analisar', {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.erro || 'Erro ao executar a análise.');
        }
        return data;
    }

    function renderClassification(resultado) {
        const melhor = resultado.modelos.random_forest.acuracia >= resultado.modelos.mlp.acuracia
            ? resultado.modelos.random_forest
            : resultado.modelos.mlp;
        document.getElementById('classification-mc').textContent = melhor.matriz_confusao.length;
        document.getElementById('classification-ac').textContent = `${(melhor.acuracia * 100).toFixed(2)}%`;
        document.getElementById('classification-pr').textContent = `${(melhor.precisao * 100).toFixed(2)}%`;
        document.getElementById('classification-re').textContent = `${(melhor.recall * 100).toFixed(2)}% / ${(melhor.f1 * 100).toFixed(2)}%`;
    }

    function renderRegression(resultado) {
        const melhor = resultado.modelos.random_forest.r2 >= resultado.modelos.mlp.r2
            ? resultado.modelos.random_forest
            : resultado.modelos.mlp;
        document.getElementById('regression-mae').textContent = melhor.mae.toFixed(4);
        document.getElementById('regression-r2').textContent = melhor.r2.toFixed(4);
        document.getElementById('regression-mse').textContent = melhor.mse.toFixed(4);
        document.getElementById('regression-rmse').textContent = melhor.rmse.toFixed(4);
    }

    async function executarMetodo(method) {
        const result = await runAnalysis(method);
        if (method === 'classificacao') {
            renderClassification(result);
        } else {
            renderRegression(result);
        }
    }

    runButton.addEventListener('click', async () => {
        runButton.disabled = true;
        try {
            showStatus('Executando análise...');
            await executarMetodo(analysisMethod.value);
            showStatus('Análise concluída.');
        } catch (error) {
            showStatus(error.message, true);
        } finally {
            runButton.disabled = false;
        }
    });

    runAllButton.addEventListener('click', async () => {
        runAllButton.disabled = true;
        try {
            showStatus('Executando classificação e regressão...');
            await executarMetodo('classificacao');
            await executarMetodo('regressao');
            showStatus('Todas as análises foram concluídas.');
        } catch (error) {
            showStatus(error.message, true);
        } finally {
            runAllButton.disabled = false;
        }
    });
});