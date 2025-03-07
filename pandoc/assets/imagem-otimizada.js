if (navigator.connection) { // Verifica se o navegador suporta a API de conexão
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection; // Pega a conexão do navegador
    const effectiveType = connection.effectiveType; // Pega o tipo de conexão
    let imageQuality; 
    switch (effectiveType) {
        case '2g': // 3G no chrome
            imageQuality = '-50%';
            break;
        case '3g': // Slow 4G no chrome
            imageQuality = '-75%';
            break;
        default:
            imageQuality = '';
            break;
    }
    document.querySelectorAll('img').forEach(img => { // Percorre todos os img da página
        let ext = img.src.split('.').pop(); // Pega a extensão da imagem
        let filename = img.src.split('/').pop().replace(`.${ext}`, ''); // Pega o nome da imagem sem a extensão
        img.src = img.src.replace(`${filename}`, `${filename}${imageQuality}`); // Substitui o nome da imagem pelo nome da imagem com a qualidade
    });
}