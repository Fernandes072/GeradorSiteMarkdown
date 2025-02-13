/**
 * @autor Carlos Augusto de S. Almeida
 * @data Novembro de 2024
 */

/**
 * Copia o conteúdo de um elemento <code> para a área de transferência.
 *
 * @async
 * @function copiarCodigo
 * @param {HTMLButtonElement} button - O botão que aciona a cópia do código.
 * @returns {Promise<void>} Uma promessa que é resolvida quando o texto é copiado com sucesso.
 */
async function copiarCodigo (button) {
    const parent = button.parentElement;
    const codigo = parent.querySelector("code").textContent;
    // Cria um elemento de texto temporário
    // Um elemento textarea é usado porque nos permite selecionar e copiar facilmente seu conteúdo
    const elemTmp = document.createElement("textarea");
    elemTmp.value = codigo;
    document.body.appendChild(elemTmp);
    // Seleciona o texto temporário
    elemTmp.select();
    // Copia o texto selecionado para a área de transferência do sistema
    await navigator.clipboard.writeText(elemTmp.value).then(() => {
        console.log('Texto copiado para área de transferencia');
    }).catch(error => {
        console.error('Não foi possível copiar o texto: ', error);
    });
    document.body.removeChild(elemTmp);

    // Altera o texto da tooltip para "Copiado"
    const tooltip = button.querySelector('.ca-tooltip-bt-copiar');
    tooltip.textContent = "Copiado!";
    setTimeout(() => {
        tooltip.textContent = 'Copiar';
    }, 5000); // Volta para o texto original após 5 seg
}


function createButtonsCopiarCodigo() {
    const codeDivsLst = document.querySelectorAll('div.sourceCode');
    for (let i = 0; i < codeDivsLst.length; i++) {
        const codeDiv = codeDivsLst[i];
        // Cria o botão "Copiar" como um elemento HTML
        const bt = document.createElement('div');
        bt.className = 'ca-copy-button';
        bt.setAttribute('onclick', 'copiarCodigo(this)');
        bt.innerHTML = `\
            <svg viewBox="0 0 16 16" width="16"> \
                <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"></path> \
                <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"></path> \
            </svg> \
            <span class="ca-tooltip-bt-copiar ca-tooltip">Copiar</span>`;
        //
        codeDiv.appendChild(bt);
    }
}
createButtonsCopiarCodigo();
