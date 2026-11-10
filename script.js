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

    // 4. Lógica de aba e visualização dos dados
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');

    function setActiveTab(tabName) {
        tabButtons.forEach((button) => {
            const isActive = button.dataset.tab === tabName;
            button.classList.toggle('active', isActive);
            button.classList.toggle('bg-primary', isActive);
            button.classList.toggle('text-white', isActive);
            button.classList.toggle('shadow-sm', isActive);
            button.classList.toggle('bg-gray-100', !isActive);
            button.classList.toggle('text-gray-700', !isActive);
            button.classList.toggle('dark:bg-gray-800', !isActive);
            button.classList.toggle('dark:text-gray-200', !isActive);
        });

        tabPanels.forEach((panel) => {
            const shouldShow = panel.id === `${tabName}-panel`;
            panel.classList.toggle('hidden', !shouldShow);
        });
    }

    tabButtons.forEach((button) => {
        button.addEventListener('click', () => setActiveTab(button.dataset.tab));
    });

    function parseCsvRows(text) {
        const primeiraLinha = text.split(/\r?\n/, 1)[0] || '';
        const delimitadores = [',', ';', '\t'];
        const delimitador = delimitadores.reduce((melhor, candidato) => {
            const quantidade = primeiraLinha.split(candidato).length - 1;
            return quantidade > melhor.quantidade
                ? { valor: candidato, quantidade }
                : melhor;
        }, { valor: ',', quantidade: 0 }).valor;
        const rows = [];
        let row = [];
        let value = '';
        let inQuotes = false;

        for (let index = 0; index < text.length; index += 1) {
            const char = text[index];

            if (char === '"') {
                if (inQuotes && text[index + 1] === '"') {
                    value += '"';
                    index += 1;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (char === delimitador && !inQuotes) {
                row.push(value);
                value = '';
            } else if ((char === '\n' || char === '\r') && !inQuotes) {
                if (char === '\r' && text[index + 1] === '\n') {
                    index += 1;
                }
                row.push(value);
                value = '';

                const hasData = row.some((cell) => String(cell).trim() !== '');
                if (hasData) {
                    rows.push(row);
                }
                row = [];
            } else {
                value += char;
            }
        }

        if (value.length > 0 || row.length > 0) {
            row.push(value);
            const hasData = row.some((cell) => String(cell).trim() !== '');
            if (hasData) {
                rows.push(row);
            }
        }

        return rows;
    }

    async function renderDataPreview(file) {
        const table = document.getElementById('data-preview-table');
        const dataRecords = document.getElementById('data-records');
        const targetColumn = document.getElementById('target-column');

        if (!file) {
            table.innerHTML = '';
            dataRecords.textContent = 'Nenhum arquivo carregado';
            targetColumn.replaceChildren(new Option('Carregue um arquivo para selecionar a coluna...', ''));
            targetColumn.disabled = true;
            return;
        }

        let rows = [];
        const nomeArquivo = file.name.toLowerCase();

        try {
            if (nomeArquivo.endsWith('.csv')) {
                const text = await file.text();
                rows = parseCsvRows(text);
            } else if (nomeArquivo.endsWith('.xlsx')) {
                const data = await file.arrayBuffer();
                const workbook = XLSX.read(data, { type: 'array' });
                const planilha = workbook.Sheets[workbook.SheetNames[0]];
                rows = XLSX.utils.sheet_to_json(planilha, { header: 1, defval: '' });
            }
        } catch (error) {
            dataRecords.textContent = 'Erro ao carregar a pré-visualização';
            table.innerHTML = `<tbody><tr><td class="p-4 text-sm text-red-600">Não foi possível ler o arquivo selecionado.</td></tr></tbody>`;
            targetColumn.replaceChildren(new Option('Não foi possível ler as colunas do arquivo', ''));
            targetColumn.disabled = true;
            console.error(error);
            return;
        }

        const linhasValidas = rows.filter((row) => row && row.some((cell) => String(cell).trim() !== ''));

        if (!linhasValidas.length) {
            table.innerHTML = '<tbody><tr><td class="p-4 text-sm text-gray-500">Arquivo sem dados válidos para exibir.</td></tr></tbody>';
            dataRecords.textContent = '0 linhas';
            targetColumn.replaceChildren(new Option('Arquivo sem colunas disponíveis', ''));
            targetColumn.disabled = true;
            return;
        }

        const maxCols = Math.max(...linhasValidas.map((row) => row.length), 1);
        targetColumn.replaceChildren();
        Array.from({ length: maxCols }, (_, index) => {
            const nome = String(linhasValidas[0][index] ?? '').trim();
            const descricao = nome ? ` — ${nome}` : '';
            targetColumn.add(new Option(`Coluna ${index + 1}${descricao}`, String(index)));
        });
        targetColumn.value = String(maxCols - 1);
        targetColumn.disabled = false;

        const colunaTarget = Number(targetColumn.value);
        const headers = Array.from({ length: maxCols }, (_, index) => {
            const isTarget = index === colunaTarget;
            const rotulo = isTarget ? `${index + 1} · TARGET` : index + 1;
            const classe = isTarget ? 'target-column' : '';
            return `<th class="px-3 py-2 ${classe}">${rotulo}</th>`;
        }).join('');
        const limit = Math.min(linhasValidas.length, 30);
        const bodyRows = linhasValidas.slice(0, limit).map((row, rowIndex) => {
            const cells = Array.from({ length: maxCols }, (_, columnIndex) => {
                const value = row[columnIndex] ?? '';
                const classe = columnIndex === colunaTarget ? 'target-column' : '';
                const valorSeguro = String(value).replace(/[&<>"']/g, (caractere) => ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;',
                })[caractere]);
                return `<td class="px-3 py-2 ${classe}">${valorSeguro}</td>`;
            }).join('');
            return `<tr><td class="row-index px-2 py-2">${rowIndex + 1}</td>${cells}</tr>`;
        }).join('');

        table.innerHTML = `
            <thead>
                <tr>
                    <th class="row-index px-2 py-2">#</th>
                    ${headers}
                </tr>
            </thead>
            <tbody>${bodyRows}</tbody>
        `;

        dataRecords.textContent = `${limit} de ${linhasValidas.length} linhas`;
        setActiveTab('dados');

        targetColumn.onchange = () => {
            const novaColuna = Number(targetColumn.value);
            table.querySelectorAll('thead th:not(.row-index), tbody td:not(.row-index)').forEach((cell, index) => {
                const coluna = index % maxCols;
                cell.classList.toggle('target-column', coluna === novaColuna);
                if (cell.tagName === 'TH') {
                    cell.textContent = coluna === novaColuna ? `${coluna + 1} · TARGET` : String(coluna + 1);
                }
            });
        };
    }

    // 5. Lógica de Upload de Arquivo (Visual)
    const fileUploadBox = document.querySelector('.border-dashed');
    const fileInput = document.getElementById('file-upload');
    const fileText = fileUploadBox.querySelector('span');

    fileUploadBox.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            const selectedFile = e.target.files[0];
            fileText.textContent = selectedFile.name;
            fileUploadBox.classList.add('border-primary', 'bg-blue-50', 'dark:bg-gray-700');
            await renderDataPreview(selectedFile);
        } else {
            fileText.textContent = 'Carregar Arquivo (.csv, .xlsx)';
            fileUploadBox.classList.remove('border-primary', 'bg-blue-50', 'dark:bg-gray-700');
            await renderDataPreview(null);
        }
    });

    const taskType = document.getElementById('task-type');
    const analysisMethod = document.getElementById('analysis-method');
    const defaultConfiguration = document.getElementById('default-configuration');
    const runButton = document.getElementById('run-button');
    const runAllButton = document.getElementById('run-all-button');
    const status = document.getElementById('analysis-status');

    const metodosPorTipo = {
        classificacao: [
            { value: 'svc', label: 'SVC (Máquinas de Vetores de Suporte)' },
            { value: 'random_forest', label: 'Random Forest' },
        ],
        regressao: [
            { value: 'mlp', label: 'Rede Neural MLP' },
            { value: 'random_forest', label: 'Random Forest' },
        ],
    };

    function atualizarMetodos() {
        const metodos = metodosPorTipo[taskType.value] || [];
        analysisMethod.replaceChildren();

        if (!metodos.length) {
            analysisMethod.disabled = true;
            analysisMethod.add(new Option('Selecione primeiro o tipo de tarefa...', ''));
            return;
        }

        analysisMethod.disabled = false;
        analysisMethod.add(new Option('Selecione um método...', ''));
        metodos.forEach((metodo) => {
            analysisMethod.add(new Option(metodo.label, metodo.value));
        });
    }

    taskType.addEventListener('change', atualizarMetodos);

    function showStatus(message, isError = false) {
        status.textContent = message;
        status.className = `mb-4 rounded-lg px-4 py-3 text-sm ${isError
            ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200'
            : 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'}`;
        status.classList.remove('hidden');
    }

    const assistantQuestion = document.getElementById('assistant-question');
    const assistantAskButton = document.getElementById('assistant-ask-button');
    const assistantButtonLabel = document.getElementById('assistant-button-label');
    const assistantAnswer = document.getElementById('assistant-answer');

    assistantAskButton.addEventListener('click', async () => {
        const pergunta = assistantQuestion.value.trim();
        if (!pergunta) {
            showStatus('Descreva seu problema para perguntar ao assistente.', true);
            return;
        }

        const formData = new FormData();
        formData.append('pergunta', pergunta);
        if (fileInput.files.length) {
            formData.append('arquivo', fileInput.files[0]);
        }

        assistantAskButton.disabled = true;
        assistantButtonLabel.textContent = 'Carregando...';
        assistantAnswer.textContent = '';
        assistantAnswer.classList.add('hidden');
        showStatus('Consultando o assistente de IA...');

        try {
            const response = await fetch('/api/perguntar', {
                method: 'POST',
                body: formData,
            });
            let data;
            try {
                data = await response.json();
            } catch {
                throw new Error('O servidor retornou uma resposta inválida.');
            }
            if (!response.ok) {
                throw new Error(data.erro || 'Não foi possível obter uma resposta do assistente.');
            }
            assistantAnswer.textContent = data.resposta;
            assistantAnswer.classList.remove('hidden');
            showStatus('Resposta do assistente recebida.');
        } catch (error) {
            const mensagem = error instanceof TypeError
                ? 'Não foi possível conectar ao assistente. Verifique sua conexão e tente novamente.'
                : error.message || 'Não foi possível obter uma resposta do assistente.';
            assistantAnswer.textContent = mensagem;
            assistantAnswer.classList.remove('hidden');
            showStatus(mensagem, true);
        } finally {
            assistantAskButton.disabled = false;
            assistantButtonLabel.textContent = 'Perguntar';
        }
    });

    async function runAnalysis(method, model = '') {
        if (!fileInput.files.length) {
            throw new Error('Selecione um arquivo CSV ou XLSX.');
        }
        if (!method) {
            throw new Error('Selecione classificação ou regressão.');
        }

        const formData = new FormData();
        formData.append('arquivo', fileInput.files[0]);
        formData.append('metodo', method);
        const targetColumn = document.getElementById('target-column');
        if (!targetColumn.disabled && targetColumn.value !== '') {
            formData.append('target_column', targetColumn.value);
        }
        if (model) {
            formData.append('modelo', model);
        }
        formData.append('padrao', defaultConfiguration.checked ? 'true' : 'false');
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
        const melhores = Object.values(resultado.modelos);
        const melhor = melhores.reduce((atual, candidato) =>
            candidato.acuracia >= atual.acuracia ? candidato : atual
        );
        document.getElementById('classification-mc').textContent = melhor.matriz_confusao.length;
        document.getElementById('classification-ac').textContent = `${(melhor.acuracia * 100).toFixed(2)}%`;
        document.getElementById('classification-pr').textContent = `${(melhor.precisao * 100).toFixed(2)}%`;
        document.getElementById('classification-re').textContent = `${(melhor.recall * 100).toFixed(2)}% / ${(melhor.f1 * 100).toFixed(2)}%`;
    }

    function renderRegression(resultado) {
        const melhores = Object.values(resultado.modelos);
        const melhor = melhores.reduce((atual, candidato) =>
            candidato.r2 >= atual.r2 ? candidato : atual
        );
        document.getElementById('regression-mae').textContent = melhor.mae.toFixed(4);
        document.getElementById('regression-r2').textContent = melhor.r2.toFixed(4);
        document.getElementById('regression-mse').textContent = melhor.mse.toFixed(4);
        document.getElementById('regression-rmse').textContent = melhor.rmse.toFixed(4);
    }

    async function executarMetodo(method) {
        const result = await runAnalysis(method, analysisMethod.value);
        if (method === 'classificacao') {
            renderClassification(result);
        } else {
            renderRegression(result);
        }
    }

    runButton.addEventListener('click', async () => {
        runButton.disabled = true;
        try {
            if (!taskType.value) {
                throw new Error('Selecione o tipo de tarefa.');
            }
            if (!analysisMethod.value) {
                throw new Error('Selecione o método.');
            }
            showStatus('Executando análise...');
            await executarMetodo(taskType.value);
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

    setActiveTab('resultados');
});