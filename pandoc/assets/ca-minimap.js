/**
 * Classe representando um minimap com preview da página.
 *
 * Pseudocódigo:
 * 1. Inicializa o minimap criando os elementos necessários e adicionando-os ao documento.
 * 2. Clona o conteúdo da página e adiciona ao minimap, aplicando escala para reduzir o tamanho.
 * 3. Calcula os fatores de escala com base nas dimensões do conteúdo e do minimap.
 * 4. Manipula eventos de scroll para atualizar a posição e o tamanho do retângulo "area-visivel".
 * 5. Manipula cliques no minimap para rolar a página até a posição correspondente.
 * 6. Se o minimap for maior que a área visível:
 *    a. Mantém o retângulo "area-visivel" no meio da área visível do minimap.
 *    b. Move o minimap para cima ou para baixo para acompanhar o scroll da página.
 * 7. Oculta automaticamente o minimap se a largura da janela for menor que o max-width do '.ca-minimap-content'.
 *    a. O minimap reaparece quando o mouse está a menos de 100px do canto direito da tela.
 */
class Minimap {
    static eyeOpen = '<svg viewBox="0 0 20 20" width="20"><path d="M.2 10a11 11 0 0 1 19.6 0A11 11 0 0 1 .2 10zm9.8 4a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0-2a2 2 0 1 1 0-4 2 2 0 0 1 0 4z" fill="#997404"/></svg>';
    static close = '<svg viewBox="0 0 512 512" width="20"><path d="M437.5 386.6 306.9 256l130.6-130.6c14.1-14.1 14.1-36.8 0-50.9-14.1-14.1-36.8-14.1-50.9 0L256 205.1 125.4 74.5c-14.1-14.1-36.8-14.1-50.9 0-14.1 14.1-14.1 36.8 0 50.9L205.1 256 74.5 386.6c-14.1 14.1-14.1 36.8 0 50.9 14.1 14.1 36.8 14.1 50.9 0L256 306.9l130.6 130.6c14.1 14.1 36.8 14.1 50.9 0 14-14.1 14-36.9 0-50.9z" fill="#997404"></path></svg>';
    // static eyeClosed = '<svg viewBox="0 0 20 20" width="20"><path d="M12.81 4.36l-1.77 1.78a4 4 0 0 0-4.9 4.9l-2.76 2.75C2.06 12.79.96 11.49.2 10a11 11 0 0 1 12.6-5.64zm3.8 1.85c1.33 1 2.43 2.3 3.2 3.79a11 11 0 0 1-12.62 5.64l1.77-1.78a4 4 0 0 0 4.9-4.9l2.76-2.75zm-.25-3.99l1.42 1.42L3.64 17.78l-1.42-1.42L16.36 2.22z" fill="#997404"/></svg>';

    constructor() {
        // Cria o contêiner do minimap
        this.minimap = document.createElement('div');
        this.minimap.id = 'ca-minimap';
        this.minimap.classList.add('hidden'); // Inicia oculto para evitar flicker

        // Cria o contêiner para o conteúdo em miniatura
        this.miniContent = document.createElement('div');
        this.miniContent.className = 'ca-mini-content';

        // Cria o retângulo "area-visivel"
        this.areaVisivel = document.createElement('div');
        this.areaVisivel.className = 'ca-rect-area-visivel';

        const hideBtnContainer = document.createElement('div');
        hideBtnContainer.className = 'ca-minimap-hide-btn-container';

        // Cria o bt para Ocultar minimap
        this.hideBtn = document.createElement('button');
        this.hideBtn.className = 'ca-minimap-hide-btn';

        // Cria o div interno ao bt
        this.spanHideBtn = document.createElement('span');
        this.spanHideBtn.className = 'ca-minimap-hide-btn-icon';
        this.spanHideBtn.innerHTML = Minimap.close;

        this.minimapHiddenByUser = sessionStorage.getItem('minimapHiddenByUser') === 'true'; // recupera a preferência do usuário da sessionStorage
        this.minimapIsHidden = this.minimapHiddenByUser;
        this.hideBtn.addEventListener('click', () => { 
            this.minimapHiddenByUser = !this.minimapHiddenByUser;
            sessionStorage.setItem('minimapHiddenByUser', this.minimapHiddenByUser.toString()); // guarda a preferência do usuário
            this.__hidden(this.minimapHiddenByUser);
            this.hideBtn.disabled = true;
            setTimeout(() => { this.hideBtn.disabled = false; }, 250); // Evita cliques múltiplos
        });

        // Cria o tooltip para o bt
        this.tooltip = document.createElement('span');
        this.tooltip.classList.add('ca-minimap-hide-btn', 'ca-tooltip');
        this.tooltip.textContent = 'Ocultar minimap';

        // Adiciona o botão ao body
        hideBtnContainer.append(this.hideBtn);
        this.hideBtn.append(this.spanHideBtn, this.tooltip);
        // Adiciona os elementos ao minimap
        this.minimap.append(this.miniContent, this.areaVisivel);
        // Adiciona o minimap ao body
        document.body.append(this.minimap, hideBtnContainer);

        // Calcula os fatores de escala iniciais
        this.__updateScalingFactors();

        // Vincula os manipuladores de eventos
        window.addEventListener('scroll', this.__onScroll.bind(this));
        window.addEventListener('resize', this.__onResize.bind(this));
        this.minimap.addEventListener('click', this.__onMinimapClick.bind(this));

        // Atualiza a visibilidade do minimap
        this.__updateMinimapVisibility();

        // Atualiza inicialmente
        this.__onScroll();

        // Inicializa o minimap ao carregar o conteúdo
        document.addEventListener('DOMContentLoaded', this.__cloneContent());

        window.addEventListener('load', () => { // Aguarda TODO o carregamento para redimensionar o minimap.
            setTimeout(() => {                  // - Útil para evitar problemas com imagens carregando e height da página.
                this.__onResize();
            }, 2000);  // 1. onResize() após 2 seg.
            setTimeout(() => {
                this.__onResize();
            }, 15000); // 2. onResize() após 15 seg.
        });
    }


    /**
     * Clona o conteúdo da página e adiciona ao minimap.
     * Passos:
     * 1. Clona o elemento '.ca-minimap-content'.
     * 2. Limpa o miniContent e adiciona o clone.
     */
    __cloneContent() {
        const fragment = document.createDocumentFragment();
        
        // 1. Clona o elemento '.ca-minimap-content' e remove os IDs, eventos e scripts
        const contentClone = document.querySelector('.ca-minimap-content').cloneNode(true);
        
        // Remove todos os IDs do clone
        contentClone.querySelectorAll('[id]').forEach(el => el.removeAttribute('id'));
        
        // Remove todos os elementos <script> do clone
        contentClone.querySelectorAll('script').forEach(script => script.remove());
        
        // Desativa todos os eventos do clone
        const disableEvents = (element) => {
            const clone = element.cloneNode(true);
            clone.replaceWith(clone.cloneNode(true));
            return clone;
        };
        disableEvents(contentClone);
        
        fragment.appendChild(contentClone);
        
        // 2. Limpa o miniContent e adiciona o fragment
        this.miniContent.innerHTML = '';
        this.miniContent.appendChild(fragment);
    }
    //region cloneContent, versão alternativa
    // cloneContent() {
    //     const contentElement = document.querySelector('.ca-minimap-content');
    
    //     // Usa html2canvas para tirar um screenshot do elemento com opções ajustadas
    //     html2canvas(contentElement, { backgroundColor: null }).then(canvas => {
    //         // Limpa o miniContent e adiciona o canvas
    //         this.miniContent.innerHTML = '';
    //         this.miniContent.appendChild(canvas);
    //     }).catch(error => {
    //         console.error('Erro ao gerar o screenshot:', error);
    //     });
    // }
    // requer
    // <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.4.1/html2canvas.min.js"></script>
    // Substituir document.addEventListener('DOMContentLoaded', () => new Minimap());
    // window.addEventListener('load', () => {
    //     setTimeout(() => {
    //         new Minimap();
    //     }, 5000); // 5000 milissegundos = 5 segundos
    // });
    //endregion cloneContent

    
    /**
     * Atualiza os fatores de escala com base nas dimensões do conteúdo e do minimap.
     */
    __updateScalingFactors() {
        // Obtém o elemento de conteúdo original
        const contentElement = document.querySelector('.ca-minimap-content');

        // Obtém as dimensões do conteúdo
        this.contentWidth = contentElement.offsetWidth;
        this.contentHeight = contentElement.scrollHeight;

        // Armazena a posição do conteúdo
        this.contentTop = contentElement.offsetTop;
        this.contentLeft = contentElement.offsetLeft;

        // Define a largura fixa do minimap
        this.minimapWidth = 100; // Largura fixa de 100px
        this.minimap.style.width = `${this.minimapWidth}px`;

        // Calcula o fator de escala com base na largura
        this.scale = this.minimapWidth / this.contentWidth;
        this.scale = Math.max(this.scale, 0.1); // Escala mínima de 0.1

        // Aplica a escala ao miniContent
        this.miniContent.style.transform = `scale(${this.scale})`;
        this.miniContent.style.width = `${this.contentWidth}px`;
        this.miniContent.style.height = `${this.contentHeight}px`;

        // Atualiza a altura do minimap
        this.minimapHeight = this.contentHeight * this.scale;
        if (this.minimapHeight > this.viewportHeight) {
            this.minimapHeight = this.minimapHeight + 6; // É o oposto do que parece.
        }                                                // - Evita que o minimap ultrapasse o height da página
        this.minimap.style.height = `${this.minimapHeight}px`;

        // Armazena a altura da janela
        this.viewportHeight = window.innerHeight;
    }


    /**
     * Manipula o evento de scroll.
     */
    __onScroll() {
        // Obtém a posição de scroll e as dimensões da janela
        const scrollTop = document.documentElement.scrollTop,
              viewportHeight = window.innerHeight;
        // Calcula a posição e as dimensões do areaVisivel
        const areaVisivelTop = (scrollTop - this.contentTop) * this.scale,
              areaVisivelHeight = viewportHeight * this.scale;

        // Atualiza o estilo do areaVisivel
        Object.assign(this.areaVisivel.style, {
            top: `${areaVisivelTop}px`,
            left: `0px`,
            width: `${this.minimapWidth}px`,
            height: `${areaVisivelHeight}px`
        });

        // Ajusta a posição do minimap se a altura for maior que a da janela
        if (this.minimapHeight > viewportHeight) {
            // Calcula a posição para manter o areaVisivel no centro da tela
            let minimapTop = -areaVisivelTop + (viewportHeight / 2) - (areaVisivelHeight / 2);

            // Limita o minimapTop para não ultrapassar os limites
            const maxMinimapTop = 0,
                  minMinimapTop = viewportHeight - this.minimapHeight;
            minimapTop = Math.min(Math.max(minimapTop, minMinimapTop), maxMinimapTop);

            this.minimap.style.top = `${minimapTop}px`;
        } else {
            // Caso contrário, mantém o minimap fixo no topo
            this.minimap.style.top = '0px';
        }
    }

    /**
     * Manipula cliques no minimap.
     */
    __onMinimapClick(event) {
        // Obtém a posição do clique
        const minimapRect = this.minimap.getBoundingClientRect(),
              clickY = event.clientY - minimapRect.top;
        // Calcula a posição de scroll
        const scrollToY = (clickY / this.scale) + this.contentTop;

        // Rola a página suavemente até a posição
        window.scrollTo({
            top: scrollToY,
            behavior: 'smooth'
        });
    }

    /**
     * Manipula o evento de redimensionamento da janela.
     */
    __onResize() {
        this.__updateScalingFactors();
        this.__updateMinimapVisibility();
        this.__onScroll();
    }

    /**
     * Atualiza a visibilidade do minimap com base na largura da janela.
     * Se a largura da janela for menor que o max-width do '.ca-minimap-content', oculta o minimap.
     * Caso contrário, mostra o minimap.
     * Além disso, quando o minimap está oculto, ele reaparece quando o mouse está
     * a menos de 100px do canto direito da tela.
     */
    __updateMinimapVisibility() {
        const maxWidth = 960 + 180, // Max-width do '.ca-minimap-content' definido no CSS
              isNarrowScreen = window.innerWidth < maxWidth;

        // Oculta o minimap se a tela for estreita ou se estiver oculto pelo usuário
        this.__hidden( isNarrowScreen || this.minimapHiddenByUser );

        // Adiciona/remove o listener de movimento do mouse se ainda não estiver adicionado
        if (isNarrowScreen && !this.mouseMoveListener) {
            this.mouseMoveListener = this.__onMouseMove.bind(this);
            window.addEventListener('mousemove', this.mouseMoveListener);
        } else if (!isNarrowScreen && this.mouseMoveListener) {
            window.removeEventListener('mousemove', this.mouseMoveListener);
            this.mouseMoveListener = null;
        }
        //region mouseMoveListener mais legível
        // // ...existing code...
        // if (!this.mouseMoveListener) {
        //     this.mouseMoveListener = this.__onMouseMove.bind(this);
        //     window.addEventListener('mousemove', this.mouseMoveListener);
        // }
        // // ...existing code...

        // __onMouseMove(event) {
        //     if (this.minimapHiddenByUser || !isNarrowScreen) return;
        //     const distanceFromRight = window.innerWidth - event.clientX;
        //     this.__hidden(distanceFromRight > 120);
        // }
        // // ...existing code...
        //endregion
    }

    /**
     * Manipula o movimento do mouse para mostrar ou Ocultar minimap.
     * @param {MouseEvent} event - O evento de movimento do mouse.
     */
    __onMouseMove(event) {
        if ( this.minimapHiddenByUser ) return;
        const distanceFromRight = window.innerWidth - event.clientX;
        this.__hidden( distanceFromRight > 120 );
    }

    /**
     * Alterna a visibilidade do minimap.
     */
    __toggleMinimapVisibility() {
        this.__hidden( !this.minimapIsHidden );
    }

    /**
     * Oculta ou mostra o minimap.
     * @param {boolean} hidden - Se verdadeiro, oculta o minimap; caso contrário, mostra.
     */
    __hidden(hidden) {
        this.minimapIsHidden = hidden;
        this.minimap.classList.toggle('hidden', hidden);
        if ( hidden ) {
            this.spanHideBtn.innerHTML = Minimap.eyeOpen;
            this.tooltip.textContent = 'Mostrar minimap';
        } else {
            this.spanHideBtn.innerHTML = Minimap.close;
            this.tooltip.textContent = 'Ocultar minimap';
        }
    }
}

new Minimap();
